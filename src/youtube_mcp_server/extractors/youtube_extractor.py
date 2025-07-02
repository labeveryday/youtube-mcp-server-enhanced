"""
Main YouTube data extractor using yt-dlp.

This module provides a comprehensive interface for extracting various types
of data from YouTube videos, channels, and playlists.
"""

import json
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

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


class YouTubeExtractorError(Exception):
    """Base exception for YouTube extractor errors."""
    pass


class YouTubeExtractor:
    """
    Comprehensive YouTube data extractor using yt-dlp.
    
    This class provides methods to extract video metadata, comments,
    transcripts, channel information, and playlist data from YouTube.
    """
    
    def __init__(self, rate_limit: Optional[str] = None):
        """
        Initialize the YouTube extractor.
        
        Args:
            rate_limit: Rate limit for requests (e.g., "1M" for 1MB/s)
        """
        self.rate_limit = rate_limit
        self._base_cmd = ["yt-dlp"]
        
        if rate_limit:
            self._base_cmd.extend(["--limit-rate", rate_limit])
    
    def _run_yt_dlp(self, url: str, options: List[str]) -> Dict[str, Any]:
        """
        Run yt-dlp with specified options and return parsed JSON.
        
        Args:
            url: YouTube URL to process
            options: Additional yt-dlp options
            
        Returns:
            Parsed JSON data from yt-dlp
            
        Raises:
            YouTubeExtractorError: If extraction fails
        """
        cmd = self._base_cmd + options + [url]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.stdout.strip():
                return json.loads(result.stdout)
            else:
                raise YouTubeExtractorError("No data returned from yt-dlp")
                
        except subprocess.CalledProcessError as e:
            error_msg = f"yt-dlp failed: {e.stderr}"
            raise YouTubeExtractorError(error_msg) from e
        except subprocess.TimeoutExpired:
            raise YouTubeExtractorError("Extraction timed out")
        except json.JSONDecodeError as e:
            raise YouTubeExtractorError(f"Failed to parse JSON: {e}") from e
    
    async def get_video_info(self, url: str) -> VideoInfo:
        """
        Extract comprehensive video information.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoInfo object with metadata and statistics
        """
        options = ["--dump-json", "--no-download"]
        data = self._run_yt_dlp(url, options)
        return VideoInfo.from_yt_dlp_data(data)
    
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
        options = ["--write-comments", "--skip-download", "--dump-json"]
        
        # Note: yt-dlp doesn't have --max-comments option
        # We'll limit the results after extraction if needed
        
        # Use temporary directory for comment files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "comments"
            options.extend(["--output", str(temp_path) + ".%(ext)s"])
            
            # Run extraction
            self._run_yt_dlp(url, options)
            
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
                self._run_yt_dlp(url, options)
                
                # Look for subtitle files
                sub_files = list(Path(temp_dir).glob("*.json3"))
                
                if not sub_files:
                    return None
                
                # Parse the first available subtitle file
                with open(sub_files[0], 'r', encoding='utf-8') as f:
                    sub_data = json.load(f)
                
                return self._parse_transcript(sub_data, url)
                
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
        options = ["--dump-json", "--no-download"]
        data = self._run_yt_dlp(url, options)
        
        return ChannelInfo(
            id=data.get("uploader_id", ""),
            name=data.get("uploader", ""),
            url=data.get("uploader_url", ""),
            description=data.get("description"),
            stats=ChannelStats(subscriber_count=data.get("subscriber_count"))
        )
    
    async def get_playlist_info(self, url: str) -> PlaylistInfo:
        """
        Extract playlist information.
        
        Args:
            url: YouTube playlist URL
            
        Returns:
            PlaylistInfo object
        """
        options = ["--dump-json", "--no-download", "--flat-playlist"]
        data = self._run_yt_dlp(url, options)
        
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
            return PlaylistInfo(
                id=first_video.get("playlist_id", ""),
                title=first_video.get("playlist_title", ""),
                uploader=first_video.get("playlist_uploader", ""),
                uploader_id=first_video.get("playlist_uploader_id", ""),
                video_count=len(videos),
                videos=videos
            )
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
            
            return PlaylistInfo(
                id=data.get("playlist_id", ""),
                title=data.get("playlist_title", data.get("title", "")),
                uploader=data.get("uploader", ""),
                uploader_id=data.get("uploader_id", ""),
                video_count=1,
                videos=[video]
            )
