"""Redis caching service for YouTube API responses."""

import hashlib
import inspect
import json
from functools import wraps
from typing import Any, Callable, Optional

import redis
import structlog

from ..config import get_settings

logger = structlog.get_logger(__name__)


class RedisCache:
    """Redis-based caching layer for YouTube API responses."""

    def __init__(self, redis_url: Optional[str] = None, cache_ttl: int = 3600):
        """
        Initialize Redis connection.

        Args:
            redis_url: Redis connection URL (defaults to settings)
            cache_ttl: Cache TTL in seconds (defaults to settings)
        """
        settings = get_settings()
        self.redis_url = redis_url or settings.redis_url
        self.cache_ttl = cache_ttl or settings.cache_ttl_seconds
        self.enabled = bool(self.redis_url)
        self.client: Optional[redis.Redis] = None

        if self.enabled:
            try:
                self.client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30,
                )
                # Test connection
                self.client.ping()
                logger.info(
                    "redis_connected",
                    ttl_seconds=self.cache_ttl,
                )
            except Exception as e:
                logger.warning("redis_connection_failed", error=str(e))
                self.enabled = False
                self.client = None
        else:
            logger.info("redis_disabled", reason="REDIS_URL not set")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"youtube_api:{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                logger.debug("cache_hit", key=key)
                return json.loads(value)
            logger.debug("cache_miss", key=key)
            return None
        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with TTL."""
        if not self.enabled or not self.client:
            return False

        try:
            ttl = ttl or self.cache_ttl
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            logger.debug("cache_set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(key)
            logger.debug("cache_delete", key=key)
            return True
        except Exception as e:
            logger.error("cache_delete_error", key=key, error=str(e))
            return False

    def clear_all(self) -> bool:
        """Clear all cache entries with our prefix."""
        if not self.enabled or not self.client:
            return False

        try:
            pattern = "youtube_api:*"
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.info("cache_cleared", keys_deleted=len(keys))
            return True
        except Exception as e:
            logger.error("cache_clear_error", error=str(e))
            return False

    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.enabled or not self.client:
            return {"enabled": False, "status": "disabled"}

        try:
            info = self.client.info("stats")
            pattern = "youtube_api:*"
            key_count = len(self.client.keys(pattern))

            return {
                "enabled": True,
                "status": "connected",
                "total_keys": key_count,
                "ttl_seconds": self.cache_ttl,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {"enabled": True, "status": "error", "error": str(e)}


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results in Redis.

    Args:
        prefix: Cache key prefix (e.g., 'video_data', 'captions')
        ttl: Time to live in seconds (defaults to CACHE_TTL_SECONDS)

    Example:
        @cached(prefix='video_data', ttl=3600)
        def get_video_data(url: str) -> dict:
            return data
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache()
            cache_key = cache._generate_key(prefix, *args, **kwargs)

            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache()
            cache_key = cache._generate_key(prefix, *args, **kwargs)

            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
