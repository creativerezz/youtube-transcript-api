"""AI service for video notes and translation using OpenRouter."""

from typing import List, Literal, Optional

import structlog
from openai import OpenAI

from ..config import get_settings
from ..exceptions import AIServiceUnavailableError

logger = structlog.get_logger(__name__)

# Cached OpenRouter client
_openrouter_client: Optional[OpenAI] = None
_client_loaded: bool = False

# OpenRouter API endpoint
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_openrouter_client() -> Optional[OpenAI]:
    """Get OpenRouter client from settings."""
    global _openrouter_client, _client_loaded

    if _client_loaded:
        return _openrouter_client

    settings = get_settings()
    if settings.has_openrouter_config:
        _openrouter_client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=OPENROUTER_BASE_URL,
        )
        logger.info("openrouter_client_initialized")
    else:
        logger.warning("openrouter_not_configured")
        _openrouter_client = None

    _client_loaded = True
    return _openrouter_client


class AIService:
    """Service for AI-powered video analysis using OpenRouter."""

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
    def _ensure_client() -> OpenAI:
        """Ensure OpenRouter client is available."""
        client = get_openrouter_client()
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
            AIServiceUnavailableError: If OpenRouter API is not configured
        """
        logger.info("generating_notes", title=title, format=format)

        client = AIService._ensure_client()

        prompt_template = AIService.NOTES_PROMPTS.get(format, AIService.NOTES_PROMPTS["structured"])
        prompt = prompt_template.format(
            title=title,
            author=author,
            transcript=transcript,
        )

        try:
            response = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )

            notes = response.choices[0].message.content
            if not notes:
                raise AIServiceUnavailableError("Failed to generate notes from AI service")
            logger.info("notes_generated", char_count=len(notes), word_count=len(notes.split()))
            return notes
        except Exception as e:
            logger.error("notes_generation_failed", error=str(e), error_type=type(e).__name__)
            raise AIServiceUnavailableError(f"Failed to generate notes: {str(e)}")

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
            AIServiceUnavailableError: If OpenRouter API is not configured
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

        try:
            response = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}],
            )

            translated_text = response.choices[0].message.content
            if not translated_text:
                raise AIServiceUnavailableError("Failed to translate transcript from AI service")
        except Exception as e:
            logger.error("translation_failed", error=str(e), error_type=type(e).__name__)
            raise AIServiceUnavailableError(f"Failed to translate transcript: {str(e)}")

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

            try:
                timestamp_response = client.chat.completions.create(
                    model="xiaomi/mimo-v2-flash:free",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": timestamp_prompt}],
                )

                timestamp_content = timestamp_response.choices[0].message.content
                if timestamp_content:
                    translated_timestamps = timestamp_content.strip().split("\n")
            except Exception as e:
                logger.error("timestamp_translation_failed", error=str(e), error_type=type(e).__name__)
                # Continue without timestamps if translation fails
                translated_timestamps = []

        logger.info(
            "translation_complete",
            char_count=len(translated_text),
            timestamp_count=len(translated_timestamps),
        )

        return translated_text, translated_timestamps

    @staticmethod
    async def process_with_pattern(
        pattern_content: str,
        transcript: str,
        title: str = "Unknown",
        author: str = "Unknown",
    ) -> str:
        """
        Process transcript using a Fabric-style pattern template.

        Args:
            pattern_content: The pattern template content (system.md)
            transcript: Video transcript to process
            title: Video title (for context)
            author: Channel name (for context)

        Returns:
            Processed output from the pattern

        Raises:
            AIServiceUnavailableError: If OpenRouter API is not configured
        """
        logger.info("processing_with_pattern", title=title, pattern_length=len(pattern_content))

        client = AIService._ensure_client()

        # Fabric patterns expect INPUT: at the end where we insert the transcript
        # Add context about the video
        context = f"Video Title: {title}\nChannel: {author}\n\n"
        full_input = context + transcript

        # Replace the INPUT: placeholder with the actual transcript
        prompt = pattern_content.replace("INPUT:", full_input)

        try:
            response = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )

            result = response.choices[0].message.content
            if not result:
                raise AIServiceUnavailableError("Failed to process pattern from AI service")

            logger.info("pattern_processed", char_count=len(result), word_count=len(result.split()))
            return result
        except Exception as e:
            logger.error("pattern_processing_failed", error=str(e), error_type=type(e).__name__)
            raise AIServiceUnavailableError(f"Failed to process with pattern: {str(e)}")
