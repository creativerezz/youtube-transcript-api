"""YouTube URL parsing utilities."""

from typing import Optional
from urllib.parse import urlparse, parse_qs

import structlog

logger = structlog.get_logger(__name__)


def get_youtube_video_id(url_or_id: str) -> Optional[str]:
    """
    Extract video ID from a YouTube URL or validate a direct video ID.

    Supported formats:
    - Direct video ID: "dQw4w9WgXcQ"
    - Standard: https://www.youtube.com/watch?v=VIDEO_ID
    - Short: https://youtu.be/VIDEO_ID
    - Embed: https://www.youtube.com/embed/VIDEO_ID
    - Shorts: https://youtube.com/shorts/VIDEO_ID
    - Live: https://www.youtube.com/live/VIDEO_ID
    - Mobile: https://m.youtube.com/watch?v=VIDEO_ID
    - With timestamp: https://youtu.be/VIDEO_ID?t=123
    - With playlist: https://www.youtube.com/watch?v=VIDEO_ID&list=...

    Args:
        url_or_id: YouTube URL or direct video ID

    Returns:
        Video ID string or None if extraction fails
    """
    logger.debug("parsing_youtube_url", input=url_or_id)

    # Check if it's already a video ID (11 characters, alphanumeric with - and _)
    if len(url_or_id) == 11 and all(c.isalnum() or c in "-_" for c in url_or_id):
        logger.debug("direct_video_id_detected", video_id=url_or_id)
        return url_or_id

    # Try to parse as URL
    try:
        parsed_url = urlparse(url_or_id)
        hostname = parsed_url.hostname

        # Handle missing scheme
        if not hostname:
            if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
                parsed_url = urlparse(f"https://{url_or_id}")
                hostname = parsed_url.hostname
            else:
                logger.warning("invalid_url_format", input=url_or_id)
                return None

        # youtu.be format (short links)
        if hostname in ("youtu.be", "www.youtu.be"):
            video_id = parsed_url.path[1:].split("?")[0].split("&")[0]
            logger.debug("extracted_from_youtu_be", video_id=video_id)
            return video_id

        # youtube.com formats
        if hostname in (
            "www.youtube.com",
            "youtube.com",
            "m.youtube.com",
            "music.youtube.com",
        ):
            # Standard watch URL: /watch?v=VIDEO_ID
            if parsed_url.path == "/watch" or parsed_url.path.startswith("/watch?"):
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get("v", [None])[0]
                logger.debug("extracted_from_watch_url", video_id=video_id)
                return video_id

            # Embed URL: /embed/VIDEO_ID
            if parsed_url.path.startswith("/embed/"):
                video_id = parsed_url.path.split("/")[2].split("?")[0]
                logger.debug("extracted_from_embed_url", video_id=video_id)
                return video_id

            # Old format: /v/VIDEO_ID
            if parsed_url.path.startswith("/v/"):
                video_id = parsed_url.path.split("/")[2].split("?")[0]
                logger.debug("extracted_from_v_url", video_id=video_id)
                return video_id

            # Shorts format: /shorts/VIDEO_ID
            if parsed_url.path.startswith("/shorts/"):
                video_id = parsed_url.path.split("/")[2].split("?")[0]
                logger.debug("extracted_from_shorts_url", video_id=video_id)
                return video_id

            # Live format: /live/VIDEO_ID
            if parsed_url.path.startswith("/live/"):
                video_id = parsed_url.path.split("/")[2].split("?")[0]
                logger.debug("extracted_from_live_url", video_id=video_id)
                return video_id

    except Exception as e:
        logger.error("url_parsing_failed", error=str(e), input=url_or_id)
        return None

    logger.warning("video_id_extraction_failed", input=url_or_id)
    return None
