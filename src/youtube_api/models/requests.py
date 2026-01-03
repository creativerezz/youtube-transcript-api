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


class VideoPatternRequest(BaseModel):
    """Request model for processing video with a pattern template."""

    url: str = Field(..., description="YouTube URL or video ID")
    pattern: str = Field(
        ...,
        description="Pattern name to apply (e.g., 'extract_ideas', 'create_summary')",
    )
    languages: Optional[List[str]] = Field(
        default=None,
        description="Preferred transcript languages",
    )
    translate_to: Optional[str] = Field(
        default=None,
        description="Translate transcript before pattern processing (e.g., 'Spanish', 'French')",
    )


class OpenRouterProxyRequest(BaseModel):
    """Request model for OpenRouter API proxy."""

    prompt: str = Field(..., description="The prompt to send to the AI model")
    model: Optional[str] = Field(
        default=None,
        description="Model name (defaults to xiaomi/mimo-v2-flash:free if not specified)",
    )
    max_tokens: Optional[int] = Field(
        default=800,
        description="Maximum tokens to generate",
    )
