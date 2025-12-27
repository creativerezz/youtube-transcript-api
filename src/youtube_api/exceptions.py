"""Custom exceptions for YouTube API Server."""

from fastapi import HTTPException, status


class YouTubeAPIError(Exception):
    """Base exception for YouTube API errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(status_code=self.status_code, detail=self.message)


class VideoNotFoundError(YouTubeAPIError):
    """Video not found or unavailable."""

    def __init__(self, video_id: str = None):
        message = f"Video not found: {video_id}" if video_id else "Video not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class InvalidURLError(YouTubeAPIError):
    """Invalid YouTube URL provided."""

    def __init__(self, url: str = None):
        message = f"Invalid YouTube URL: {url}" if url else "Invalid YouTube URL"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class TranscriptNotFoundError(YouTubeAPIError):
    """No transcript available for video."""

    def __init__(self, video_id: str = None, languages: list = None):
        if languages:
            message = f"No transcript found for video {video_id} in languages: {languages}"
        elif video_id:
            message = f"No transcript found for video: {video_id}"
        else:
            message = "No transcript found for video"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class RateLimitError(YouTubeAPIError):
    """Rate limited by YouTube or API."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class AIServiceUnavailableError(YouTubeAPIError):
    """AI service (Anthropic) is not configured or unavailable."""

    def __init__(
        self,
        message: str = "AI features not available. Please configure ANTHROPIC_API_KEY.",
    ):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)


class CacheError(YouTubeAPIError):
    """Error with cache operations."""

    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProxyError(YouTubeAPIError):
    """Error with proxy configuration or connection."""

    def __init__(self, message: str = "Proxy connection failed"):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)
