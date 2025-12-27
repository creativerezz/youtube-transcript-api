import os
import json
import hashlib
from typing import Optional, Any, Callable
from datetime import datetime
import redis
from functools import wraps

class RedisCache:
    """Redis-based caching layer for YouTube API responses."""

    def __init__(self):
        """Initialize Redis connection from environment variables."""
        self.redis_url = os.getenv("REDIS_URL")
        self.cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", 3600))  # Default 1 hour
        self.enabled = bool(self.redis_url)
        self.client: Optional[redis.Redis] = None

        if self.enabled:
            try:
                self.client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30
                )
                # Test connection
                self.client.ping()
                print(f"[{datetime.now()}] Redis cache connected successfully")
                print(f"[{datetime.now()}] Cache TTL: {self.cache_ttl} seconds")
            except Exception as e:
                print(f"[{datetime.now()}] WARNING: Redis connection failed: {e}")
                print(f"[{datetime.now()}] Cache will be disabled")
                self.enabled = False
                self.client = None
        else:
            print(f"[{datetime.now()}] Redis cache disabled (REDIS_URL not set)")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        # Create a string representation of all arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)

        # Hash for consistent key length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"youtube_api:{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                print(f"[{datetime.now()}] Cache HIT: {key}")
                return json.loads(value)
            print(f"[{datetime.now()}] Cache MISS: {key}")
            return None
        except Exception as e:
            print(f"[{datetime.now()}] Cache GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with TTL."""
        if not self.enabled or not self.client:
            return False

        try:
            ttl = ttl or self.cache_ttl
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            print(f"[{datetime.now()}] Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Cache SET error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(key)
            print(f"[{datetime.now()}] Cache DELETE: {key}")
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Cache DELETE error: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all cache entries (use with caution)."""
        if not self.enabled or not self.client:
            return False

        try:
            # Only delete keys with our prefix
            pattern = "youtube_api:*"
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                print(f"[{datetime.now()}] Cache CLEARED: {len(keys)} keys deleted")
            return True
        except Exception as e:
            print(f"[{datetime.now()}] Cache CLEAR error: {e}")
            return False

    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.enabled or not self.client:
            return {
                "enabled": False,
                "status": "disabled"
            }

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
            return {
                "enabled": True,
                "status": "error",
                "error": str(e)
            }


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
        ttl: Time to live in seconds (defaults to CACHE_TTL_SECONDS env var)

    Example:
        @cached(prefix='video_data', ttl=3600)
        def get_video_data(url: str) -> dict:
            # expensive operation
            return data
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key from function arguments
            cache_key = cache._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call the actual function
            result = await func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key from function arguments
            cache_key = cache._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call the actual function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)

            return result

        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
