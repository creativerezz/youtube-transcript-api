"""FastAPI dependency injection for YouTube API Server."""

from typing import Optional

from openai import OpenAI
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import Settings, get_settings
from .services.ai import get_openrouter_client
from .services.cache import RedisCache, get_cache

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


def get_settings_dep() -> Settings:
    """Dependency for getting application settings."""
    return get_settings()


def get_cache_dep() -> RedisCache:
    """Dependency for getting cache instance."""
    return get_cache()


def get_openrouter_dep() -> Optional[OpenAI]:
    """Dependency for getting OpenRouter client."""
    return get_openrouter_client()


async def get_rate_limiter(request: Request) -> Limiter:
    """Dependency for rate limiting."""
    return limiter
