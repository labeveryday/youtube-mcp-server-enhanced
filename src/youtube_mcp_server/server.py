"""MCP server implementation using FastMCP for YouTube data extraction."""

import logging
import sys
import os
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import time

from mcp.server.fastmcp import FastMCP
import mcp

from youtube_mcp_server.extractors import YouTubeExtractor
from youtube_mcp_server.models import VideoInfo, CommentThread, Transcript, ChannelInfo, PlaylistInfo
from youtube_mcp_server.utils.errors import YouTubeExtractorError, InvalidURLError
from youtube_mcp_server.utils.url_utils import is_valid_youtube_url, extract_video_id

# Version of this MCP server
__version__ = "0.1.0"

# Try to get MCP version
try:
    mcp_version = getattr(mcp, "__version__", "unknown")
except:
    mcp_version = "unknown"

# Configure logging to stderr only with color support
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m'    # Reset
    }
    
    def format(self, record):
        log_message = super().format(record)
        level_name = record.levelname
        if level_name in self.COLORS:
            return f"{self.COLORS[level_name]}{log_message}{self.COLORS['RESET']}"
        return log_message

# Set up logger
logger = logging.getLogger("youtube_mcp_server")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize FastMCP server with proper configuration
mcp = FastMCP(
    name="YouTube MCP Server Enhanced"
)

# Global extractor instance
extractor: Optional[YouTubeExtractor] = None

# Initialize extractor
async def initialize_extractor():
    """Initialize the YouTube extractor."""
    global extractor
    
    if extractor is not None:
        logger.debug("Extractor already initialized, reusing existing extractor")
        return
    
    logger.info("Initializing YouTube extractor...")
    
    # Initialize YouTube extractor with configurable options
    rate_limit = os.environ.get("YOUTUBE_RATE_LIMIT")
    max_retries = int(os.environ.get("YOUTUBE_MAX_RETRIES", "3"))
    retry_delay = float(os.environ.get("YOUTUBE_RETRY_DELAY", "1.0"))
    timeout = int(os.environ.get("YOUTUBE_TIMEOUT", "300"))
    enable_cache = os.environ.get("YOUTUBE_ENABLE_CACHE", "true").lower() == "true"
    cache_ttl = int(os.environ.get("YOUTUBE_CACHE_TTL", "3600"))
    
    extractor = YouTubeExtractor(
        rate_limit=rate_limit,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
        enable_cache=enable_cache,
        cache_ttl=cache_ttl
    )
    
    logger.info("✅ Successfully initialized YouTube extractor")
    logger.info(f"Configuration: retries={max_retries}, timeout={timeout}s, cache={'enabled' if enable_cache else 'disabled'}")

def validate_youtube_url(url: str) -> str:
    """Validate YouTube URL and raise appropriate errors."""
    if not url:
        raise InvalidURLError("URL is required")
    
    if not is_valid_youtube_url(url):
        raise InvalidURLError(f"Invalid YouTube URL: {url}")
    
    return url

