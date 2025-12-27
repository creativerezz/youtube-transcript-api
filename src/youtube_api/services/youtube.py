"""YouTube video metadata service using httpx for async HTTP."""

from typing import Optional
from urllib.parse import urlencode

import httpx
import structlog

from ..config import get_settings
from ..exceptions import InvalidURLError, VideoNotFoundError
from ..utils.url_parser import get_youtube_video_id
from .cache import cached

logger = structlog.get_logger(__name__)

# Shared HTTP client for connection pooling
_http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create the shared HTTP client with connection pooling."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
            ),
        )
    return _http_client


async def close_http_client() -> None:
    """Close the shared HTTP client (for cleanup)."""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


class YouTubeService:
    """Service for fetching YouTube video metadata."""

    @staticmethod
    @cached(prefix="video_data", ttl=3600)
    async def get_video_data(url: str) -> dict:
        """
        Get video metadata from YouTube oEmbed API.

        Args:
            url: YouTube URL or video ID

        Returns:
            Dictionary containing video metadata

        Raises:
            InvalidURLError: If URL cannot be parsed
            VideoNotFoundError: If video doesn't exist
        """
        logger.info("fetching_video_data", url=url)

        if not url:
            raise InvalidURLError("No URL provided")

        video_id = get_youtube_video_id(url)
        if not video_id:
            raise InvalidURLError(url)

        logger.debug("video_id_extracted", video_id=video_id)

        try:
            params = {
                "format": "json",
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
            oembed_url = f"https://www.youtube.com/oembed?{urlencode(params)}"

            client = await get_http_client()
            response = await client.get(oembed_url)

            if response.status_code == 404:
                raise VideoNotFoundError(video_id)

            response.raise_for_status()
            video_data = response.json()

            logger.info(
                "video_data_fetched",
                video_id=video_id,
                title=video_data.get("title"),
            )

            return {
                "title": video_data.get("title"),
                "author_name": video_data.get("author_name"),
                "author_url": video_data.get("author_url"),
                "type": video_data.get("type"),
                "height": video_data.get("height"),
                "width": video_data.get("width"),
                "version": video_data.get("version"),
                "provider_name": video_data.get("provider_name"),
                "provider_url": video_data.get("provider_url"),
                "thumbnail_url": video_data.get("thumbnail_url"),
            }

        except httpx.HTTPStatusError as e:
            logger.error("oembed_api_error", status_code=e.response.status_code)
            if e.response.status_code == 404:
                raise VideoNotFoundError(video_id)
            raise VideoNotFoundError(f"Failed to fetch video data: {e}")

        except Exception as e:
            logger.error("video_data_error", error=str(e))
            raise VideoNotFoundError(f"Error getting video data: {e}")
