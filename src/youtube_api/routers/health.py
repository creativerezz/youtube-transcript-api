"""Health and cache management endpoints."""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends
import structlog

from ..config import Settings, get_settings
from ..dependencies import get_cache_dep, get_anthropic_dep
from ..models.responses import (
    APIInfoResponse,
    CacheClearResponse,
    CacheStatsResponse,
    HealthResponse,
)
from ..services.cache import RedisCache

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=APIInfoResponse)
async def root(anthropic=Depends(get_anthropic_dep)) -> Dict:
    """Root endpoint with API information."""
    return {
        "name": "YouTube Tools API",
        "version": "2.0.0",
        "endpoints": {
            "GET /": "This info",
            "GET /health": "Health check",
            "GET /cache/stats": "Cache statistics",
            "POST /cache/clear": "Clear cache",
            "POST /video-data": "Get video metadata (cached)",
            "POST /video-captions": "Get video captions/transcripts (cached)",
            "POST /video-timestamps": "Get timestamped transcripts (cached)",
            "POST /video-transcript-languages": "List available languages (cached)",
            "POST /video-notes": "Generate structured notes from video (requires ANTHROPIC_API_KEY)",
            "POST /video-translate": "Translate video transcript (requires ANTHROPIC_API_KEY)",
        },
        "docs": "/docs",
        "ai_features_available": anthropic is not None,
    }


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
    cache: RedisCache = Depends(get_cache_dep),
) -> Dict:
    """Health check endpoint to verify server and service status."""
    logger.info("health_check")

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "proxy_status": f"webshare_{'enabled' if settings.has_proxy_config else 'disabled'}",
        "proxy_username": settings.webshare_proxy_username if settings.has_proxy_config else None,
        "cache_status": f"redis_{'enabled' if cache.enabled else 'disabled'}",
        "cache_ttl_seconds": cache.cache_ttl if cache.enabled else None,
        "parallel_processing": "enabled",
    }


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats(cache: RedisCache = Depends(get_cache_dep)) -> Dict:
    """Get cache statistics."""
    logger.info("cache_stats_requested")
    return cache.get_stats()


@router.post("/cache/clear", response_model=CacheClearResponse)
async def cache_clear(cache: RedisCache = Depends(get_cache_dep)) -> Dict:
    """Clear all cached data."""
    logger.info("cache_clear_requested")

    if not cache.enabled:
        return {
            "success": False,
            "message": "Cache is not enabled",
            "timestamp": datetime.now().isoformat(),
        }

    success = cache.clear_all()
    return {
        "success": success,
        "message": "Cache cleared successfully" if success else "Failed to clear cache",
        "timestamp": datetime.now().isoformat(),
    }
