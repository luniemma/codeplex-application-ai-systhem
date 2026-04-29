"""
Production security hardening: HTTP response headers + rate limiting.

Headers protect against common browser-side attacks (XSS, clickjacking, MIME
sniffing, mixed content). HSTS only kicks in when the request was served
over HTTPS — in dev (HTTP), we skip it so the browser doesn't refuse to
talk to localhost on the next refresh.

Rate limiting uses Flask-Limiter with two backends:
- Redis when REDIS_URL is reachable (shared limits across workers)
- in-memory otherwise (per-worker; fine for dev and single-worker prod)
"""
from __future__ import annotations

import logging

from flask import Flask, Response, request

logger = logging.getLogger(__name__)


def _build_csp(playground_enabled: bool) -> str:
    """The playground at `/` loads marked.js from jsdelivr; allow that origin
    explicitly rather than `unsafe-inline` everywhere."""
    directives = [
        "default-src 'self'",
        # Inline styles are needed for the playground's <style> block.
        "style-src 'self' 'unsafe-inline'",
        # Inline script for the playground's tab/fetch logic.
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        "img-src 'self' data:",
        "connect-src 'self'",
        "font-src 'self' data:",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
    if not playground_enabled:
        directives = [d for d in directives if "jsdelivr" not in d and "unsafe-inline" not in d]
    return "; ".join(directives)


def install_security_headers(app: Flask) -> None:
    """Add a small middleware that attaches hardening headers to every response."""
    csp = _build_csp(playground_enabled=True)

    @app.after_request
    def _add_headers(response: Response) -> Response:
        # Browser-side protections — cheap, broadly compatible.
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        response.headers.setdefault("Content-Security-Policy", csp)
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")

        # HSTS only over HTTPS. Setting it on plain HTTP is an anti-pattern
        # because some browsers will pin the policy and refuse to fall back.
        if request.is_secure or request.headers.get("X-Forwarded-Proto") == "https":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )

        return response


def install_rate_limiter(app: Flask, redis_url: str | None = None):
    """Configure Flask-Limiter with Redis when reachable, in-memory otherwise.

    Returns the Limiter instance so callers (routes) can apply per-route
    overrides via @limiter.limit("...").
    """
    # Lazy import so requirements stay optional for tests that don't need it.
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    # Resolve storage backend at startup. The probe uses a tight 200ms
    # timeout so a Redis-down environment doesn't add seconds to every
    # gunicorn worker boot or pytest run.
    storage_uri = "memory://"
    backend = "in-memory"
    if redis_url:
        try:
            import redis  # type: ignore

            client = redis.from_url(redis_url, socket_connect_timeout=0.2, socket_timeout=0.2)
            client.ping()
            storage_uri = redis_url
            backend = "redis"
        except Exception as exc:
            logger.warning(
                "rate_limiter: Redis unreachable (%s) — falling back to in-memory storage. "
                "Limits will not be shared across workers.",
                exc,
            )

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        # Sane defaults; per-route limits override these via @limiter.limit().
        default_limits=["200 per minute", "2000 per hour"],
        storage_uri=storage_uri,
        # /health and /livez/readyz must not be rate limited or k8s probes will fail.
        default_limits_exempt_when=lambda: request.path in {"/health", "/livez", "/readyz"},
        headers_enabled=True,  # emit X-RateLimit-* headers
    )
    logger.info("rate_limiter: storage=%s default=200/min,2000/hour", backend)
    return limiter
