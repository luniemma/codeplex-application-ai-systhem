"""
AI Services Module - Integration with multiple AI providers
"""

import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import Any, ClassVar

try:
    from flask import g, has_request_context
except ImportError:  # pragma: no cover
    g = None  # type: ignore

    def has_request_context() -> bool:  # type: ignore[no-redef]
        return False


from app.cache import cache_result
from app.config import config
from app.retry import with_retry

logger = logging.getLogger(__name__)


def _timed_call(provider: str, op: str, fn: Callable):
    """Run `fn` (wrapped in retry-on-transient-error) and emit a single
    structured log line covering provider, op, status, and duration. Tags
    flask.g with the provider so all downstream logs in the same request
    can be filtered by provider.

    Permanent errors (auth, missing key, invalid model) propagate on the
    first attempt; transient errors (timeouts, 5xx, 429) get up to 3
    attempts with exponential backoff before failing.
    """
    if has_request_context():
        g.ai_provider = provider

    retried_fn = with_retry()(fn)

    started = time.perf_counter()
    try:
        result = retried_fn()
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "provider_call provider=%s op=%s status=ok duration_ms=%d",
            provider,
            op,
            elapsed_ms,
            extra={"provider": provider, "op": op, "duration_ms": elapsed_ms, "status": "ok"},
        )
        return result
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.warning(
            "provider_call provider=%s op=%s status=error duration_ms=%d error=%s",
            provider,
            op,
            elapsed_ms,
            exc,
            extra={"provider": provider, "op": op, "duration_ms": elapsed_ms, "status": "error"},
        )
        raise


def _is_key_configured(key: str) -> bool:
    """A key counts as configured only if it's set and not a `your_*` placeholder."""
    return bool(key) and not key.startswith("your_")


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def analyze_code(self, code: str) -> dict[str, Any]:
        """Analyze code and return results"""
        pass

    @abstractmethod
    def generate_code(self, prompt: str) -> str:
        """Generate code based on prompt"""
        pass

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        """Chat with AI model"""
        pass

    def chat_stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """Stream chat tokens. Default falls back to a one-shot chat() so
        providers that don't override streaming still work — they just
        deliver everything in one chunk."""
        yield self.chat(messages)