# Prompts for common YouTube analysis tasks
@mcp.prompt("analyze-video")
async def analyze_video_prompt(
    url: str,
    include_comments: bool = False,
    include_transcript: bool = False,
    max_comments: int = 10
) -> Dict[str, Any]:
    """Comprehensive analysis of a YouTube video including metadata, engagement, and optional comments/transcript."""
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    try:
        # Get basic video info
        video_info = await extractor.get_video_info(url)
        
        result = {
            "video_info": {
                "title": video_info.metadata.title,
                "channel": video_info.metadata.uploader,
                "views": video_info.stats.view_count,
                "likes": video_info.stats.like_count,
                "comments": video_info.stats.comment_count,
                "duration": video_info.stats.duration_string,
                "upload_date": video_info.metadata.upload_date,
                "like_rate": f"{video_info.like_to_view_ratio:.3%}" if video_info.like_to_view_ratio else "N/A",
                "comment_rate": f"{video_info.comment_to_view_ratio:.3%}" if video_info.comment_to_view_ratio else "N/A"
            }
        }
        
        # Add comments if requested
        if include_comments:
            comments = await extractor.get_video_comments(url, max_comments)
            result["comments"] = [
                {
                    "author": thread.top_comment.author,
                    "text": thread.top_comment.text[:200] + "..." if len(thread.top_comment.text) > 200 else thread.top_comment.text,
                    "likes": thread.top_comment.like_count,
                    "replies": len(thread.replies)
                }
                for thread in comments[:max_comments]
            ]
        
        # Add transcript if requested
        if include_transcript:
            transcript = await extractor.get_video_transcript(url)
            if transcript:
                result["transcript"] = {
                    "language": transcript.language,
                    "auto_generated": transcript.is_auto_generated,
                    "entries_count": len(transcript.entries),
                    "full_text": transcript.full_text[:500] + "..." if len(transcript.full_text) > 500 else transcript.full_text
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        raise RuntimeError(f"Failed to analyze video: {str(e)}")

@mcp.prompt("compare-videos")
async def compare_videos_prompt(
    urls: List[str]
) -> Dict[str, Any]:
    """Compare engagement metrics across multiple YouTube videos."""
    global extractor
    if not extractor:
        await initialize_extractor()
    
    if len(urls) < 2:
        raise ValueError("At least 2 URLs are required for comparison")
    
    if len(urls) > 5:
        raise ValueError("Maximum 5 URLs allowed for comparison")
    
    results = []
    
    for url in urls:
        validate_youtube_url(url)
        try:
            video_info = await extractor.get_video_info(url)
            results.append({
                "url": url,
                "title": video_info.metadata.title,
                "channel": video_info.metadata.uploader,
                "views": video_info.stats.view_count,
                "likes": video_info.stats.like_count,
                "comments": video_info.stats.comment_count,
                "like_rate": video_info.like_to_view_ratio or 0,
                "comment_rate": video_info.comment_to_view_ratio or 0
            })
        except Exception as e:
            logger.warning(f"Failed to analyze {url}: {str(e)}")
            results.append({
                "url": url,
                "error": str(e)
            })
    
    # Sort by views for comparison
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        valid_results.sort(key=lambda x: x["views"], reverse=True)
    
    return {
        "comparison": valid_results,
        "summary": {
            "total_videos": len(valid_results),
            "highest_views": max(r["views"] for r in valid_results) if valid_results else 0,
            "average_like_rate": sum(r["like_rate"] for r in valid_results) / len(valid_results) if valid_results else 0
        }
    }

# Core YouTube extraction tools
@mcp.tool()
async def get_video_info(url: str) -> Dict[str, Any]:
    """Extract comprehensive information about a YouTube video including metadata, statistics, and engagement metrics.
    
    Args:
        url: YouTube video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
    
    Returns:
        Dictionary containing video information including title, channel, views, likes, comments, duration, and engagement rates
    
    Examples:
        - get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    try:
        video_info = await extractor.get_video_info(url)
        
        return {
            "metadata": {
                "id": video_info.metadata.id,
                "title": video_info.metadata.title,
                "description": video_info.metadata.description,
                "channel": video_info.metadata.uploader,
                "channel_id": video_info.metadata.uploader_id,
                "channel_url": video_info.metadata.uploader_url,
                "upload_date": video_info.metadata.upload_date,
                "tags": video_info.metadata.tags,
                "categories": video_info.metadata.categories,
                "thumbnail": video_info.metadata.thumbnail
            },
            "statistics": {
                "view_count": video_info.stats.view_count,
                "like_count": video_info.stats.like_count,
                "comment_count": video_info.stats.comment_count,
                "duration_seconds": video_info.stats.duration_seconds,
                "duration_string": video_info.stats.duration_string
            },
            "engagement": {
                "like_to_view_ratio": video_info.like_to_view_ratio,
                "comment_to_view_ratio": video_info.comment_to_view_ratio,
                "like_rate_percentage": f"{video_info.like_to_view_ratio * 100:.3f}%" if video_info.like_to_view_ratio else "N/A",
                "comment_rate_percentage": f"{video_info.comment_to_view_ratio * 100:.3f}%" if video_info.comment_to_view_ratio else "N/A"
            },
            "technical": {
                "age_limit": video_info.age_limit,
                "availability": video_info.availability,
                "live_status": video_info.live_status
            }
        }
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to extract video info: {str(e)}")

@mcp.tool()
async def get_video_comments(url: str, max_comments: int = 100) -> List[Dict[str, Any]]:
    """Extract comments from a YouTube video with optional limit.
    
    Args:
        url: YouTube video URL
        max_comments: Maximum number of comments to extract (default: 100, max: 1000)
    
    Returns:
        List of comment threads with author, text, likes, and replies
    
    Examples:
        - get_video_comments("https://www.youtube.com/watch?v=dQw4w9WgXcQ", max_comments=50)
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    if max_comments > 1000:
        max_comments = 1000
        logger.warning("Limited max_comments to 1000 for performance")
    
    try:
        comments = await extractor.get_video_comments(url, max_comments)
        
        return [
            {
                "id": thread.top_comment.id,
                "author": thread.top_comment.author,
                "author_id": thread.top_comment.author_id,
                "text": thread.top_comment.text,
                "like_count": thread.top_comment.like_count,
                "timestamp": thread.top_comment.timestamp,
                "is_pinned": thread.top_comment.is_pinned,
                "is_favorited": thread.top_comment.is_favorited,
                "reply_count": len(thread.replies),
                "replies": [
                    {
                        "id": reply.id,
                        "author": reply.author,
                        "text": reply.text,
                        "like_count": reply.like_count,
                        "timestamp": reply.timestamp
                    }
                    for reply in thread.replies[:3]  # Limit replies shown
                ] if thread.replies else []
            }
            for thread in comments
        ]
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to extract comments: {str(e)}")

@mcp.tool()
async def get_video_transcript(url: str) -> Optional[Dict[str, Any]]:
    """Extract transcript/subtitles from a YouTube video.
    
    Args:
        url: YouTube video URL
    
    Returns:
        Dictionary containing transcript information with timestamped entries, or None if no transcript available
    
    Examples:
        - get_video_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    try:
        transcript = await extractor.get_video_transcript(url)
        
        if not transcript:
            return None
        
        return {
            "video_id": transcript.video_id,
            "language": transcript.language,
            "is_auto_generated": transcript.is_auto_generated,
            "total_duration": transcript.total_duration,
            "entries_count": len(transcript.entries),
            "full_text": transcript.full_text,
            "entries": [
                {
                    "start_time": entry.start_time,
                    "end_time": entry.end_time,
                    "duration": entry.duration,
                    "text": entry.text,
                    "formatted_time": entry.formatted_time
                }
                for entry in transcript.entries
            ]
        }
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to extract transcript: {str(e)}")

@mcp.tool()
async def search_transcript(url: str, query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
    """Search for specific text within a video's transcript.
    
    Args:
        url: YouTube video URL
        query: Text to search for in the transcript
        case_sensitive: Whether search should be case sensitive (default: false)
    
    Returns:
        List of transcript entries containing the search query
    
    Examples:
        - search_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "never gonna")
        - search_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "NEVER", case_sensitive=True)
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    
    try:
        transcript = await extractor.get_video_transcript(url)
        
        if not transcript:
            return []
        
        results = transcript.search_text(query, case_sensitive)
        
        return [
            {
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "duration": entry.duration,
                "text": entry.text,
                "formatted_time": entry.formatted_time
            }
            for entry in results
        ]
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to search transcript: {str(e)}")

