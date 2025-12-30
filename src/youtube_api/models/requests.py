"""Pydantic request models for API endpoints."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class YouTubeRequest(BaseModel):
    """Base request model for YouTube video operations."""

    url: str = Field(..., description="YouTube URL or video ID")
    languages: Optional[List[str]] = Field(
        default=None,
        description="Preferred transcript languages (e.g., ['en', 'es'])",
    )


class VideoNotesRequest(BaseModel):
    """Request model for generating video notes."""

    url: str = Field(..., description="YouTube URL or video ID")
    languages: Optional[List[str]] = Field(
        default=None,
        description="Preferred transcript languages",
    )
    format: Literal["structured", "summary", "detailed"] = Field(
        default="structured",
        description="Notes format: structured, summary, or detailed",
    )


class VideoTranslateRequest(BaseModel):
    """Request model for translating video transcripts."""

    url: str = Field(..., description="YouTube URL or video ID")
    target_language: str = Field(
        ...,
        description="Target language for translation (e.g., 'Spanish', 'French')",
    )
    source_languages: Optional[List[str]] = Field(
        default=None,
        description="Preferred source transcript languages",
    )


class SaveTranscriptRequest(BaseModel):
    """Request model for saving a transcript."""

    url: str = Field(..., description="YouTube URL or video ID")
    languages: Optional[List[str]] = Field(
        default=None,
        description="Preferred transcript languages",
    )
    auto_save: bool = Field(
        default=True,
        description="Automatically save transcripts when fetched",
    )
