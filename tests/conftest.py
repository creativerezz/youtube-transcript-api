"""pytest fixtures for YouTube API Server tests."""

import pytest
from fastapi.testclient import TestClient

from src.youtube_api.app import app
from src.youtube_api.services.cache import RedisCache, get_cache


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def cache():
    """Get the cache instance for testing."""
    return get_cache()


@pytest.fixture
def sample_video_id():
    """Sample YouTube video ID for testing."""
    return "dQw4w9WgXcQ"


@pytest.fixture
def sample_video_url():
    """Sample YouTube video URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
