"""AI service for video notes and translation using Anthropic Claude."""

from typing import List, Literal, Optional

import structlog
from anthropic import Anthropic

from ..config import get_settings
from ..exceptions import AIServiceUnavailableError

logger = structlog.get_logger(__name__)

# Cached Anthropic client
_anthropic_client: Optional[Anthropic] = None
_client_loaded: bool = False


def get_anthropic_client() -> Optional[Anthropic]:
    """Get Anthropic client from settings."""
    global _anthropic_client, _client_loaded

    if _client_loaded:
        return _anthropic_client

    settings = get_settings()
    if settings.has_anthropic_config:
        _anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        logger.info("anthropic_client_initialized")
    else:
        logger.warning("anthropic_not_configured")
        _anthropic_client = None

    _client_loaded = True
    return _anthropic_client


class AIService:
    """Service for AI-powered video analysis using Claude."""

    # Notes format prompts
    NOTES_PROMPTS = {
        "summary": """Create a concise summary of this YouTube video.

Video Title: {title}
Channel: {author}

Transcript:
{transcript}

Provide:
1. A 2-3 sentence executive summary
2. 3-5 key takeaways as bullet points
3. Main topics covered

Format the response in clean markdown.""",
        "detailed": """Create detailed notes from this YouTube video transcript.

Video Title: {title}
Channel: {author}

Transcript:
{transcript}

Provide:
1. Executive Summary (3-4 sentences)
2. Detailed outline with main sections and subsections
3. Key concepts explained
4. Important quotes or statements
5. Action items or recommendations (if applicable)

Format the response in clean markdown with proper headings.""",
        "structured": """Convert this YouTube video transcript into well-structured notes.

Video Title: {title}
Channel: {author}

Transcript:
{transcript}

Create structured notes with:
1. Overview: Brief description of video content
2. Main Topics: Organized by sections with key points
3. Key Takeaways: Most important information
4. Conclusion: Final thoughts or summary

Format the response in clean markdown with proper headings and bullet points.""",
    }

    TRANSLATION_PROMPT = """Translate this YouTube video transcript to {target_language}.

Video Title: {title}
Channel: {author}

Original Transcript:
{transcript}

Requirements:
1. Translate the entire transcript naturally and accurately
2. Maintain the original tone and style
3. Preserve technical terms appropriately
4. Keep the translation conversational as if spoken
5. Do not add explanations or notes - only provide the translation

Provide ONLY the translated transcript, nothing else."""

    TIMESTAMP_TRANSLATION_PROMPT = """Translate these video timestamps to {target_language}.

Original Timestamps:
{timestamps}

Requirements:
1. Keep the timestamp format (MM:SS - text)
2. Only translate the text part, not the timestamps
3. Maintain natural speech patterns
4. Provide ONLY the translated timestamps, one per line

Translated timestamps:"""

    @staticmethod
    def _ensure_client() -> Anthropic:
        """Ensure Anthropic client is available."""
        client = get_anthropic_client()
        if not client:
            raise AIServiceUnavailableError()
        return client

    @staticmethod
    async def generate_notes(
        title: str,
        author: str,
        transcript: str,
        format: Literal["structured", "summary", "detailed"] = "structured",
    ) -> str:
        """
        Generate structured notes from video transcript.

        Args:
            title: Video title
            author: Channel name
            transcript: Full transcript text
            format: Notes format (structured, summary, detailed)

        Returns:
            Generated notes in markdown format

        Raises:
            AIServiceUnavailableError: If Anthropic API is not configured
        """
        logger.info("generating_notes", title=title, format=format)

        client = AIService._ensure_client()

        prompt_template = AIService.NOTES_PROMPTS.get(format, AIService.NOTES_PROMPTS["structured"])
        prompt = prompt_template.format(
            title=title,
            author=author,
            transcript=transcript,
        )

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        notes = message.content[0].text
        logger.info("notes_generated", char_count=len(notes), word_count=len(notes.split()))
        return notes

    @staticmethod
    async def translate_transcript(
        title: str,
        author: str,
        transcript: str,
        target_language: str,
        timestamps: Optional[List[str]] = None,
    ) -> tuple[str, List[str]]:
        """
        Translate video transcript to target language.

        Args:
            title: Video title
            author: Channel name
            transcript: Full transcript text
            target_language: Target language (e.g., "Spanish", "French")
            timestamps: Optional list of timestamped segments to translate

        Returns:
            Tuple of (translated_transcript, translated_timestamps)

        Raises:
            AIServiceUnavailableError: If Anthropic API is not configured
        """
        logger.info("translating_transcript", title=title, target_language=target_language)

        client = AIService._ensure_client()

        # Translate main transcript
        prompt = AIService.TRANSLATION_PROMPT.format(
            target_language=target_language,
            title=title,
            author=author,
            transcript=transcript,
        )

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )

        translated_text = message.content[0].text

        # Translate timestamps if provided
        translated_timestamps = []
        if timestamps:
            # Sample first 20 timestamps to keep costs reasonable
            sample_timestamps = timestamps[:20] if len(timestamps) > 20 else timestamps
            timestamps_text = "\n".join(sample_timestamps)

            timestamp_prompt = AIService.TIMESTAMP_TRANSLATION_PROMPT.format(
                target_language=target_language,
                timestamps=timestamps_text,
            )

            timestamp_message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": timestamp_prompt}],
            )

            translated_timestamps = timestamp_message.content[0].text.strip().split("\n")

        logger.info(
            "translation_complete",
            char_count=len(translated_text),
            timestamp_count=len(translated_timestamps),
        )

        return translated_text, translated_timestamps