@mcp.tool()
async def analyze_video_engagement(url: str) -> Dict[str, Any]:
    """Analyze engagement metrics for a YouTube video with industry benchmarks.
    
    Args:
        url: YouTube video URL
    
    Returns:
        Dictionary containing engagement analysis with benchmarks and recommendations
    
    Examples:
        - analyze_video_engagement("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    try:
        video_info = await extractor.get_video_info(url)
        
        # Calculate engagement metrics
        views = video_info.stats.view_count
        likes = video_info.stats.like_count or 0
        comments = video_info.stats.comment_count or 0
        
        like_rate = (likes / views * 100) if views > 0 else 0
        comment_rate = (comments / views * 100) if views > 0 else 0
        
        # Engagement benchmarks (industry standards)
        def get_benchmark(rate: float, thresholds: List[float]) -> str:
            if rate > thresholds[0]:
                return "Excellent"
            elif rate > thresholds[1]:
                return "Good"
            elif rate > thresholds[2]:
                return "Average"
            else:
                return "Below Average"
        
        like_benchmark = get_benchmark(like_rate, [4.0, 2.0, 1.0])
        comment_benchmark = get_benchmark(comment_rate, [0.5, 0.2, 0.1])
        
        return {
            "video": {
                "title": video_info.metadata.title,
                "channel": video_info.metadata.uploader,
                "upload_date": video_info.metadata.upload_date
            },
            "raw_metrics": {
                "views": views,
                "likes": likes,
                "comments": comments,
                "total_engagement": likes + comments
            },
            "engagement_rates": {
                "like_rate": like_rate,
                "comment_rate": comment_rate,
                "total_engagement_rate": (likes + comments) / views * 100 if views > 0 else 0
            },
            "benchmarks": {
                "like_performance": like_benchmark,
                "comment_performance": comment_benchmark,
                "overall_assessment": "Excellent" if like_benchmark == "Excellent" and comment_benchmark in ["Excellent", "Good"] else "Good" if like_benchmark in ["Excellent", "Good"] or comment_benchmark in ["Excellent", "Good"] else "Average"
            },
            "insights": {
                "like_rate_vs_benchmark": f"Like rate of {like_rate:.3f}% is {like_benchmark.lower()}",
                "comment_rate_vs_benchmark": f"Comment rate of {comment_rate:.3f}% is {comment_benchmark.lower()}",
                "recommendations": [
                    "Consider analyzing top comments for audience feedback" if comment_rate > 0.2 else "Low comment engagement - consider asking questions to encourage discussion",
                    "Strong like engagement indicates good content reception" if like_rate > 2.0 else "Consider improving content quality or thumbnail/title optimization"
                ]
            }
        }
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to analyze engagement: {str(e)}")

@mcp.tool()
async def get_channel_info(url: str) -> Dict[str, Any]:
    """Extract information about a YouTube channel.
    
    Args:
        url: YouTube channel URL (e.g., https://www.youtube.com/@channelname)
    
    Returns:
        Dictionary containing channel information and statistics
    
    Examples:
        - get_channel_info("https://www.youtube.com/@RickAstleyYT")
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    try:
        channel_info = await extractor.get_channel_info(url)
        
        return {
            "id": channel_info.id,
            "name": channel_info.name,
            "url": channel_info.url,
            "description": channel_info.description,
            "avatar_url": channel_info.avatar_url,
            "banner_url": channel_info.banner_url,
            "verified": channel_info.verified,
            "country": channel_info.country,
            "language": channel_info.language,
            "tags": channel_info.tags,
            "statistics": {
                "subscriber_count": channel_info.stats.subscriber_count if channel_info.stats else None,
                "video_count": channel_info.stats.video_count if channel_info.stats else None,
                "view_count": channel_info.stats.view_count if channel_info.stats else None
            }
        }
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to extract channel info: {str(e)}")

@mcp.tool()
async def get_playlist_info(url: str) -> Dict[str, Any]:
    """Extract information about a YouTube playlist including all videos.
    
    Args:
        url: YouTube playlist URL
    
    Returns:
        Dictionary containing playlist information and video list
    
    Examples:
        - get_playlist_info("https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMZOz59Oq8HmPME")
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    validate_youtube_url(url)
    
    try:
        playlist_info = await extractor.get_playlist_info(url)
        
        return {
            "id": playlist_info.id,
            "title": playlist_info.title,
            "description": playlist_info.description,
            "uploader": playlist_info.uploader,
            "uploader_id": playlist_info.uploader_id,
            "video_count": playlist_info.video_count,
            "total_duration_seconds": playlist_info.total_duration,
            "total_duration_formatted": f"{playlist_info.total_duration // 3600}h {(playlist_info.total_duration % 3600) // 60}m",
            "total_views": playlist_info.total_views,
            "videos": [
                {
                    "video_id": video.video_id,
                    "title": video.title,
                    "uploader": video.uploader,
                    "duration": video.duration,
                    "view_count": video.view_count,
                    "playlist_index": video.playlist_index
                }
                for video in playlist_info.videos
            ]
        }
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to extract playlist info: {str(e)}")

@mcp.tool()
async def search_youtube(
    query: str, 
    search_type: str = "video",
    max_results: int = 20
) -> Dict[str, Any]:
    """Search YouTube for videos, channels, or playlists.
    
    Args:
        query: Search query string
        search_type: Type of search ("video", "channel", "playlist")
        max_results: Maximum number of results to return (max 50)
    
    Returns:
        Dictionary containing search results and metadata
    
    Examples:
        - search_youtube("Python programming tutorials", "video", 10)
        - search_youtube("Tech channels", "channel", 5)
        - search_youtube("Music playlists", "playlist", 15)
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    if not query.strip():
        raise RuntimeError("Search query is required")
    
    if search_type not in ["video", "channel", "playlist"]:
        raise RuntimeError("Search type must be 'video', 'channel', or 'playlist'")
    
    if max_results < 1 or max_results > 50:
        raise RuntimeError("Max results must be between 1 and 50")
    
    try:
        results = await extractor.search_youtube(query, search_type, max_results)
        
        return {
            "query": query,
            "search_type": search_type,
            "max_results": max_results,
            "result_count": len(results),
            "results": results
        }
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Search failed: {str(e)}")

@mcp.tool()
async def get_trending_videos(
    region: str = "US", 
    max_results: int = 20
) -> Dict[str, Any]:
    """Get trending videos for a specific region.
    
    Args:
        region: Country code (e.g., "US", "GB", "DE", "JP", "IN")
        max_results: Maximum number of results to return (max 50)
    
    Returns:
        Dictionary containing trending videos and metadata
    
    Examples:
        - get_trending_videos("US", 10)
        - get_trending_videos("GB", 20)
        - get_trending_videos("JP", 15)
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    if max_results < 1 or max_results > 50:
        raise RuntimeError("Max results must be between 1 and 50")
    
    try:
        results = await extractor.get_trending_videos(region, max_results)
        
        return {
            "region": region,
            "max_results": max_results,
            "result_count": len(results),
            "trending_videos": results
        }
        
    except YouTubeExtractorError as e:
        raise RuntimeError(f"Failed to get trending videos: {str(e)}")

@mcp.tool()
async def batch_extract_urls(
    urls: List[str], 
    extract_type: str = "video"
) -> Dict[str, Any]:
    """Extract information from multiple YouTube URLs concurrently.
    
    Args:
        urls: List of YouTube URLs to process
        extract_type: Type of extraction ("video", "channel", "playlist")
    
    Returns:
        Dictionary containing batch extraction results and metadata
    
    Examples:
        - batch_extract_urls(["https://youtube.com/watch?v=...", "https://youtube.com/watch?v=..."], "video")
        - batch_extract_urls(["https://youtube.com/@channel1", "https://youtube.com/@channel2"], "channel")
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    if not urls:
        raise RuntimeError("URL list cannot be empty")
    
    if len(urls) > 20:
        raise RuntimeError("Maximum 20 URLs allowed per batch request")
    
    if extract_type not in ["video", "channel", "playlist"]:
        raise RuntimeError("Extract type must be 'video', 'channel', or 'playlist'")
    
    # Validate all URLs
    validated_urls = []
    for url in urls:
        try:
            validated_urls.append(validate_youtube_url(url))
        except InvalidURLError as e:
            raise RuntimeError(f"Invalid URL in list: {url} - {str(e)}")
    
    try:
        results = await extractor.batch_extract(validated_urls, extract_type)
        
        return {
            "extract_type": extract_type,
            "total_urls": len(validated_urls),
            "successful_extractions": len(results),
            "failed_extractions": len(validated_urls) - len(results),
            "results": results
        }
        
    except Exception as e:
        raise RuntimeError(f"Batch extraction failed: {str(e)}")

@mcp.tool()
async def get_extractor_health() -> Dict[str, Any]:
    """Get the health status and configuration of the YouTube extractor.
    
    Returns:
        Dictionary containing extractor health information, configuration, and cache statistics
    
    Examples:
        - get_extractor_health()
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    try:
        health_status = extractor.get_health_status()
        cache_stats = extractor.get_cache_stats()
        
        return {
            "health": health_status,
            "cache": cache_stats,
            "server_version": __version__,
            "mcp_version": mcp_version
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "server_version": __version__,
            "mcp_version": mcp_version
        }

@mcp.tool()
async def clear_extractor_cache() -> Dict[str, Any]:
    """Clear all cached data from the extractor.
    
    Returns:
        Dictionary confirming cache clearance
    
    Examples:
        - clear_extractor_cache()
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    try:
        extractor.clear_cache()
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": str(time.time())
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to clear cache: {str(e)}")

@mcp.tool()
async def get_extractor_config() -> Dict[str, Any]:
    """Get the current configuration of the YouTube extractor.
    
    Returns:
        Dictionary containing extractor configuration parameters
    
    Examples:
        - get_extractor_config()
    """
    global extractor
    if not extractor:
        await initialize_extractor()
    
    try:
        health_status = extractor.get_health_status()
        
        return {
            "rate_limit": extractor.rate_limit,
            "max_retries": extractor.max_retries,
            "retry_delay": extractor.retry_delay,
            "timeout": extractor.timeout,
            "enable_cache": extractor.enable_cache,
            "cache_ttl": extractor.cache_ttl,
            "yt_dlp_version": health_status.get("yt_dlp_version"),
            "status": health_status.get("status")
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to get configuration: {str(e)}")

def run_server():
    """Run the MCP server."""
    # Print banner
    print("\n" + "=" * 70)
    print(f"  YouTube MCP Server Enhanced v{__version__}")
    print(f"  MCP Version: {mcp_version}")
    print("=" * 70)
    print("  🎥 Comprehensive YouTube data extraction")
    print("  📊 Video analytics and engagement metrics")
    print("  💬 Comment extraction and analysis")
    print("  📝 Transcript processing and search")
    print("  📺 Channel and playlist information")
    print("  🔍 YouTube search functionality")
    print("  📈 Trending videos by region")
    print("  ⚡ Batch processing and concurrent extraction")
    print("  💾 Intelligent caching with TTL")
    print("  🔄 Automatic retry with exponential backoff")
    print("  📊 Health monitoring and configuration")
    print("=" * 70)
    print("  Available Tools:")
    print("  • get_video_info() - Extract video metadata and stats")
    print("  • get_video_comments() - Extract video comments")
    print("  • get_video_transcript() - Extract video transcripts")
    print("  • get_channel_info() - Extract channel information")
    print("  • get_playlist_info() - Extract playlist details")
    print("  • search_youtube() - Search videos/channels/playlists")
    print("  • get_trending_videos() - Get trending videos by region")
    print("  • batch_extract_urls() - Process multiple URLs concurrently")
    print("  • get_extractor_health() - Monitor extractor health")
    print("  • get_extractor_config() - View current configuration")
    print("  • clear_extractor_cache() - Clear cached data")
    print("=" * 70)
    print("  Server starting...")
    print("=" * 70 + "\n")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    run_server()
