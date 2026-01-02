"""
Prompt template service for managing and loading Fabric-style patterns.

This service manages prompt templates stored in the 'prompts' directory,
allowing for pattern-based processing of video transcripts.
"""
import os
import structlog
from typing import Dict, List, Optional, TypedDict
from functools import lru_cache

logger = structlog.get_logger(__name__)


class PromptInfo(TypedDict):
    """Structure for prompt metadata."""
    name: str
    category: str
    path: str
    content: Optional[str]


class PromptService:
    """
    Service to manage loading and caching of system prompts.

    Prompts are stored in the 'prompts' directory at the project root.
    This service provides methods to list available prompts and retrieve their content.
    """

    def __init__(self):
        # Find prompts directory relative to this file
        # Current: src/youtube_api/utils/prompt_service.py
        # Target: prompts/ (at project root)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up: utils -> youtube_api -> src -> root
        self.prompts_dir = os.path.abspath(os.path.join(current_dir, "../../../prompts"))

        self._cache: Dict[str, PromptInfo] = {}
        self._loaded = False

    def _load_prompts(self) -> None:
        """
        Scan the prompts directory and populate the cache.
        This is called lazily on the first request.
        """
        if self._loaded:
            return

        if not os.path.exists(self.prompts_dir):
            logger.warning("prompts_directory_not_found", path=self.prompts_dir)
            return

        logger.info("loading_prompts", path=self.prompts_dir)

        count = 0
        for root, dirs, files in os.walk(self.prompts_dir):
            for file in files:
                if file == "system.md":
                    # The parent folder name is the prompt name
                    prompt_name = os.path.basename(root)

                    # The grandparent folder is the category (if any)
                    rel_path = os.path.relpath(root, self.prompts_dir)
                    parts = rel_path.split(os.sep)

                    category = "uncategorized"
                    if len(parts) > 1:
                        category = parts[0]

                    full_path = os.path.join(root, file)

                    self._cache[prompt_name] = {
                        "name": prompt_name,
                        "category": category,
                        "path": full_path,
                        "content": None  # Content loaded on demand
                    }
                    count += 1

        self._loaded = True
        logger.info("prompts_loaded", count=count)

    def list_prompts(self) -> List[PromptInfo]:
        """Return a list of all available prompts (without content)."""
        self._load_prompts()
        # Return a list of dicts without the 'content' field to keep it light
        return [
            {k: v for k, v in p.items() if k != "content"}
            for p in self._cache.values()
        ]

    def get_prompt(self, name: str) -> Optional[str]:
        """
        Get the content of a specific prompt by name.
        Content is cached in memory after first read.
        """
        self._load_prompts()

        if name not in self._cache:
            return None

        prompt_info = self._cache[name]

        # Load content if not already in memory
        if prompt_info["content"] is None:
            try:
                with open(prompt_info["path"], "r", encoding="utf-8") as f:
                    prompt_info["content"] = f.read()
            except Exception as e:
                logger.error("error_reading_prompt", path=prompt_info["path"], error=str(e))
                return None

        return prompt_info["content"]

    def refresh(self) -> None:
        """Clear cache and reload prompts from disk."""
        self._cache = {}
        self._loaded = False
        self._load_prompts()

    def get_prompts_by_category(self, category: str) -> List[PromptInfo]:
        """Get all prompts in a specific category."""
        self._load_prompts()
        return [
            {k: v for k, v in p.items() if k != "content"}
            for p in self._cache.values()
            if p["category"] == category
        ]

    def get_categories(self) -> List[str]:
        """Get list of all prompt categories."""
        self._load_prompts()
        categories = set(p["category"] for p in self._cache.values())
        return sorted(list(categories))


# Singleton instance
_prompt_service: Optional[PromptService] = None


def get_prompt_service() -> PromptService:
    """Get the singleton PromptService instance."""
    global _prompt_service
    if _prompt_service is None:
        _prompt_service = PromptService()
    return _prompt_service
