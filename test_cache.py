#!/usr/bin/env python3
"""
Quick test script to verify Redis caching functionality
"""
import os
import sys
from cache import get_cache

def test_cache():
    """Test basic cache operations"""
    print("Testing Redis cache...")
    print("-" * 50)

    # Get cache instance
    cache = get_cache()

    print(f"Cache enabled: {cache.enabled}")
    if not cache.enabled:
        print("\nℹ️  Cache is disabled (REDIS_URL not set)")
        print("To enable caching:")
        print("1. Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
        print("2. Set REDIS_URL: export REDIS_URL=redis://localhost:6379")
        print("3. Run this test again")
        return

    print(f"Cache TTL: {cache.cache_ttl} seconds")
    print()

    # Test set/get
    print("Test 1: Set and get a value")
    test_key = "youtube_api:test:123"
    test_value = {"title": "Test Video", "author": "Test Author"}

    success = cache.set(test_key, test_value, ttl=60)
    print(f"  Set operation: {'✓ Success' if success else '✗ Failed'}")

    retrieved = cache.get(test_key)
    print(f"  Get operation: {'✓ Success' if retrieved == test_value else '✗ Failed'}")
    print(f"  Retrieved value: {retrieved}")
    print()

    # Test cache stats
    print("Test 2: Get cache statistics")
    stats = cache.get_stats()
    print(f"  Status: {stats.get('status', 'unknown')}")
    print(f"  Total keys: {stats.get('total_keys', 0)}")
    print(f"  Keyspace hits: {stats.get('keyspace_hits', 0)}")
    print(f"  Keyspace misses: {stats.get('keyspace_misses', 0)}")
    print()

    # Test delete
    print("Test 3: Delete a value")
    success = cache.delete(test_key)
    print(f"  Delete operation: {'✓ Success' if success else '✗ Failed'}")

    retrieved = cache.get(test_key)
    print(f"  Verify deletion: {'✓ Success' if retrieved is None else '✗ Failed'}")
    print()

    print("-" * 50)
    print("✅ All cache tests completed!")

if __name__ == "__main__":
    test_cache()
