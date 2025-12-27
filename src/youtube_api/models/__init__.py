"""Pydantic models for request/response validation."""

from .requests import YouTubeRequest, VideoNotesRequest, VideoTranslateRequest
from .responses import (
    VideoDataResponse,
    CaptionsResponse,
    TimestampsResponse,
    LanguagesResponse,
    HealthResponse,
    CacheStatsResponse,
    NotesResponse,
    TranslationResponse,
)

__all__ = [
    # Request models
    "YouTubeRequest",
    "VideoNotesRequest",
    "VideoTranslateRequest",
    # Response models
    "VideoDataResponse",
    "CaptionsResponse",
    "TimestampsResponse",
    "LanguagesResponse",
    "HealthResponse",
    "CacheStatsResponse",
    "NotesResponse",
    "TranslationResponse",
]
