"""API routers for YouTube API Server."""

from .health import router as health_router
from .video import router as video_router
from .ai import router as ai_router

__all__ = ["health_router", "video_router", "ai_router"]
