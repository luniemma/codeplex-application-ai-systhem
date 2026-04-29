"""
API Routes Module - REST endpoints for Codeplex AI
"""

import json
import logging

from flask import Blueprint, Response, request, stream_with_context

from app.ai_services import AIServiceFactory, analyze_code, chat_stream, generate_code
from app.ai_services import chat as ai_chat
from app.config import config
from app.utils import create_response

logger = logging.getLogger(__name__)

# Create blueprints
api_bp = Blueprint("api", __name__, url_prefix="/api")
health_bp = Blueprint("health", __name__)


def _provider_has_real_key(name: str) -> bool:
    key_attr = f"{name.upper()}_API_KEY"
    value = getattr(config, key_attr, "")
    return bool(value) and not value.startswith("your_")


# ─── Health endpoints ──────────────────────────────────────────────────────
# /livez — kubelet "liveness" probe. Process alive? Nothing else.
# /readyz — kubelet "readiness" probe. Are we wired up enough to serve real
#           traffic (i.e. at least one provider key configured)?
# /health — legacy alias for /livez, kept so existing clients (the smoke
#           test, Docker HEALTHCHECK) don't break.


@health_bp.route("/livez", methods=["GET"])
@health_bp.route("/health", methods=["GET"])
def liveness():
    """Process liveness — returns 200 as long as the WSGI app is responding.
    Used by Kubernetes' livenessProbe; failure here triggers a pod restart."""
    return create_response(
        {
            "status": "healthy",
            "service": "codeplex-ai",
            "version": "1.0.0",
        },
        200,
    )


@health_bp.route("/readyz", methods=["GET"])
def readiness():
    """Readiness probe — returns 503 unless we can plausibly serve a real
    request. Used by Kubernetes' readinessProbe; failure here removes the
    pod from the service load balancer without restarting it."""
    providers = {p: _provider_has_real_key(p) for p in ("openai", "anthropic", "google")}
    any_ready = any(providers.values())
    body = {
        "status": "ready" if any_ready else "not_ready",
        "providers": providers,
    }
    return create_response(body, 200 if any_ready else 503)


@api_bp.route("/models", methods=["GET"])
def list_models():
    """List available AI models"""
    try:
        providers = AIServiceFactory.get_available_providers()
        return create_response({"providers": providers, "count": len(providers)}, 200)
    except Exception as e:
        logger.error(f"Failed to list models: {e!s}")
        return create_response({"error": str(e)}, 500)


@api_bp.route("/analyze", methods=["POST"])
def analyze():
    """Analyze code endpoint"""
    try:
        # silent=True returns None on malformed JSON (instead of raising 400),
        # so we can return our own envelope-shaped error.
        data = request.get_json(silent=True) or {}
        if "code" not in data:
            return create_response({"error": "Code is required"}, 400)

        code = data.get("code")
        provider = data.get("provider", "openai")

        if not code:
            return create_response({"error": "Code cannot be empty"}, 400)

        # Analyze code
        result = analyze_code(code, provider)
        return create_response(result, 200)

    except ValueError as e:
        logger.warning(f"Validation error in analyze: {e!s}")
        return create_response({"error": str(e)}, 400)
    except Exception as e:
        logger.error(f"Analysis error: {e!s}")
        return create_response({"error": f"Analysis failed: {e}"}, 500)


@api_bp.route("/generate", methods=["POST"])
def generate():
    """Generate code endpoint"""
    try:
        data = request.get_json(silent=True) or {}
        if "prompt" not in data:
            return create_response({"error": "Prompt is required"}, 400)

        prompt = data.get("prompt")
        provider = data.get("provider", "openai")

        if not prompt:
            return create_response({"error": "Prompt cannot be empty"}, 400)

        # Generate code
        generated_code = generate_code(prompt, provider)
        return create_response(
            {"provider": provider, "prompt": prompt, "generated_code": generated_code}, 200
        )

    except ValueError as e:
        logger.warning(f"Validation error in generate: {e!s}")
        return create_response({"error": str(e)}, 400)
    except Exception as e:
        logger.error(f"Generation error: {e!s}")
        return create_response({"error": f"Code generation failed: {e}"}, 500)


