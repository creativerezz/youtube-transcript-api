"""Video data and transcript endpoints."""

from typing import Dict, List

from fastapi import APIRouter, Depends, Request
import structlog

from ..dependencies import limiter
from ..models.requests import YouTubeRequest
from ..models.responses import (
    CaptionsResponse,
    LanguagesResponse,
    TimestampsResponse,
    VideoDataResponse,
)
from ..services.transcript import TranscriptService
from ..services.youtube import YouTubeService
from ..exceptions import InvalidURLError, TranscriptNotFoundError, VideoNotFoundError

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/video-data", response_model=VideoDataResponse)
@limiter.limit("60/minute")
async def get_video_data(request: Request, body: YouTubeRequest) -> Dict:
    """
    Get video metadata from YouTube.

    Returns title, author, thumbnail, and other oEmbed data.
    Results are cached for 1 hour.
    """
    logger.info("video_data_request", url=body.url)

    try:
        result = await YouTubeService.get_video_data(body.url)
        return result
    except (InvalidURLError, VideoNotFoundError) as e:
        raise e.to_http_exception()


@router.post("/video-captions", response_model=CaptionsResponse)
@limiter.limit("60/minute")
async def get_video_captions(request: Request, body: YouTubeRequest) -> Dict:
    """
    Get video captions/transcript as plain text.

    Supports language preferences. Results are cached for 1 hour.
    """
    logger.info("video_captions_request", url=body.url, languages=body.languages)

    try:
        captions = await TranscriptService.get_captions(body.url, body.languages)
        return {"captions": captions}
    except (InvalidURLError, TranscriptNotFoundError) as e:
        raise e.to_http_exception()


@router.post("/video-timestamps", response_model=TimestampsResponse)
@limiter.limit("60/minute")
async def get_video_timestamps(request: Request, body: YouTubeRequest) -> Dict:
    """
    Get timestamped transcript segments.

    Returns list of "MM:SS - text" formatted segments.
    Results are cached for 1 hour.
    """
    logger.info("video_timestamps_request", url=body.url, languages=body.languages)

    try:
        timestamps = await TranscriptService.get_timestamps(body.url, body.languages)
        return {"timestamps": timestamps}
    except (InvalidURLError, TranscriptNotFoundError) as e:
        raise e.to_http_exception()


@router.post("/video-transcript-languages", response_model=LanguagesResponse)
@limiter.limit("60/minute")
async def get_video_transcript_languages(request: Request, body: YouTubeRequest) -> Dict:
    """
    List available transcript languages for a video.

    Returns language codes, names, and whether they're auto-generated.
    Results are cached for 1 hour.
    """
    logger.info("video_languages_request", url=body.url)

    try:
        languages = await TranscriptService.get_available_languages(body.url)
        return {"available_languages": languages}
    except (InvalidURLError, TranscriptNotFoundError) as e:
        raise e.to_http_exception()
