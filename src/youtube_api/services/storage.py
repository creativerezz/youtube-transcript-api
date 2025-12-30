"""Persistent transcript storage service."""

import json
from datetime import datetime
from typing import Dict, List, Optional

import structlog

from ..config import get_settings
from ..services.cache import get_cache
from ..utils.url_parser import get_youtube_video_id

logger = structlog.get_logger(__name__)


class TranscriptStorage:
    """Service for persistent transcript storage."""

    STORAGE_PREFIX = "transcript_storage"
    METADATA_PREFIX = "transcript_metadata"

    def __init__(self):
        """Initialize transcript storage."""
        self.cache = get_cache()
        self.enabled = self.cache.enabled

    def _get_storage_key(self, video_id: str, language: Optional[str] = None) -> str:
        """Generate storage key for transcript."""
        if language:
            return f"{self.STORAGE_PREFIX}:{video_id}:{language}"
        return f"{self.STORAGE_PREFIX}:{video_id}"

    def _get_metadata_key(self, video_id: str) -> str:
        """Generate metadata key for video."""
        return f"{self.METADATA_PREFIX}:{video_id}"

    def save_transcript(
        self,
        video_id: str,
        transcript: str,
        language: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Save transcript to persistent storage.

        Args:
            video_id: YouTube video ID
            transcript: Transcript text
            language: Language code (optional)
            metadata: Additional metadata (title, author, etc.)

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("storage_disabled", reason="Redis not available")
            return False

        try:
            # Save transcript (no TTL = permanent storage)
            # Use setex with a very long TTL (10 years) to simulate permanent storage
            storage_key = self._get_storage_key(video_id, language)
            self.cache.client.setex(storage_key, 315360000, transcript)  # 10 years
            logger.info("transcript_saved", video_id=video_id, language=language)

            # Update metadata
            metadata_key = self._get_metadata_key(video_id)
            existing_metadata = self.get_metadata(video_id) or {}
            
            # Update or create metadata
            if language:
                if "languages" not in existing_metadata:
                    existing_metadata["languages"] = []
                if language not in existing_metadata["languages"]:
                    existing_metadata["languages"].append(language)

            # Merge provided metadata
            if metadata:
                existing_metadata.update(metadata)

            # Add/update timestamp
            existing_metadata["last_updated"] = datetime.now().isoformat()
            if "created_at" not in existing_metadata:
                existing_metadata["created_at"] = datetime.now().isoformat()

            # Save metadata (no TTL - use 10 years)
            self.cache.client.setex(metadata_key, 315360000, json.dumps(existing_metadata))
            logger.info("metadata_updated", video_id=video_id)

            return True
        except Exception as e:
            logger.error("save_transcript_error", video_id=video_id, error=str(e))
            return False

    def get_transcript(
        self, video_id: str, language: Optional[str] = None
    ) -> Optional[str]:
        """
        Retrieve stored transcript.

        Args:
            video_id: YouTube video ID
            language: Language code (optional, returns default if not specified)

        Returns:
            Transcript text or None if not found
        """
        if not self.enabled:
            return None

        try:
            # Try specific language first
            if language:
                storage_key = self._get_storage_key(video_id, language)
                transcript = self.cache.client.get(storage_key)
                if transcript:
                    logger.info("transcript_retrieved", video_id=video_id, language=language)
                    return transcript

            # Try default (no language specified) - look for any language
            # First check if there's a default key
            storage_key = self._get_storage_key(video_id)
            transcript = self.cache.client.get(storage_key)
            if transcript:
                logger.info("transcript_retrieved", video_id=video_id, language="default")
                return transcript

            # If no default, try to find any language variant
            pattern = f"{self.STORAGE_PREFIX}:{video_id}:*"
            keys = self.cache.client.keys(pattern)
            if keys:
                # Get the first available transcript
                transcript = self.cache.client.get(keys[0])
                if transcript:
                    logger.info("transcript_retrieved", video_id=video_id, language="any")
                    return transcript

            logger.debug("transcript_not_found", video_id=video_id, language=language)
            return None
        except Exception as e:
            logger.error("get_transcript_error", video_id=video_id, error=str(e))
            return None

    def get_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Get metadata for a stored transcript.

        Args:
            video_id: YouTube video ID

        Returns:
            Metadata dictionary or None if not found
        """
        if not self.enabled:
            return None

        try:
            metadata_key = self._get_metadata_key(video_id)
            metadata_json = self.cache.client.get(metadata_key)
            if metadata_json:
                return json.loads(metadata_json)
            return None
        except Exception as e:
            logger.error("get_metadata_error", video_id=video_id, error=str(e))
            return None

    def list_stored_videos(self, limit: int = 100) -> List[Dict]:
        """
        List all stored video transcripts.

        Args:
            limit: Maximum number of videos to return

        Returns:
            List of video metadata dictionaries
        """
        if not self.enabled:
            return []

        try:
            pattern = f"{self.METADATA_PREFIX}:*"
            keys = self.cache.client.keys(pattern)[:limit]

            videos = []
            for key in keys:
                video_id = key.replace(f"{self.METADATA_PREFIX}:", "")
                metadata = self.get_metadata(video_id)
                if metadata:
                    metadata["video_id"] = video_id
                    videos.append(metadata)

            logger.info("videos_listed", count=len(videos))
            return videos
        except Exception as e:
            logger.error("list_videos_error", error=str(e))
            return []

    def delete_transcript(self, video_id: str, language: Optional[str] = None) -> bool:
        """
        Delete stored transcript.

        Args:
            video_id: YouTube video ID
            language: Language code (optional, deletes all languages if not specified)

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            if language:
                # Delete specific language
                storage_key = self._get_storage_key(video_id, language)
                self.cache.client.delete(storage_key)
                logger.info("transcript_deleted", video_id=video_id, language=language)
            else:
                # Delete all languages for this video
                pattern = f"{self.STORAGE_PREFIX}:{video_id}*"
                keys = self.cache.client.keys(pattern)
                if keys:
                    self.cache.client.delete(*keys)

                # Delete metadata
                metadata_key = self._get_metadata_key(video_id)
                self.cache.client.delete(metadata_key)
                logger.info("transcript_deleted", video_id=video_id, language="all")

            return True
        except Exception as e:
            logger.error("delete_transcript_error", video_id=video_id, error=str(e))
            return False

    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage statistics
        """
        if not self.enabled:
            return {"enabled": False}

        try:
            transcript_keys = self.cache.client.keys(f"{self.STORAGE_PREFIX}:*")
            metadata_keys = self.cache.client.keys(f"{self.METADATA_PREFIX}:*")

            return {
                "enabled": True,
                "total_transcripts": len(transcript_keys),
                "total_videos": len(metadata_keys),
            }
        except Exception as e:
            logger.error("storage_stats_error", error=str(e))
            return {"enabled": True, "error": str(e)}


# Global storage instance
_storage_instance: Optional[TranscriptStorage] = None


def get_storage() -> TranscriptStorage:
    """Get or create the global storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = TranscriptStorage()
    return _storage_instance
