"""Tests for Redis caching service."""

import pytest

from src.youtube_api.services.cache import RedisCache, get_cache


class TestRedisCache:
    """Test cases for RedisCache class."""

    def test_cache_instance_creation(self, cache):
        """Test cache instance is created."""
        assert cache is not None
        assert isinstance(cache, RedisCache)

    def test_get_cache_singleton(self):
        """Test get_cache returns same instance."""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2

    def test_cache_stats_structure(self, cache):
        """Test cache stats returns expected structure."""
        stats = cache.get_stats()
        assert "enabled" in stats
        assert "status" in stats

    @pytest.mark.skipif(
        not get_cache().enabled,
        reason="Redis not configured",
    )
    def test_set_and_get(self, cache):
        """Test setting and getting a value."""
        test_key = "youtube_api:test:pytest"
        test_value = {"title": "Test Video", "author": "Test Author"}

        # Set value
        success = cache.set(test_key, test_value, ttl=60)
        assert success is True

        # Get value
        retrieved = cache.get(test_key)
        assert retrieved == test_value

        # Cleanup
        cache.delete(test_key)

    @pytest.mark.skipif(
        not get_cache().enabled,
        reason="Redis not configured",
    )
    def test_delete(self, cache):
        """Test deleting a value."""
        test_key = "youtube_api:test:delete"
        test_value = {"test": "data"}

        # Set value
        cache.set(test_key, test_value, ttl=60)

        # Delete value
        success = cache.delete(test_key)
        assert success is True

        # Verify deletion
        retrieved = cache.get(test_key)
        assert retrieved is None

    def test_get_nonexistent_key(self, cache):
        """Test getting a key that doesn't exist."""
        result = cache.get("youtube_api:nonexistent:key")
        assert result is None

    def test_generate_key(self, cache):
        """Test cache key generation."""
        key = cache._generate_key("test", "arg1", "arg2", kwarg1="val1")
        assert key.startswith("youtube_api:test:")
        assert len(key) > len("youtube_api:test:")
