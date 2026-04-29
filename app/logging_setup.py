"""
Centralized logging configuration.

Two output formats, picked via LOG_FORMAT env var:
- "text" (default) — human-readable, includes request_id when available.
- "json"           — one JSON object per line, suitable for log aggregators
                     (Datadog, Loki, Cloudwatch, etc.).

A `RequestIdFilter` injects `request_id` (and `provider` when set) onto every
log record from `flask.g`, so handlers and downstream calls don't need to
thread the ID through manually.
"""
import json
import logging
import os
import sys
import time
from typing import ClassVar

try:
    from flask import g, has_request_context
except ImportError:  # pragma: no cover — flask is a hard dep, but keep import safe
    g = None  # type: ignore

    def has_request_context() -> bool:  # type: ignore[no-redef]
        return False


def _get_request_id() -> str | None:
    if has_request_context():
        return getattr(g, "request_id", None)
    return None


def _get_provider() -> str | None:
    if has_request_context():
        return getattr(g, "ai_provider", None)
    return None


class RequestIdFilter(logging.Filter):
    """Attach Flask request context fields onto every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _get_request_id() or "-"
        record.ai_provider = _get_provider() or "-"
        return True


class TextFormatter(logging.Formatter):
    """Human-readable single-line format with optional request_id."""

    DEFAULT_FORMAT = (
        "%(asctime)s %(levelname)-5s %(name)s "
        "[req=%(request_id)s] %(message)s"
    )

    def __init__(self) -> None:
        super().__init__(fmt=self.DEFAULT_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


class JsonFormatter(logging.Formatter):
    """One JSON object per line — for log aggregators."""

    # Standard LogRecord attributes we don't want to copy verbatim.
    _RESERVED: ClassVar[set[str]] = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "asctime",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)
            ) + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = getattr(record, "request_id", None)
        if rid and rid != "-":
            payload["request_id"] = rid
        provider = getattr(record, "ai_provider", None)
        if provider and provider != "-":
            payload["ai_provider"] = provider
        # Pick up any custom extras passed via logger.info(..., extra={...})
        for key, value in record.__dict__.items():
            if key in self._RESERVED or key.startswith("_") or key in payload:
                continue
            try:
                json.dumps(value)
            except (TypeError, ValueError):
                value = repr(value)
            payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging() -> logging.Logger:
    """
    Configure the root logger and return the app logger.

    Idempotent — safe to call multiple times (e.g. from create_app() in tests).
    Honors LOG_LEVEL and LOG_FORMAT env vars.
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("LOG_FORMAT", "text").lower()

    formatter = JsonFormatter() if fmt == "json" else TextFormatter()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    # Replace any handlers a previous setup_logging() (or basicConfig) installed,
    # so test re-runs and dev-mode reloads don't double-log.
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Werkzeug's dev-server access log is too verbose at INFO and we already
    # log requests ourselves via after_request. Keep it at WARNING so we still
    # see real errors from it.
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    return logging.getLogger("app")
