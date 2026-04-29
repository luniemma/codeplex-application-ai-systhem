"""
Caching Module - Redis-based caching
"""

import json
import logging
from functools import wraps
from typing import Any

import redis

from app.config import config

logger = logging.getLogger(__name__)


class CacheClient:
    """Redis cache client"""

    def __init__(self, redis_url: str = config.REDIS_URL):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e!s}")
            self.redis_client = None

    def get(self, key: str) -> Any | None:
        """Get value from cache"""
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e!s}")
            return None

    def set(self, key: str, value: Any, ttl: int = config.CACHE_TTL) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e!s}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e!s}")
            return False

    def clear(self) -> bool:
        """Clear all cache"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e!s}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis_client:
            return False

        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e!s}")
            return False


# Global cache client
cache_client = CacheClient()


def cache_result(ttl: int = config.CACHE_TTL, key_prefix: str | None = None):
    """Cache decorator"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not config.ENABLE_CACHING:
                return f(*args, **kwargs)

            # Generate cache key
            prefix = key_prefix or f.__name__
            key = f"{prefix}:{args}:{kwargs}"

            # Try to get from cache
            cached_value = cache_client.get(key)
            if cached_value is not None:
                # Hits are common — keep at DEBUG to avoid swamping logs.
                logger.debug("cache hit prefix=%s", prefix)
                return cached_value

            # Cache miss → INFO so you can correlate "this request actually
            # talked to the upstream provider" without flipping log levels.
            logger.info("cache miss prefix=%s — calling upstream", prefix)
            result = f(*args, **kwargs)
            cache_client.set(key, result, ttl)
            return result

        return decorated_function

    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache by pattern"""
    if not cache_client.redis_client:
        return

    try:
        keys = cache_client.redis_client.keys(pattern)
        for key in keys:
            cache_client.delete(key)
        logger.info(f"Invalidated {len(keys)} cache keys")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e!s}")


class InMemoryCache:
    """In-memory cache fallback"""

    def __init__(self, max_size: int = config.CACHE_MAX_SIZE):
        self.cache = {}
        self.max_size = max_size

    def get(self, key: str) -> Any | None:
        """Get value from cache"""
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> bool:
        """Set value in cache"""
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            self.cache.pop(next(iter(self.cache)))

        self.cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> bool:
        """Clear all cache"""
        self.cache.clear()
        return True
