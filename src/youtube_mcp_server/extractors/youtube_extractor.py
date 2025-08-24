"""
Main YouTube data extractor using yt-dlp.

This module provides a comprehensive interface for extracting various types
of data from YouTube videos, channels, and playlists.
"""

import json
import subprocess
import tempfile
import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from functools import lru_cache
import logging

from ..models import (
    VideoInfo, 
    ChannelInfo, 
    ChannelStats,
    CommentThread, 
    Comment,
    Transcript, 
    TranscriptEntry,
    PlaylistInfo,
    PlaylistItem
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeExtractorError(Exception):
    """Base exception for YouTube extractor errors."""
    pass


class YouTubeExtractor:
    """
    Comprehensive YouTube data extractor using yt-dlp.
    
    This class provides methods to extract video metadata, comments,
    transcripts, channel information, and playlist data from YouTube.
    """
    
    def __init__(
        self, 
        rate_limit: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: int = 300,
        enable_cache: bool = True,
        cache_ttl: int = 3600
    ):
        """
        Initialize the YouTube extractor.
        
        Args:
            rate_limit: Rate limit for requests (e.g., "1M" for 1MB/s)
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Delay between retries in seconds
            timeout: Timeout for yt-dlp operations in seconds
            enable_cache: Whether to enable result caching
            cache_ttl: Cache TTL in seconds
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        
        self._base_cmd = ["yt-dlp"]
        
        if rate_limit:
            self._base_cmd.extend(["--limit-rate", rate_limit])
        
        # Verify yt-dlp is available
        self._verify_yt_dlp()
    
    def _verify_yt_dlp(self) -> None:
        """Verify that yt-dlp is available and working."""
        try:
            result = subprocess.run(
                self._base_cmd + ["--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise YouTubeExtractorError("yt-dlp is not working properly")
            logger.info(f"yt-dlp version: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise YouTubeExtractorError("yt-dlp is not installed or not in PATH")
    
    def _run_yt_dlp_with_retry(self, url: str, options: List[str]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Run yt-dlp with retry logic for failed requests.
        
        Args:
            url: YouTube URL to process
            options: Additional yt-dlp options
            
        Returns:
            Parsed JSON data from yt-dlp
            
        Raises:
            YouTubeExtractorError: If extraction fails after all retries
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return self._run_yt_dlp(url, options)
            except YouTubeExtractorError as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}. Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    # Exponential backoff
                    self.retry_delay *= 2
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed for {url}")
                    break
        
        raise YouTubeExtractorError(f"Failed to extract data from {url} after {self.max_retries + 1} attempts: {last_error}")
    
    def _run_yt_dlp(self, url: str, options: List[str]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Run yt-dlp with specified options and return parsed JSON.
        
        Args:
            url: YouTube URL to process
            options: Additional yt-dlp options
            
        Returns:
            Parsed JSON data from yt-dlp (dict for single item, list for multiple items)
            
        Raises:
            YouTubeExtractorError: If extraction fails
        """
        cmd = self._base_cmd + options + [url]
        
        try:
            logger.debug(f"Running yt-dlp: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=self.timeout
            )
            
            if result.stdout.strip():
                # Handle multiple JSON lines (one per line)
                lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                
                if len(lines) == 1:
                    # Single JSON object
                    return json.loads(lines[0])
                else:
                    # Multiple JSON objects (one per line)
                    return [json.loads(line) for line in lines]
            else:
                raise YouTubeExtractorError("No data returned from yt-dlp")
                
        except subprocess.CalledProcessError as e:
            error_msg = f"yt-dlp failed: {e.stderr}"
            logger.error(f"yt-dlp error for {url}: {error_msg}")
            raise YouTubeExtractorError(error_msg) from e
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp timeout for {url}")
            raise YouTubeExtractorError("Extraction timed out")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {url}: {e}")
            raise YouTubeExtractorError(f"Failed to parse JSON: {e}") from e
    
    @lru_cache(maxsize=100)
    def _get_cached_data(self, cache_key: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """Get cached data if available and not expired."""
        if not self.enable_cache:
            return None
        
        # Simple in-memory cache with TTL
        # In production, consider using Redis or similar
        current_time = time.time()
        if hasattr(self, '_cache') and cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if current_time - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for {cache_key}")
                return data
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
        
        return None
    
    def _set_cached_data(self, cache_key: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """Cache data with timestamp."""
        if not self.enable_cache:
            return
        
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        self._cache[cache_key] = (data, time.time())
        logger.debug(f"Cached data for {cache_key}")
    
    async def get_video_info(self, url: str) -> VideoInfo:
        """
        Extract comprehensive video information.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoInfo object with metadata and statistics
        """
        cache_key = f"video_info:{url}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return VideoInfo.from_yt_dlp_data(cached_data)
        
        options = ["--dump-json", "--no-download"]
        data = self._run_yt_dlp_with_retry(url, options)
        
        # Cache the result
        self._set_cached_data(cache_key, data)
        
        return VideoInfo.from_yt_dlp_data(data)
    
    async def get_playlist_info(self, url: str) -> PlaylistInfo:
        """
        Extract playlist information.
        
        Args:
            url: YouTube playlist URL
            
        Returns:
            PlaylistInfo object
        """
        cache_key = f"playlist_info:{url}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return PlaylistInfo.from_yt_dlp_data(cached_data)
        
        options = ["--dump-json", "--no-download", "--flat-playlist"]
        data = self._run_yt_dlp_with_retry(url, options)
        
        # Handle both single video and playlist responses
        if isinstance(data, list):
            # Multiple videos in playlist
            videos = []
            for i, video_data in enumerate(data, 1):
                video = PlaylistItem(
                    video_id=video_data.get("id", ""),
                    title=video_data.get("title", ""),
                    uploader=video_data.get("uploader", ""),
                    duration=video_data.get("duration"),
                    view_count=video_data.get("view_count"),
                    playlist_index=i
                )
                videos.append(video)
            
            # Use first video's playlist info
            first_video = data[0] if data else {}
            playlist_info = PlaylistInfo(
                id=first_video.get("playlist_id", ""),
                title=first_video.get("playlist_title", ""),
                uploader=first_video.get("playlist_uploader", ""),
                uploader_id=first_video.get("playlist_uploader_id", ""),
                video_count=len(videos),
                videos=videos
            )
            
            # Cache the result
            self._set_cached_data(cache_key, data)
            return playlist_info
        else:
            # Single video
            video = PlaylistItem(
                video_id=data.get("id", ""),
                title=data.get("title", ""),
                uploader=data.get("uploader", ""),
                duration=data.get("duration"),
                view_count=data.get("view_count"),
                playlist_index=1
            )
            
            playlist_info = PlaylistInfo(
                id=data.get("playlist_id", ""),
                title=data.get("playlist_title", data.get("title", "")),
                uploader=data.get("uploader", ""),
                uploader_id=data.get("uploader_id", ""),
                video_count=1,
                videos=[video]
            )
            
            # Cache the result
            self._set_cached_data(cache_key, data)
            return playlist_info
    
    async def get_video_comments(
        self, 
        url: str, 
        max_comments: Optional[int] = None
    ) -> List[CommentThread]:
        """
        Extract video comments.
        
        Args:
            url: YouTube video URL
            max_comments: Maximum number of comments to extract (note: yt-dlp doesn't support limiting)
            
        Returns:
            List of comment threads
        """
        cache_key = f"comments:{url}:{max_comments or 'all'}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        options = ["--write-comments", "--skip-download", "--dump-json"]
        
        # Note: yt-dlp doesn't have --max-comments option
        # We'll limit the results after extraction if needed
        
        # Use temporary directory for comment files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "comments"
            options.extend(["--output", str(temp_path) + ".%(ext)s"])
            
            # Run extraction
            self._run_yt_dlp_with_retry(url, options)
            
            # Look for comment files
            comment_files = list(Path(temp_dir).glob("*.info.json"))
            
            if not comment_files:
                return []
            
            # Parse comment data
            comments = []
            for comment_file in comment_files:
                with open(comment_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    comments.extend(self._parse_comments(data))
            
            # Limit results if requested
            if max_comments and len(comments) > max_comments:
                comments = comments[:max_comments]
            
            # Cache the result
            self._set_cached_data(cache_key, comments)
            return comments
    
    def _parse_comments(self, data: Dict[str, Any]) -> List[CommentThread]:
        """Parse comment data from yt-dlp output."""
        threads = []
        
        comment_data = data.get("comments", [])
        
        for comment_info in comment_data:
            # Create main comment
            main_comment = Comment(
                id=comment_info.get("id", ""),
                text=comment_info.get("text", ""),
                author=comment_info.get("author", ""),
                author_id=comment_info.get("author_id"),
                like_count=comment_info.get("like_count", 0),
                timestamp=comment_info.get("timestamp"),
                is_pinned=comment_info.get("is_pinned", False),
                is_favorited=comment_info.get("is_favorited", False)
            )
            
            # Parse replies
            replies = []
            for reply_info in comment_info.get("replies", []):
                reply = Comment(
                    id=reply_info.get("id", ""),
                    text=reply_info.get("text", ""),
                    author=reply_info.get("author", ""),
                    author_id=reply_info.get("author_id"),
                    like_count=reply_info.get("like_count", 0),
                    timestamp=reply_info.get("timestamp"),
                    parent_id=main_comment.id
                )
                replies.append(reply)
            
            thread = CommentThread(
                top_comment=main_comment,
                replies=replies,
                total_reply_count=len(replies)
            )
            threads.append(thread)
        
        return threads
    
    async def get_video_transcript(self, url: str) -> Optional[Transcript]:
        """
        Extract video transcript/subtitles.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Transcript object or None if no transcript available
        """
        cache_key = f"transcript:{url}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        options = [
            "--write-subs", 
            "--write-auto-subs", 
            "--skip-download",
            "--sub-format", "json3"
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "transcript"
            options.extend(["--output", str(temp_path) + ".%(ext)s"])
            
            try:
                self._run_yt_dlp_with_retry(url, options)
                
                # Look for subtitle files
                sub_files = list(Path(temp_dir).glob("*.json3"))
                
                if not sub_files:
                    return None
                
                # Parse the first available subtitle file
                with open(sub_files[0], 'r', encoding='utf-8') as f:
                    sub_data = json.load(f)
                
                transcript = self._parse_transcript(sub_data, url)
                
                # Cache the result
                self._set_cached_data(cache_key, transcript)
                return transcript
                
            except YouTubeExtractorError:
                return None
    
    def _parse_transcript(self, data: Dict[str, Any], url: str) -> Transcript:
        """Parse transcript data from yt-dlp subtitle output."""
        entries = []
        
        for event in data.get("events", []):
            if "segs" in event:
                start_time = event.get("tStartMs", 0) / 1000.0
                duration = event.get("dDurationMs", 0) / 1000.0
                
                text_parts = []
                for seg in event["segs"]:
                    if "utf8" in seg:
                        text_parts.append(seg["utf8"])
                
                if text_parts:
                    entry = TranscriptEntry(
                        start_time=start_time,
                        end_time=start_time + duration,
                        text="".join(text_parts).strip(),
                        duration=duration
                    )
                    entries.append(entry)
        
        # Extract video ID from URL
        video_id = self._extract_video_id(url)
        
        return Transcript(
            video_id=video_id,
            language="en",  # Default, could be detected from filename
            is_auto_generated=True,  # Assume auto-generated for now
            entries=entries
        )
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        else:
            return "unknown"
    
    async def get_channel_info(self, url: str) -> ChannelInfo:
        """
        Extract channel information.
        
        Args:
            url: YouTube channel URL
            
        Returns:
            ChannelInfo object
        """
        cache_key = f"channel_info:{url}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return ChannelInfo.from_yt_dlp_data(cached_data)
        
        # First try to get actual channel info (not playlist data)
        options = ["--dump-json", "--no-download"]
        
        try:
            data = self._run_yt_dlp_with_retry(url, options)
            
            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                # Channel with videos - use first video's channel info
                video_data = data[0]
                
                # Extract channel info from video data
                channel_id = video_data.get("uploader_id", video_data.get("channel_id", ""))
                channel_name = video_data.get("uploader", video_data.get("channel", ""))
                channel_url = video_data.get("uploader_url", video_data.get("channel_url", ""))
                
                # Get actual channel statistics if available
                stats = None
                if video_data.get("channel_follower_count") is not None:
                    stats = ChannelStats(
                        subscriber_count=video_data.get("channel_follower_count"),
                        video_count=video_data.get("playlist_count", 0),
                        view_count=None  # Will calculate below
                    )
                elif video_data.get("playlist_count") is not None:
                    # Create stats with just video count if subscriber count not available
                    stats = ChannelStats(
                        subscriber_count=None,
                        video_count=video_data.get("playlist_count", 0),
                        view_count=None  # Will calculate below
                    )
                
                # Calculate channel view count by summing recent video views
                channel_view_count = await self._calculate_channel_view_count(url)
                if stats:
                    stats.view_count = channel_view_count
                
                channel_info = ChannelInfo(
                    id=channel_id,
                    name=channel_name,
                    url=channel_url,
                    description=video_data.get("description", ""),
                    avatar_url=video_data.get("uploader_avatar", ""),
                    banner_url=video_data.get("uploader_banner", ""),
                    verified=bool(video_data.get("channel_is_verified", False)),
                    country=video_data.get("uploader_country", ""),
                    language=video_data.get("uploader_language", ""),
                    tags=video_data.get("uploader_tags", []),
                    stats=stats
                )
                
                # Cache the result
                self._set_cached_data(cache_key, data)
                return channel_info
            else:
                # Direct channel info
                channel_data = data
                
                stats = None
                if channel_data.get("channel_follower_count") is not None:
                    stats = ChannelStats(
                        subscriber_count=channel_data.get("channel_follower_count"),
                        video_count=channel_data.get("video_count"),
                        view_count=None  # Will calculate below
                    )
                
                # Calculate channel view count
                channel_view_count = await self._calculate_channel_view_count(url)
                if stats:
                    stats.view_count = channel_view_count
                
                channel_info = ChannelInfo(
                    id=channel_data.get("uploader_id", channel_data.get("channel_id", "")),
                    name=channel_data.get("uploader", channel_data.get("channel", "")),
                    url=channel_data.get("uploader_url", channel_data.get("channel_url", "")),
                    description=channel_data.get("description", ""),
                    avatar_url=channel_data.get("uploader_avatar", channel_data.get("channel_avatar", "")),
                    banner_url=channel_data.get("uploader_banner", channel_data.get("channel_banner", "")),
                    verified=bool(channel_data.get("uploader_verified", False)),
                    country=channel_data.get("uploader_country", channel_data.get("channel_country", "")),
                    language=channel_data.get("uploader_language", channel_data.get("channel_language", "")),
                    tags=channel_data.get("uploader_tags", channel_data.get("channel_tags", [])),
                    stats=stats
                )
                
                # Cache the result
                self._set_cached_data(cache_key, data)
                return channel_info
            
        except YouTubeExtractorError:
            # Fallback: try to get basic channel info from a video on the channel
            # This is a workaround for channels that don't return metadata directly
            try:
                # Get the channel's uploads playlist or recent videos
                uploads_url = url.rstrip('/') + '/videos'
                options = ["--dump-json", "--no-download", "--flat-playlist", "--playlist-items", "1"]
                data = self._run_yt_dlp_with_retry(uploads_url, options)
                
                if isinstance(data, list) and len(data) > 0:
                    video_data = data[0]
                    
                    stats = None
                    if video_data.get("subscriber_count") is not None:
                        stats = ChannelStats(
                            subscriber_count=video_data.get("subscriber_count"),
                            video_count=video_data.get("video_count"),
                            view_count=None  # Will calculate below
                        )
                    
                    # Calculate channel view count
                    channel_view_count = await self._calculate_channel_view_count(url)
                    if stats:
                        stats.view_count = channel_view_count
                    
                    channel_info = ChannelInfo(
                        id=video_data.get("uploader_id", ""),
                        name=video_data.get("uploader", ""),
                        url=video_data.get("uploader_url", ""),
                        description=video_data.get("description", ""),
                        avatar_url=video_data.get("uploader_avatar", ""),
                        banner_url=video_data.get("uploader_banner", ""),
                        verified=bool(video_data.get("uploader_verified", False)),
                        country=video_data.get("uploader_country", ""),
                        language=video_data.get("uploader_language", ""),
                        tags=video_data.get("uploader_tags", []),
                        stats=stats
                    )
                    
                    # Cache the result
                    self._set_cached_data(cache_key, data)
                    return channel_info
                else:
                    raise YouTubeExtractorError("Could not extract channel information")
                    
            except Exception as e:
                raise YouTubeExtractorError(f"Failed to extract channel info: {str(e)}")
    
    async def _calculate_channel_view_count(self, channel_url: str) -> Optional[int]:
        """
        Calculate total channel view count by summing recent video views.
        
        Args:
            channel_url: YouTube channel URL
            
        Returns:
            Total channel view count or None if calculation fails
        """
        try:
            # Get recent videos from the channel (limit to first 50 for performance)
            videos_url = channel_url.rstrip('/') + '/videos'
            options = ["--dump-json", "--no-download", "--flat-playlist", "--playlist-items", "50"]
            
            data = self._run_yt_dlp_with_retry(videos_url, options)
            
            if isinstance(data, list) and len(data) > 0:
                total_views = 0
                valid_videos = 0
                
                for video in data:
                    view_count = video.get("view_count")
                    if view_count is not None and isinstance(view_count, (int, float)):
                        total_views += int(view_count)
                        valid_videos += 1
                
                # Return total if we have valid data
                if valid_videos > 0:
                    return total_views
                    
            return None
            
        except Exception:
            # If calculation fails, return None
            return None
    
    async def search_youtube(
        self, 
        query: str, 
        search_type: str = "video",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos, channels, or playlists.
        
        Args:
            query: Search query string
            search_type: Type of search ("video", "channel", "playlist")
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        cache_key = f"search:{query}:{search_type}:{max_results}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        # Construct search URL
        search_url = f"ytsearch{max_results}:{query}"
        
        options = ["--dump-json", "--no-download", "--flat-playlist"]
        
        try:
            data = self._run_yt_dlp_with_retry(search_url, options)
            
            if isinstance(data, list):
                # Filter by type if specified
                if search_type != "video":
                    filtered_data = []
                    for item in data:
                        if search_type == "channel" and item.get("uploader_url"):
                            filtered_data.append(item)
                        elif search_type == "playlist" and item.get("playlist_id"):
                            filtered_data.append(item)
                        elif search_type == "video" and item.get("id"):
                            filtered_data.append(item)
                    data = filtered_data
                
                # Cache the result
                self._set_cached_data(cache_key, data)
                return data
            else:
                return [data] if data else []
                
        except YouTubeExtractorError:
            logger.error(f"Search failed for query: {query}")
            return []
    
    async def get_trending_videos(self, region: str = "US", max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Get trending videos for a specific region.
        
        Args:
            region: Country code (e.g., "US", "GB", "DE")
            max_results: Maximum number of results to return
            
        Returns:
            List of trending videos
        """
        cache_key = f"trending:{region}:{max_results}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        # Use trending URL for the region
        trending_url = f"https://www.youtube.com/feed/trending?gl={region}"
        options = ["--dump-json", "--no-download", "--flat-playlist", "--playlist-items", str(max_results)]
        
        try:
            data = self._run_yt_dlp_with_retry(trending_url, options)
            
            if isinstance(data, list):
                # Cache the result
                self._set_cached_data(cache_key, data)
                return data
            else:
                return [data] if data else []
                
        except YouTubeExtractorError:
            logger.error(f"Failed to get trending videos for region: {region}")
            return []
    
    async def batch_extract(
        self, 
        urls: List[str], 
        extract_type: str = "video"
    ) -> List[Union[VideoInfo, ChannelInfo, PlaylistInfo]]:
        """
        Extract information from multiple URLs concurrently.
        
        Args:
            urls: List of YouTube URLs
            extract_type: Type of extraction ("video", "channel", "playlist")
            
        Returns:
            List of extracted information objects
        """
        tasks = []
        
        for url in urls:
            if extract_type == "video":
                task = self.get_video_info(url)
            elif extract_type == "channel":
                task = self.get_channel_info(url)
            elif extract_type == "playlist":
                task = self.get_playlist_info(url)
            else:
                continue
            
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to extract from {urls[i]}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the extractor.
        
        Returns:
            Dictionary with health information
        """
        try:
            # Check yt-dlp availability
            version_result = subprocess.run(
                self._base_cmd + ["--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            yt_dlp_healthy = version_result.returncode == 0
            
            # Check cache status
            cache_info = {
                "enabled": self.enable_cache,
                "size": len(getattr(self, '_cache', {})),
                "ttl": self.cache_ttl
            }
            
            return {
                "status": "healthy" if yt_dlp_healthy else "unhealthy",
                "yt_dlp_available": yt_dlp_healthy,
                "yt_dlp_version": version_result.stdout.strip() if yt_dlp_healthy else None,
                "cache": cache_info,
                "config": {
                    "rate_limit": self.rate_limit,
                    "max_retries": self.max_retries,
                    "timeout": self.timeout
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "yt_dlp_available": False
            }

    def clear_cache(self) -> None:
        """Clear all cached data."""
        if hasattr(self, '_cache'):
            self._cache.clear()
            logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not hasattr(self, '_cache'):
            return {"enabled": False, "size": 0, "ttl": self.cache_ttl}
        
        cache_size = len(self._cache)
        cache_keys = list(self._cache.keys())
        
        return {
            "enabled": self.enable_cache,
            "size": cache_size,
            "ttl": self.cache_ttl,
            "keys": cache_keys[:10],  # Show first 10 keys
            "total_keys": len(cache_keys)
        }
