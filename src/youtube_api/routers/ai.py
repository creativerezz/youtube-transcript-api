"""AI-powered endpoints for video notes and translation."""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
import httpx
import structlog

from ..config import get_settings
from ..dependencies import get_openrouter_dep, limiter
from ..exceptions import AIServiceUnavailableError, InvalidURLError, TranscriptNotFoundError
from ..models.requests import OpenRouterProxyRequest, VideoNotesRequest, VideoPatternRequest, VideoTranslateRequest
from ..models.responses import NotesResponse, OpenRouterProxyResponse, PatternProcessingResponse, TranslationResponse
from ..services.ai import AIService
from ..services.transcript import TranscriptService
from ..services.youtube import YouTubeService
from ..utils.prompt_service import get_prompt_service

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/video-notes", response_model=NotesResponse)
@limiter.limit("10/minute")
async def generate_video_notes(
    request: Request,
    body: VideoNotesRequest,
    openrouter=Depends(get_openrouter_dep),
) -> Dict:
    """
    Generate structured notes from a YouTube video transcript.

    Requires OPENROUTER_API_KEY to be configured.
    Supports three formats: structured (default), summary, detailed.
    """
    logger.info("video_notes_request", url=body.url, format=body.format)

    if not openrouter:
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
    openrouter=Depends(get_openrouter_dep),
) -> Dict:
    """
    Translate a YouTube video transcript to another language.

    Requires OPENROUTER_API_KEY to be configured.
    Supports 50+ languages.
    """
    logger.info(
        "video_translate_request",
        url=body.url,
        target_language=body.target_language,
    )

    if not openrouter:
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


@router.post("/openrouter-proxy", response_model=OpenRouterProxyResponse)
@limiter.limit("30/minute")
async def openrouter_proxy(
    request: Request,
    body: OpenRouterProxyRequest,
    openrouter=Depends(get_openrouter_dep),
) -> Dict[str, Any]:
    """
    Proxy endpoint for OpenRouter API.

    Forwards requests to OpenRouter's chat completions endpoint.
    Requires OPENROUTER_API_KEY to be configured.
    """
    logger.info("openrouter_proxy_request", model=body.model, max_tokens=body.max_tokens)

    if not openrouter:
        raise AIServiceUnavailableError().to_http_exception()

    try:
        settings = get_settings()
        if not settings.openrouter_api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENROUTER_API_KEY not configured"
            )

        model = body.model or "xiaomi/mimo-v2-flash:free"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": body.prompt}],
                    "max_tokens": body.max_tokens,
                },
            )

            response.raise_for_status()
            data = response.json()

            return {"response": data}

    except httpx.HTTPStatusError as e:
        logger.error("openrouter_http_error", status=e.response.status_code, detail=str(e))
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenRouter API error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error("openrouter_request_error", detail=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to OpenRouter: {str(e)}"
        )
    except Exception as e:
        logger.error("openrouter_unexpected_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
