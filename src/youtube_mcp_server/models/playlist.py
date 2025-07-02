"""
Playlist-related data models for YouTube content.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PlaylistItem(BaseModel):
    """Individual item in a YouTube playlist."""
    
    video_id: str = Field(description="YouTube video ID")
    title: str = Field(description="Video title")
    uploader: str = Field(description="Video uploader/channel")
    duration: Optional[int] = Field(None, description="Video duration in seconds")
    view_count: Optional[int] = Field(None, description="Video view count")
    playlist_index: int = Field(description="Position in playlist (1-based)")


class PlaylistInfo(BaseModel):
    """Complete YouTube playlist information."""
    
    id: str = Field(description="Playlist ID")
    title: str = Field(description="Playlist title")
    description: Optional[str] = Field(None, description="Playlist description")
    uploader: str = Field(description="Playlist creator")
    uploader_id: str = Field(description="Creator channel ID")
    video_count: int = Field(description="Number of videos in playlist")
    videos: List[PlaylistItem] = Field(default_factory=list, description="Playlist videos")
    
    @property
    def total_duration(self) -> int:
        """Calculate total playlist duration in seconds."""
        return sum(video.duration or 0 for video in self.videos)
    
    @property
    def total_views(self) -> int:
        """Calculate total views across all playlist videos."""
        return sum(video.view_count or 0 for video in self.videos)
