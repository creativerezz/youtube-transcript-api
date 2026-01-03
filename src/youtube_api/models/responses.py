"""Pydantic response models for API endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VideoDataResponse(BaseModel):
    """Response model for video metadata."""

    title: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    type: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    version: Optional[str] = None
    provider_name: Optional[str] = None
    provider_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class CaptionsResponse(BaseModel):
    """Response model for video captions."""

    captions: str = Field(..., description="Full transcript text")


class TimestampsResponse(BaseModel):
    """Response model for timestamped transcript."""

    timestamps: List[str] = Field(
        ..., description="List of timestamped transcript segments"
    )


class LanguageInfo(BaseModel):
    """Information about an available transcript language."""

    language: str = Field(..., description="Language name")
    language_code: str = Field(..., description="ISO language code")
    is_generated: bool = Field(..., description="Whether transcript is auto-generated")
    is_translatable: bool = Field(..., description="Whether transcript can be translated")


class LanguagesResponse(BaseModel):
    """Response model for available transcript languages."""

    available_languages: List[LanguageInfo] = Field(
        ..., description="List of available transcript languages"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    proxy_status: str = Field(..., description="Webshare proxy status")
    proxy_username: Optional[str] = None
    cache_status: str = Field(..., description="Redis cache status")
    cache_ttl_seconds: Optional[int] = None
    parallel_processing: str = "enabled"


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""

    enabled: bool
    status: str
    total_keys: Optional[int] = None
    ttl_seconds: Optional[int] = None
    keyspace_hits: Optional[int] = None
    keyspace_misses: Optional[int] = None
    error: Optional[str] = None


class CacheClearResponse(BaseModel):
    """Response model for cache clear operation."""

    success: bool
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class NotesResponse(BaseModel):
    """Response model for generated video notes."""

    video_title: Optional[str] = None
    channel: Optional[str] = None
    format: str = Field(..., description="Notes format used")
    notes: str = Field(..., description="Generated notes in markdown")
    word_count: int = Field(..., description="Word count of generated notes")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TranslationResponse(BaseModel):
    """Response model for translated transcript."""

    video_title: Optional[str] = None
    channel: Optional[str] = None
    target_language: str = Field(..., description="Target language")
    translated_transcript: str = Field(..., description="Full translated transcript")
    translated_timestamps: List[str] = Field(
        ..., description="Sample translated timestamps"
    )
    word_count: int = Field(..., description="Word count of translation")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    note: str = Field(
        default="Use this translated transcript with ElevenLabs voice cloning for dubbed audio"
    )


class APIInfoResponse(BaseModel):
    """Response model for root endpoint."""

    name: str = "YouTube Summaries API"
    version: str = "2.0.0"
    endpoints: Dict[str, str]
    docs: str = "/docs"
    ai_features_available: bool


class StoredTranscriptResponse(BaseModel):
    """Response model for stored transcript."""

    video_id: str
    transcript: str
    language: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StorageStatsResponse(BaseModel):
    """Response model for storage statistics."""

    enabled: bool
    total_transcripts: Optional[int] = None
    total_videos: Optional[int] = None
    error: Optional[str] = None


class StorageListResponse(BaseModel):
    """Response model for listing stored transcripts."""

    videos: List[Dict[str, Any]]
    count: int


class StorageSaveResponse(BaseModel):
    """Response model for saving transcript."""

    success: bool
    message: str
    video_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PatternProcessingResponse(BaseModel):
    """Response model for pattern-based transcript processing."""

    video_title: Optional[str] = None
    channel: Optional[str] = None
    pattern: str = Field(..., description="Pattern name used")
    pattern_category: str = Field(..., description="Pattern category")
    result: str = Field(..., description="Processed output from pattern")
    translated: bool = Field(default=False, description="Whether transcript was translated first")
    translation_language: Optional[str] = None
    word_count: int = Field(..., description="Word count of result")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class OpenRouterProxyResponse(BaseModel):
    """Response model for OpenRouter API proxy."""

    response: Any = Field(..., description="Raw response from OpenRouter API")
