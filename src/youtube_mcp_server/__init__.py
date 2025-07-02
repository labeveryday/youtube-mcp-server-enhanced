"""
YouTube MCP Server Enhanced

A comprehensive Model Context Protocol server for YouTube data extraction.
Provides tools for extracting video metadata, comments, transcripts, and more.

Features:
- Video information extraction (metadata, statistics, engagement metrics)
- Comment extraction with threading support
- Transcript/subtitle extraction and search
- Channel information extraction
- Playlist analysis
- Engagement analysis and benchmarking

Usage:
    Run as MCP server: python -m youtube_mcp_server.server
    Or use programmatically: from youtube_mcp_server import YouTubeExtractor
"""

from .extractors import YouTubeExtractor
from .models import (
    VideoInfo,
    VideoStats,
    VideoMetadata,
    ChannelInfo,
    CommentThread,
    Comment,
    Transcript,
    TranscriptEntry,
    PlaylistInfo,
    PlaylistItem,
)

__version__ = "0.1.0"
__author__ = "Du'An Lightfoot"
__email__ = "duanlig@amazon.com"

__all__ = [
    "YouTubeExtractor",
    "VideoInfo",
    "VideoStats", 
    "VideoMetadata",
    "ChannelInfo",
    "CommentThread",
    "Comment",
    "Transcript",
    "TranscriptEntry",
    "PlaylistInfo",
    "PlaylistItem",
]
