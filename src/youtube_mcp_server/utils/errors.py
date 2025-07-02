"""Custom exceptions for the YouTube MCP server."""


class YouTubeExtractorError(Exception):
    """Base exception for YouTube extractor errors."""
    pass


class InvalidURLError(YouTubeExtractorError):
    """Raised when an invalid YouTube URL is provided."""
    pass


class VideoNotFoundError(YouTubeExtractorError):
    """Raised when a YouTube video is not found or not accessible."""
    pass


class TranscriptNotAvailableError(YouTubeExtractorError):
    """Raised when transcript/subtitles are not available for a video."""
    pass


class CommentsDisabledError(YouTubeExtractorError):
    """Raised when comments are disabled for a video."""
    pass


class RateLimitError(YouTubeExtractorError):
    """Raised when rate limiting is encountered."""
    pass


class ConfigurationError(YouTubeExtractorError):
    """Raised when there's a configuration issue."""
    pass
