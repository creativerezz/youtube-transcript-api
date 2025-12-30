"""FastAPI application setup and configuration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import structlog

from .config import get_settings
from .dependencies import limiter
from .exceptions import YouTubeAPIError
from .routers import ai_router, health_router, storage_router, video_router
from .services.cache import get_cache
from .services.transcript import get_proxy_config
from .services.youtube import close_http_client
from .utils.logging import setup_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    settings = get_settings()

    # Setup logging
    setup_logging(json_logs=settings.json_logs, log_level=settings.log_level)

    # Startup
    logger.info("=" * 40)
    logger.info("youtube_api_server_starting")
    logger.info("=" * 40)

    # Initialize services
    cache = get_cache()
    proxy_config = get_proxy_config()

    logger.info(
        "server_config",
        host=settings.host,
        port=settings.port,
        cache_enabled=cache.enabled,
        cache_ttl=cache.cache_ttl if cache.enabled else None,
        proxy_enabled=proxy_config is not None,
        ai_enabled=settings.has_openrouter_config,
    )

    logger.info("available_endpoints", endpoints=[
        "GET /",
        "GET /health",
        "GET /cache/stats",
        "POST /cache/clear",
        "POST /video-data",
        "POST /video-captions",
        "POST /video-timestamps",
        "POST /video-transcript-languages",
        "POST /video-notes",
        "POST /video-translate",
        "POST /transcripts/save",
        "POST /transcripts/get",
        "GET /transcripts/list",
        "POST /transcripts/delete",
        "GET /transcripts/stats",
    ])

    logger.info("=" * 40)

    yield

    # Shutdown
    logger.info("=" * 40)
    logger.info("youtube_api_server_shutting_down")
    await close_http_client()
    logger.info("=" * 40)


# Create FastAPI app
app = FastAPI(
    title="YouTube Tools API",
    description="API for extracting YouTube video information, transcripts, and AI-powered features",
    version="2.0.0",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Custom exception handler for YouTubeAPIError
@app.exception_handler(YouTubeAPIError)
async def youtube_api_error_handler(request: Request, exc: YouTubeAPIError):
    """Handle custom YouTube API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


# Include routers
app.include_router(health_router)
app.include_router(video_router)
app.include_router(ai_router)
app.include_router(storage_router)


def run_server():
    """Run the server (for CLI entry point)."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.youtube_api.app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run_server()
