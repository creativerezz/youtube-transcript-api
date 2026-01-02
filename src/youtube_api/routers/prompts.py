"""
Prompt template management endpoints.

Provides endpoints to list, retrieve, and manage Fabric-style pattern templates.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
import structlog

from ..utils.prompt_service import get_prompt_service, PromptInfo

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/prompts",
    tags=["prompts"],
)


@router.get(
    "/",
    summary="List all available prompts",
    response_description="A list of all available pattern templates",
    response_model=Dict[str, Any],
)
async def list_prompts():
    """
    List all available pattern templates.

    Returns a categorized list of all prompt templates without their full content
    to keep the response lightweight.

    Example response:
    ```json
    {
      "total": 30,
      "categories": ["extraction", "business", "development", ...],
      "prompts": [
        {
          "name": "extract_ideas",
          "category": "extraction",
          "path": "/path/to/prompt"
        },
        ...
      ]
    }
    ```
    """
    service = get_prompt_service()
    prompts = service.list_prompts()
    categories = service.get_categories()

    logger.info("prompts_listed", total=len(prompts), categories=len(categories))

    return {
        "total": len(prompts),
        "categories": categories,
        "prompts": prompts,
    }


@router.get(
    "/categories",
    summary="List prompt categories",
    response_description="List of all prompt categories",
)
async def list_categories() -> Dict[str, Any]:
    """
    Get a list of all prompt categories with counts.

    Returns:
        Dictionary with category names and prompt counts
    """
    service = get_prompt_service()
    prompts = service.list_prompts()
    categories = service.get_categories()

    # Count prompts per category
    category_counts = {}
    for prompt in prompts:
        cat = prompt.get("category", "uncategorized")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "categories": categories,
        "counts": category_counts,
        "total_categories": len(categories),
    }


@router.get(
    "/category/{category}",
    summary="Get prompts by category",
    response_description="List of prompts in the specified category",
)
async def get_prompts_by_category(category: str) -> Dict[str, Any]:
    """
    Get all prompts in a specific category.

    Args:
        category: Category name (e.g., "extraction", "business", "development")
    """
    service = get_prompt_service()
    prompts = service.get_prompts_by_category(category)

    if not prompts:
        raise HTTPException(
            status_code=404,
            detail=f"No prompts found in category '{category}'"
        )

    return {
        "category": category,
        "count": len(prompts),
        "prompts": prompts,
    }


@router.get(
    "/{name}",
    summary="Get prompt content",
    response_description="The full content of the requested prompt template",
)
async def get_prompt(name: str) -> Dict[str, Any]:
    """
    Get the full content of a specific prompt template.

    Args:
        name: The name of the prompt (folder name), e.g., 'extract_ideas', 'create_summary'

    Returns:
        Prompt metadata and full content
    """
    service = get_prompt_service()
    content = service.get_prompt(name)

    if content is None:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt '{name}' not found"
        )

    # Get prompt metadata
    prompts = service.list_prompts()
    metadata = next((p for p in prompts if p["name"] == name), {})

    logger.info("prompt_retrieved", name=name, category=metadata.get("category"))

    return {
        "name": name,
        "category": metadata.get("category", "unknown"),
        "content": content,
    }


@router.post(
    "/refresh",
    summary="Refresh prompt cache",
    response_description="Confirmation that the cache has been cleared and reloaded",
)
async def refresh_prompts() -> Dict[str, Any]:
    """
    Force a refresh of the prompt cache.

    Useful if you've added new prompts to the filesystem without restarting the server.
    """
    service = get_prompt_service()
    service.refresh()

    prompts = service.list_prompts()
    logger.info("prompts_refreshed", count=len(prompts))

    return {
        "message": "Prompt cache refreshed successfully",
        "total_prompts": len(prompts),
    }
