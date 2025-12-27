"""AI-powered endpoints for video notes and translation."""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, Request
import structlog

from ..dependencies import get_anthropic_dep, limiter
from ..exceptions import AIServiceUnavailableError, InvalidURLError, TranscriptNotFoundError
from ..models.requests import VideoNotesRequest, VideoTranslateRequest
from ..models.responses import NotesResponse, TranslationResponse
from ..services.ai import AIService
from ..services.transcript import TranscriptService
from ..services.youtube import YouTubeService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/video-notes", response_model=NotesResponse)
@limiter.limit("10/minute")
async def generate_video_notes(
    request: Request,
    body: VideoNotesRequest,
    anthropic=Depends(get_anthropic_dep),
) -> Dict:
    """
    Generate structured notes from a YouTube video transcript.

    Requires ANTHROPIC_API_KEY to be configured.
    Supports three formats: structured (default), summary, detailed.
    """
    logger.info("video_notes_request", url=body.url, format=body.format)

    if not anthropic:
        raise AIServiceUnavailableError().to_http_exception()

    try:
        # Get video metadata
        video_data = await YouTubeService.get_video_data(body.url)

        # Get transcript
        captions = await TranscriptService.get_captions(body.url, body.languages)

        # Generate notes
        notes = await AIService.generate_notes(
            title=video_data.get("title", "Unknown"),
            author=video_data.get("author_name", "Unknown"),
            transcript=captions,
            format=body.format,
        )

        return {
            "video_title": video_data.get("title"),
            "channel": video_data.get("author_name"),
            "format": body.format,
            "notes": notes,
            "word_count": len(notes.split()),
            "timestamp": datetime.now().isoformat(),
        }

    except (InvalidURLError, TranscriptNotFoundError) as e:
        raise e.to_http_exception()
    except AIServiceUnavailableError as e:
        raise e.to_http_exception()


@router.post("/video-translate", response_model=TranslationResponse)
@limiter.limit("10/minute")
async def translate_video_transcript(
    request: Request,
    body: VideoTranslateRequest,
    anthropic=Depends(get_anthropic_dep),
) -> Dict:
    """
    Translate a YouTube video transcript to another language.

    Requires ANTHROPIC_API_KEY to be configured.
    Supports 50+ languages.
    """
    logger.info(
        "video_translate_request",
        url=body.url,
        target_language=body.target_language,
    )

    if not anthropic:
        raise AIServiceUnavailableError().to_http_exception()

    try:
        # Get video metadata
        video_data = await YouTubeService.get_video_data(body.url)

        # Get transcript
        captions = await TranscriptService.get_captions(body.url, body.source_languages)

        # Get timestamps for translation
        timestamps = await TranscriptService.get_timestamps(body.url, body.source_languages)

        # Translate
        translated_text, translated_timestamps = await AIService.translate_transcript(
            title=video_data.get("title", "Unknown"),
            author=video_data.get("author_name", "Unknown"),
            transcript=captions,
            target_language=body.target_language,
            timestamps=timestamps,
        )

        return {
            "video_title": video_data.get("title"),
            "channel": video_data.get("author_name"),
            "target_language": body.target_language,
            "translated_transcript": translated_text,
            "translated_timestamps": translated_timestamps,
            "word_count": len(translated_text.split()),
            "timestamp": datetime.now().isoformat(),
            "note": "Use this translated transcript with ElevenLabs voice cloning for dubbed audio",
        }

    except (InvalidURLError, TranscriptNotFoundError) as e:
        raise e.to_http_exception()
    except AIServiceUnavailableError as e:
        raise e.to_http_exception()
