"""YouTube transcript/caption service."""

import asyncio
from typing import List, Optional, Tuple

import structlog
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

from ..config import get_settings
from ..exceptions import InvalidURLError, TranscriptNotFoundError
from ..utils.url_parser import get_youtube_video_id
from .cache import cached

logger = structlog.get_logger(__name__)

# Cached proxy configuration
_proxy_config: Optional[WebshareProxyConfig] = None
_proxy_config_loaded: bool = False


def get_proxy_config() -> Optional[WebshareProxyConfig]:
    """Get Webshare proxy configuration from settings."""
    global _proxy_config, _proxy_config_loaded

    if _proxy_config_loaded:
        return _proxy_config

    settings = get_settings()
    if settings.has_proxy_config:
        _proxy_config = WebshareProxyConfig(
            proxy_username=settings.webshare_proxy_username,
            proxy_password=settings.webshare_proxy_password,
            filter_ip_locations=["de", "us"],
        )
        logger.info("proxy_config_loaded", username=settings.webshare_proxy_username)
    else:
        logger.warning("proxy_not_configured")
        _proxy_config = None

    _proxy_config_loaded = True
    return _proxy_config


def create_youtube_api() -> YouTubeTranscriptApi:
    """Create YouTubeTranscriptApi instance with optional proxy."""
    proxy_config = get_proxy_config()
    if proxy_config:
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    return YouTubeTranscriptApi()


class TranscriptService:
    """Service for fetching YouTube video transcripts."""

    @staticmethod
    def _get_transcript_with_fallback(
        video_id: str, languages: Optional[List[str]] = None
    ) -> Tuple[any, List[str]]:
        """
        Get transcript with language fallback logic.

        Args:
            video_id: YouTube video ID
            languages: Preferred languages list

        Returns:
            Tuple of (transcript, available_languages)
        """
        api = create_youtube_api()
        transcript_list = api.list(video_id)
        available_languages = [t.language_code for t in transcript_list]

        if languages:
            for lang in languages:
                if lang in available_languages:
                    return api.fetch(video_id, languages=[lang]), available_languages
            # Fallback to first available
            return api.fetch(video_id, languages=[available_languages[0]]), available_languages

        # Prefer English if available
        if "en" in available_languages:
            return api.fetch(video_id, languages=["en"]), available_languages

        return api.fetch(video_id, languages=[available_languages[0]]), available_languages

    @staticmethod
    @cached(prefix="video_captions", ttl=3600)
    async def get_captions(url: str, languages: Optional[List[str]] = None) -> str:
        """
        Get video captions/transcript as plain text.

        Args:
            url: YouTube URL or video ID
            languages: Preferred transcript languages

        Returns:
            Full transcript text

        Raises:
            InvalidURLError: If URL cannot be parsed
            TranscriptNotFoundError: If no transcript is available
        """
        logger.info("fetching_captions", url=url, languages=languages)

        if not url:
            raise InvalidURLError("No URL provided")

        video_id = get_youtube_video_id(url)
        if not video_id:
            raise InvalidURLError(url)

        try:
            transcript, available = await asyncio.to_thread(
                TranscriptService._get_transcript_with_fallback, video_id, languages
            )

            logger.info(
                "transcript_fetched",
                video_id=video_id,
                language=transcript.language_code,
                snippet_count=len(transcript),
                available_languages=available,
            )

            caption_text = " ".join(snippet.text for snippet in transcript)
            logger.debug("captions_combined", char_count=len(caption_text))
            return caption_text

        except Exception as e:
            logger.error("transcript_error", video_id=video_id, error=str(e))
            raise TranscriptNotFoundError(video_id, languages)

    @staticmethod
    @cached(prefix="video_timestamps", ttl=3600)
    async def get_timestamps(
        url: str, languages: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get timestamped transcript segments.

        Args:
            url: YouTube URL or video ID
            languages: Preferred transcript languages

        Returns:
            List of timestamped transcript segments

        Raises:
            InvalidURLError: If URL cannot be parsed
            TranscriptNotFoundError: If no transcript is available
        """
        logger.info("fetching_timestamps", url=url, languages=languages)

        if not url:
            raise InvalidURLError("No URL provided")

        video_id = get_youtube_video_id(url)
        if not video_id:
            raise InvalidURLError(url)

        try:
            transcript, _ = await asyncio.to_thread(
                TranscriptService._get_transcript_with_fallback, video_id, languages
            )

            timestamps = []
            for snippet in transcript:
                start = int(snippet.start)
                minutes, seconds = divmod(start, 60)
                timestamp = f"{minutes}:{seconds:02d} - {snippet.text}"
                timestamps.append(timestamp)

            logger.info("timestamps_generated", count=len(timestamps))
            return timestamps

        except Exception as e:
            logger.error("timestamp_error", video_id=video_id, error=str(e))
            raise TranscriptNotFoundError(video_id, languages)

    @staticmethod
    @cached(prefix="video_languages", ttl=3600)
    async def get_available_languages(url: str) -> List[dict]:
        """
        List available transcript languages for a video.

        Args:
            url: YouTube URL or video ID

        Returns:
            List of language info dictionaries

        Raises:
            InvalidURLError: If URL cannot be parsed
            TranscriptNotFoundError: If video has no transcripts
        """
        logger.info("listing_languages", url=url)

        if not url:
            raise InvalidURLError("No URL provided")

        video_id = get_youtube_video_id(url)
        if not video_id:
            raise InvalidURLError(url)

        try:

            def list_transcripts(vid: str):
                api = create_youtube_api()
                return api.list(vid)

            transcript_list = await asyncio.to_thread(list_transcripts, video_id)

            languages_info = []
            for transcript in transcript_list:
                lang_info = {
                    "language": transcript.language,
                    "language_code": transcript.language_code,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable,
                }
                languages_info.append(lang_info)

            logger.info("languages_found", count=len(languages_info))
            return languages_info

        except Exception as e:
            logger.error("languages_error", video_id=video_id, error=str(e))
            raise TranscriptNotFoundError(video_id)
