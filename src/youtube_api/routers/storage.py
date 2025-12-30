"""Transcript storage endpoints."""

from typing import Dict

from fastapi import APIRouter, Depends, Request
import structlog

from ..dependencies import limiter
from ..exceptions import InvalidURLError
from ..models.requests import SaveTranscriptRequest, YouTubeRequest
from ..models.responses import (
    StorageListResponse,
    StorageSaveResponse,
    StorageStatsResponse,
    StoredTranscriptResponse,
)
from ..services.storage import get_storage
from ..services.transcript import TranscriptService
from ..services.youtube import YouTubeService
from ..utils.url_parser import get_youtube_video_id

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/transcripts/save", response_model=StorageSaveResponse)
@limiter.limit("30/minute")
async def save_transcript(
    request: Request,
    body: SaveTranscriptRequest,
) -> Dict:
    """
    Save a transcript to persistent storage.

    Fetches the transcript if not already stored, then saves it permanently.
    """
    logger.info("save_transcript_request", url=body.url)

    video_id = get_youtube_video_id(body.url)
    if not video_id:
        raise InvalidURLError(body.url).to_http_exception()

    storage = get_storage()
    if not storage.enabled:
        return {
            "success": False,
            "message": "Storage is not enabled. Please configure REDIS_URL.",
            "video_id": video_id,
        }

    try:
        # Get video metadata
        video_data = await YouTubeService.get_video_data(body.url)

        # Get transcript
        captions = await TranscriptService.get_captions(body.url, body.languages)

        # Determine language used
        languages = await TranscriptService.get_available_languages(body.url)
        used_language = None
        if languages:
            if body.languages:
                # Find which language was actually used
                for lang in body.languages:
                    lang_code = next(
                        (l["language_code"] for l in languages if l["language_code"] == lang),
                        None,
                    )
                    if lang_code:
                        used_language = lang_code
                        break
            if not used_language and languages:
                used_language = languages[0]["language_code"]

        # Save transcript
        metadata = {
            "title": video_data.get("title"),
            "author": video_data.get("author_name"),
            "thumbnail_url": video_data.get("thumbnail_url"),
        }

        success = storage.save_transcript(
            video_id=video_id,
            transcript=captions,
            language=used_language,
            metadata=metadata,
        )

        if success:
            return {
                "success": True,
                "message": "Transcript saved successfully",
                "video_id": video_id,
            }
        else:
            return {
                "success": False,
                "message": "Failed to save transcript",
                "video_id": video_id,
            }

    except Exception as e:
        logger.error("save_transcript_error", video_id=video_id, error=str(e))
        return {
            "success": False,
            "message": f"Error saving transcript: {str(e)}",
            "video_id": video_id,
        }


@router.post("/transcripts/get", response_model=StoredTranscriptResponse)
@limiter.limit("60/minute")
async def get_stored_transcript(
    request: Request,
    body: YouTubeRequest,
) -> Dict:
    """
    Retrieve a stored transcript.

    Returns the transcript from persistent storage if available.
    """
    logger.info("get_stored_transcript_request", url=body.url)

    video_id = get_youtube_video_id(body.url)
    if not video_id:
        raise InvalidURLError(body.url).to_http_exception()

    storage = get_storage()
    if not storage.enabled:
        raise InvalidURLError("Storage is not enabled").to_http_exception()

    # Determine language
    language = None
    if body.languages and len(body.languages) > 0:
        language = body.languages[0]

    transcript = storage.get_transcript(video_id, language)
    if not transcript:
        raise InvalidURLError(
            f"Transcript not found for video {video_id}"
        ).to_http_exception()

    metadata = storage.get_metadata(video_id)

    return {
        "video_id": video_id,
        "transcript": transcript,
        "language": language,
        "metadata": metadata,
    }


@router.get("/transcripts/list", response_model=StorageListResponse)
@limiter.limit("30/minute")
async def list_stored_transcripts(request: Request) -> Dict:
    """
    List all stored transcripts.

    Returns metadata for all videos with stored transcripts.
    """
    logger.info("list_stored_transcripts_request")

    storage = get_storage()
    if not storage.enabled:
        return {"videos": [], "count": 0}

    videos = storage.list_stored_videos()
    return {"videos": videos, "count": len(videos)}


@router.post("/transcripts/delete")
@limiter.limit("30/minute")
async def delete_stored_transcript(
    request: Request,
    body: YouTubeRequest,
) -> Dict:
    """
    Delete a stored transcript.

    Removes the transcript and metadata from storage.
    """
    logger.info("delete_stored_transcript_request", url=body.url)

    video_id = get_youtube_video_id(body.url)
    if not video_id:
        raise InvalidURLError(body.url).to_http_exception()

    storage = get_storage()
    if not storage.enabled:
        return {
            "success": False,
            "message": "Storage is not enabled",
        }

    language = None
    if body.languages and len(body.languages) > 0:
        language = body.languages[0]

    success = storage.delete_transcript(video_id, language)
    return {
        "success": success,
        "message": "Transcript deleted successfully" if success else "Failed to delete transcript",
        "video_id": video_id,
    }


@router.get("/transcripts/stats", response_model=StorageStatsResponse)
@limiter.limit("30/minute")
async def get_storage_stats(request: Request) -> Dict:
    """
    Get storage statistics.

    Returns information about stored transcripts.
    """
    logger.info("storage_stats_request")

    storage = get_storage()
    return storage.get_storage_stats()
