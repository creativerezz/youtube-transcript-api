"""FastAPI dependency injection for YouTube API Server."""

from typing import Optional

from anthropic import Anthropic
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import Settings, get_settings
from .services.ai import get_anthropic_client
from .services.cache import RedisCache, get_cache

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


def get_settings_dep() -> Settings:
    """Dependency for getting application settings."""
    return get_settings()


def get_cache_dep() -> RedisCache:
    """Dependency for getting cache instance."""
    return get_cache()


def get_anthropic_dep() -> Optional[Anthropic]:
    """Dependency for getting Anthropic client."""
    return get_anthropic_client()


async def get_rate_limiter(request: Request) -> Limiter:
    """Dependency for rate limiting."""
    return limiter