@api_bp.route("/optimize", methods=["POST"])
def optimize():
    """Optimize code endpoint"""
    try:
        data = request.get_json(silent=True) or {}
        if "code" not in data:
            return create_response({"error": "Code is required"}, 400)

        code = data.get("code")
        provider = data.get("provider", "openai")

        if not code:
            return create_response({"error": "Code cannot be empty"}, 400)

        # Create optimization prompt
        prompt = f"""Analyze and optimize the following code for performance, readability, and best practices:

{code}

Provide:
1. Identified issues
2. Optimized version of the code
3. Explanation of changes
4. Performance improvements"""

        optimized = generate_code(prompt, provider)

        return create_response(
            {"provider": provider, "original_code": code, "optimized_code": optimized}, 200
        )

    except ValueError as e:
        logger.warning(f"Validation error in optimize: {e!s}")
        return create_response({"error": str(e)}, 400)
    except Exception as e:
        logger.error(f"Optimization error: {e!s}")
        return create_response({"error": f"Code optimization failed: {e}"}, 500)


@api_bp.route("/chat/stream", methods=["POST"])
def chat_stream_route():
    """Streaming chat endpoint — Server-Sent Events.

    Each event is a `data: <json>` line where the JSON has either a `chunk`
    (text token) or an `error` (string). The stream terminates with
    `data: [DONE]`. Client side: parse with `fetch + ReadableStream` rather
    than `EventSource` (which only supports GET).
    """
    data = request.get_json(silent=True) or {}
    if "messages" not in data:
        return create_response({"error": "Messages are required"}, 400)
    messages = data.get("messages") or []
    provider = data.get("provider", "openai")
    if not messages or not isinstance(messages, list):
        return create_response({"error": "Messages must be a non-empty list"}, 400)

    def _events():
        try:
            for chunk in chat_stream(messages, provider):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except ValueError as exc:
            # Missing key / unknown provider — surface as a typed error event.
            logger.warning(f"chat_stream validation: {exc!s}")
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        except Exception as exc:
            logger.error(f"chat_stream upstream error: {exc!s}")
            yield f"data: {json.dumps({'error': f'Chat stream failed: {exc}'})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(_events()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # tell nginx not to buffer SSE
            "Connection": "keep-alive",
        },
    )


@api_bp.route("/chat", methods=["POST"])
def chat():
    """Chat with AI endpoint"""
    try:
        data = request.get_json(silent=True) or {}
        if "messages" not in data:
            return create_response({"error": "Messages are required"}, 400)

        messages = data.get("messages", [])
        provider = data.get("provider", "openai")

        if not messages or not isinstance(messages, list):
            return create_response({"error": "Messages must be a non-empty list"}, 400)

        # Chat with AI
        response = ai_chat(messages, provider)

        return create_response(
            {"provider": provider, "messages": messages, "response": response}, 200
        )

    except ValueError as e:
        logger.warning(f"Validation error in chat: {e!s}")
        return create_response({"error": str(e)}, 400)
    except Exception as e:
        logger.error(f"Chat error: {e!s}")
        return create_response({"error": f"Chat failed: {e}"}, 500)


@api_bp.route("/batch-analyze", methods=["POST"])
def batch_analyze():
    """Batch analyze multiple code snippets"""
    try:
        data = request.get_json(silent=True) or {}
        if "codes" not in data:
            return create_response({"error": "Codes array is required"}, 400)

        codes = data.get("codes", [])
        provider = data.get("provider", "openai")

        if not codes or not isinstance(codes, list):
            return create_response({"error": "Codes must be a non-empty list"}, 400)

        results = []
        for idx, code in enumerate(codes):
            try:
                result = analyze_code(code, provider)
                results.append({"index": idx, "status": "success", "data": result})
            except Exception as e:
                results.append({"index": idx, "status": "error", "error": str(e)})

        return create_response({"provider": provider, "total": len(codes), "results": results}, 200)

    except Exception as e:
        logger.error(f"Batch analysis error: {e!s}")
        return create_response({"error": f"Batch analysis failed: {e}"}, 500)


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_response({"error": "Endpoint not found"}, 404)


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error!s}")
    return create_response({"error": "Internal server error"}, 500)
