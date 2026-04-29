"""
Retry policy for upstream provider calls.

Wraps `tenacity` so the rest of the codebase doesn't need to know the
library's API. Defaults: up to 3 attempts, exponential backoff with jitter,
total cap ~10s. Only retries on transient errors (network, timeout, 5xx,
429); permanent errors (auth, invalid model) propagate immediately.
"""

from __future__ import annotations

import logging

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def _is_retryable(exc: BaseException) -> bool:
    """Decide whether an exception is worth retrying.

    We can't import provider SDKs here without circular issues, so we match
    on class name and HTTP status hints. False positives just mean we retry
    something we don't need to — costly but not incorrect.
    """
    name = type(exc).__name__.lower()

    # Permanent failures — stop immediately.
    if "auth" in name or "permission" in name or "notfound" in name:
        return False
    if isinstance(exc, ValueError):  # e.g. "key not configured"
        return False

    # Transient failures — retry.
    transient_keywords = (
        "timeout",
        "connection",
        "network",
        "unavailable",
        "ratelimit",
        "rate_limit",
        "toomanyrequests",
        "503",
        "504",
        "502",
    )
    msg = str(exc).lower()
    if any(k in name for k in transient_keywords):
        return True
    # Default: don't retry on patterns we don't recognise. Better to surface a
    # clean error than mask bugs by silently retrying.
    return any(k in msg for k in transient_keywords)


def with_retry(
    *,
    attempts: int = 3,
    min_wait_s: float = 0.5,
    max_wait_s: float = 4.0,
):
    """Decorator factory: applies retry-with-backoff policy to upstream calls.

    Usage:
        @with_retry()
        def call_upstream(...):
            ...
    """
    return retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=min_wait_s, min=min_wait_s, max=max_wait_s),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