class OpenAIProvider(AIProvider):
    """OpenAI API Provider"""

    def __init__(self):
        if not _is_key_configured(config.OPENAI_API_KEY):
            raise ValueError(
                "OPENAI_API_KEY is not configured. Set a real key in .env (not the 'your_openai_key_here' placeholder) and restart the server."
            )
        try:
            import openai

            openai.api_key = config.OPENAI_API_KEY
            self.client = openai
        except ImportError:
            logger.error("OpenAI package not installed")
            raise

    def analyze_code(self, code: str) -> dict[str, Any]:
        """Analyze code using OpenAI"""
        try:
            response = self.client.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code analyzer. Analyze the provided code and give detailed feedback.",
                    },
                    {"role": "user", "content": f"Analyze this code:\n\n{code}"},
                ],
                temperature=config.OPENAI_TEMPERATURE,
            )
            return {
                "provider": "openai",
                "analysis": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
            }
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e!s}")
            raise

    def generate_code(self, prompt: str) -> str:
        """Generate code using OpenAI"""
        try:
            response = self.client.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code generator. Generate clean, well-documented code.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=config.OPENAI_TEMPERATURE,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e!s}")
            raise

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Chat with OpenAI"""
        try:
            response = self.client.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=config.OPENAI_TEMPERATURE,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat error: {e!s}")
            raise

    def chat_stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """Stream chat tokens from OpenAI (`stream=True`)."""
        try:
            stream = self.client.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=config.OPENAI_TEMPERATURE,
                stream=True,
            )
            for chunk in stream:
                # Older openai==0.27.x SDK exposes delta as a dict-like.
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None) or (
                    delta.get("content") if isinstance(delta, dict) else None
                )
                if content:
                    yield content
        except Exception as e:
            logger.error(f"OpenAI chat_stream error: {e!s}")
            raise


class AnthropicProvider(AIProvider):
    """Anthropic Claude Provider"""

    def __init__(self):
        if not _is_key_configured(config.ANTHROPIC_API_KEY):
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured. Set a real key in .env (not the 'your_anthropic_key_here' placeholder) and restart the server."
            )
        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        except ImportError:
            logger.error("Anthropic package not installed")
            raise

    def analyze_code(self, code: str) -> dict[str, Any]:
        """Analyze code using Claude"""
        try:
            response = self.client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": f"Analyze this code:\n\n{code}"}],
            )
            return {
                "provider": "anthropic",
                "analysis": response.content[0].text,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            }
        except Exception as e:
            logger.error(f"Anthropic analysis error: {e!s}")
            raise

    def generate_code(self, prompt: str) -> str:
        """Generate code using Claude"""
        try:
            response = self.client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation error: {e!s}")
            raise

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Chat with Claude"""
        try:
            response = self.client.messages.create(
                model=config.ANTHROPIC_MODEL, max_tokens=2048, messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic chat error: {e!s}")
            raise

    def chat_stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """Stream chat tokens from Claude via the SDK's text_stream context."""
        try:
            with self.client.messages.stream(
                model=config.ANTHROPIC_MODEL, max_tokens=2048, messages=messages
            ) as stream:
                for text in stream.text_stream:
                    if text:
                        yield text
        except Exception as e:
            logger.error(f"Anthropic chat_stream error: {e!s}")
            raise


class GoogleProvider(AIProvider):
    """Google Generative AI Provider"""

    def __init__(self):
        if not _is_key_configured(config.GOOGLE_API_KEY):
            raise ValueError(
                "GOOGLE_API_KEY is not configured. Set a real key in .env (not the 'your_google_key_here' placeholder) and restart the server."
            )
        try:
            import google.generativeai as genai

            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.client = genai
        except ImportError:
            logger.error("Google generativeai package not installed")
            raise

    def analyze_code(self, code: str) -> dict[str, Any]:
        """Analyze code using Google"""
        try:
            model = self.client.GenerativeModel(config.GOOGLE_MODEL)
            response = model.generate_content(
                f"Analyze this code:\n\n{code}",
                generation_config=self.client.types.GenerationConfig(temperature=0.7),
            )
            return {
                "provider": "google",
                "analysis": response.text,
                "tokens_used": 0,  # Google API doesn't provide token count in same way
            }
        except Exception as e:
            logger.error(f"Google analysis error: {e!s}")
            raise

    def generate_code(self, prompt: str) -> str:
        """Generate code using Google"""
        try:
            model = self.client.GenerativeModel(config.GOOGLE_MODEL)
            response = model.generate_content(
                prompt, generation_config=self.client.types.GenerationConfig(temperature=0.7)
            )
            return response.text
        except Exception as e:
            logger.error(f"Google generation error: {e!s}")
            raise

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Chat with Google"""
        try:
            model = self.client.GenerativeModel(config.GOOGLE_MODEL)
            chat = model.start_chat()

            for msg in messages[:-1]:
                chat.send_message(msg.get("content", ""), stream=False)

            response = chat.send_message(messages[-1].get("content", ""), stream=False)
            return response.text
        except Exception as e:
            logger.error(f"Google chat error: {e!s}")
            raise

    def chat_stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """Stream chat tokens from Google's generative API (stream=True)."""
        try:
            model = self.client.GenerativeModel(config.GOOGLE_MODEL)
            chat = model.start_chat()
            # Replay history (non-streamed) so the stream-target message has
            # the right context. Cheaper than running a full chain through
            # generate_content() each time.
            for msg in messages[:-1]:
                chat.send_message(msg.get("content", ""), stream=False)
            response = chat.send_message(messages[-1].get("content", ""), stream=True)
            for chunk in response:
                text = getattr(chunk, "text", None)
                if text:
                    yield text
        except Exception as e:
            logger.error(f"Google chat_stream error: {e!s}")
            raise


class AIServiceFactory:
    """Factory for creating AI service providers"""

    _providers: ClassVar[dict[str, type[AIProvider]]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
    }

    @staticmethod
    def create_provider(provider_name: str = "openai") -> AIProvider:
        """Create and return an AI provider instance"""
        try:
            provider_class = AIServiceFactory._providers.get(provider_name.lower())
            if not provider_class:
                raise ValueError(f"Unknown provider: {provider_name}")
            return provider_class()
        except Exception as e:
            logger.error(f"Failed to create provider {provider_name}: {e!s}")
            raise

    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available providers"""
        return list(AIServiceFactory._providers.keys())


# Helper functions — wrapped with @cache_result so identical (input, provider)
# pairs are memoized. No-ops gracefully if Redis is unreachable or
# ENABLE_CACHING is False. Each upstream call is wrapped in _timed_call so
# we get a single log line per real provider invocation (cache hits skip it).
@cache_result(key_prefix="analyze_code")
def analyze_code(code: str, provider: str = "openai") -> dict[str, Any]:
    """Analyze code with specified provider"""
    ai_provider = AIServiceFactory.create_provider(provider)
    return _timed_call(provider, "analyze_code", lambda: ai_provider.analyze_code(code))


@cache_result(key_prefix="generate_code")
def generate_code(prompt: str, provider: str = "openai") -> str:
    """Generate code with specified provider"""
    ai_provider = AIServiceFactory.create_provider(provider)
    return _timed_call(provider, "generate_code", lambda: ai_provider.generate_code(prompt))


@cache_result(key_prefix="chat")
def chat(messages: list[dict[str, str]], provider: str = "openai") -> str:
    """Chat with AI with specified provider"""
    ai_provider = AIServiceFactory.create_provider(provider)
    return _timed_call(provider, "chat", lambda: ai_provider.chat(messages))


def chat_stream(messages: list[dict[str, str]], provider: str = "openai") -> Iterator[str]:
    """Stream chat tokens for the given provider. Not cached — streaming
    responses are stateful per request. Provider creation can still raise
    `ValueError` for missing keys; surface that to the caller so the route
    handler can emit a sensible error event."""
    if has_request_context():
        g.ai_provider = provider
    ai_provider = AIServiceFactory.create_provider(provider)
    started = time.perf_counter()
    chunks = 0
    try:
        for chunk in ai_provider.chat_stream(messages):
            chunks += 1
            yield chunk
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "provider_call provider=%s op=chat_stream status=ok duration_ms=%d chunks=%d",
            provider,
            "chat_stream",
            elapsed_ms,
            extra={
                "provider": provider,
                "op": "chat_stream",
                "duration_ms": elapsed_ms,
                "status": "ok",
                "chunks": chunks,
            },
        )
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.warning(
            "provider_call provider=%s op=chat_stream status=error duration_ms=%d error=%s",
            provider,
            elapsed_ms,
            exc,
            extra={
                "provider": provider,
                "op": "chat_stream",
                "duration_ms": elapsed_ms,
                "status": "error",
            },
        )
        raise
