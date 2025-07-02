"""
YouTube data extractors using yt-dlp.

This module provides high-level extractors for different types of YouTube content.
All extractors are built on top of yt-dlp for reliable data extraction.
"""

from .youtube_extractor import YouTubeExtractor

__all__ = ["YouTubeExtractor"]
