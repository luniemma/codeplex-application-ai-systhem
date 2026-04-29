"""
Codeplex AI - Main Application Entry Point
"""
import logging
import os
import time
import uuid

from dotenv import load_dotenv
from flask import Flask, g, request
from flask_cors import CORS

load_dotenv()

from app.logging_setup import setup_logging  # noqa: E402 — must run after load_dotenv

logger = setup_logging()


def _is_key_set(value: str) -> bool:
    return bool(value) and not value.startswith("your_")


def _log_startup_banner() -> None:
    """Emit a one-time summary of effective config so an operator can see at
    a glance which providers, cache, and DB are wired in."""
    from app.cache import cache_client
    from app.config import config

    providers = {
        "openai": _is_key_set(config.OPENAI_API_KEY),
        "anthropic": _is_key_set(config.ANTHROPIC_API_KEY),
        "google": _is_key_set(config.GOOGLE_API_KEY),
    }
    enabled = [p for p, ok in providers.items() if ok]
    disabled = [p for p, ok in providers.items() if not ok]

    redis_state = "connected" if cache_client.redis_client else "not reachable (in-memory fallback)"

    logger.info("=" * 60)
    logger.info("Codeplex AI starting")
    logger.info("  environment   = %s", config.ENVIRONMENT)
    logger.info("  debug         = %s", config.DEBUG)
    logger.info("  bind          = %s:%s", config.API_HOST, config.API_PORT)
    logger.info("  log_level     = %s", config.LOG_LEVEL)
    logger.info("  log_format    = %s", os.getenv("LOG_FORMAT", "text"))
    logger.info("  providers     = enabled=%s, disabled=%s",
                enabled or "(none — all keys are placeholders)", disabled)
    logger.info("  cache (redis) = %s", redis_state)
    logger.info("  caching flag  = %s", config.ENABLE_CACHING)
    logger.info("  database_url  = %s", _redact_url(config.DATABASE_URL))
    logger.info("=" * 60)


def _redact_url(url: str) -> str:
    """Strip user:pass from a URL before logging it."""
    if "@" not in url:
        return url
    scheme, rest = url.split("://", 1) if "://" in url else ("", url)
    _, host_part = rest.rsplit("@", 1)
    return f"{scheme}://***:***@{host_part}" if scheme else f"***:***@{host_part}"


def _install_request_logging(app: Flask) -> None:
    """Attach request lifecycle hooks for visibility:
    - generate a short request_id, expose it on flask.g and X-Request-ID header
    - log a summary line on each completed request with method, path, status, duration
    """
    access_logger = logging.getLogger("app.access")

    @app.before_request
    def _before_request():
        g.request_id = uuid.uuid4().hex[:12]
        g.request_start = time.perf_counter()

    @app.after_request
    def _after_request(response):
        elapsed_ms = int((time.perf_counter() - getattr(g, "request_start", time.perf_counter())) * 1000)
        # Expose the request id so client can reference it in bug reports.
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-")

        # Skip access logs for /health under INFO so health probes don't drown
        # out real traffic; still log them at DEBUG, and always log non-200s.
        is_health_probe = request.path == "/health" and response.status_code == 200
        level = logging.DEBUG if is_health_probe else logging.INFO

        access_logger.log(
            level,
            "%s %s %d (%dms, %sB)",
            request.method,
            request.full_path.rstrip("?") or request.path,
            response.status_code,
            elapsed_ms,
            response.calculate_content_length() or "-",
        )
        return response

    # Unhandled exceptions: Flask's `got_request_exception` signal lets us
    # log without intercepting the response. Skip HTTPException (404, 400,
    # etc.) — those are part of the normal flow, not "unhandled".
    from flask.signals import got_request_exception
    from werkzeug.exceptions import HTTPException

    def _on_unhandled(sender, exception, **_):
        if isinstance(exception, HTTPException):
            return
        access_logger.exception(
            "unhandled exception during %s %s", request.method, request.path,
        )

    got_request_exception.connect(_on_unhandled, app)


def _resolve_cors_origins() -> list[str]:
    """CORS_ORIGINS defaults to '*' (open) only in development; in
    production we require explicit origins so an unconfigured deploy
    can't accidentally expose itself to every site on the web."""
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    if os.getenv("ENVIRONMENT", "production").lower() == "development":
        return ["*"]
    # Production with no explicit origins — same-origin only (empty list
    # disables cross-origin sharing). Operators must opt in to wildcards.
    logger.warning(
        "CORS_ORIGINS is empty in production — refusing all cross-origin requests. "
        "Set CORS_ORIGINS=https://your-frontend.example.com,... to allow specific origins."
    )
    return []


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app.config.update(
        DEBUG=os.getenv("DEBUG", "False").lower() == "true",
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_REQUEST_SIZE", 10485760)),
    )

    CORS(app, resources={
        r"/api/*": {
            "origins": _resolve_cors_origins(),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"],
            "expose_headers": ["X-Request-ID"],
        }
    })

    _install_request_logging(app)

    # Production security hardening — headers + rate limits.
    from app.security import install_rate_limiter, install_security_headers
    install_security_headers(app)
    limiter = install_rate_limiter(app, redis_url=os.getenv("REDIS_URL"))
    app.extensions["limiter"] = limiter  # exposed for per-route limits in routes.py

    from app.routes import api_bp, health_bp
    from app.web import web_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(web_bp)

    # Per-blueprint rate limits — tighter than the global default for the
    # AI endpoints since each call costs real money. Applied after the
    # blueprint is registered, before the app starts handling requests.
    limiter.limit("30 per minute")(api_bp)

    logger.info("Flask app created in %s mode", os.getenv("ENVIRONMENT", "production"))

    return app


# Emit startup banner once at import time. Gunicorn imports this module in
# every worker, so each worker logs its own banner — useful for diagnosing
# worker-specific config drift, and harmless under low worker counts.
_log_startup_banner()


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        debug=os.getenv("DEBUG", "False").lower() == "true",
    )
