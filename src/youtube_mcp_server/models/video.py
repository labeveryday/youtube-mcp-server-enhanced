"""
Video-related data models for YouTube content.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class VideoStats(BaseModel):
    """Statistics for a YouTube video."""
    
    view_count: int = Field(description="Total number of views")
    like_count: Optional[int] = Field(None, description="Number of likes")
    comment_count: Optional[int] = Field(None, description="Number of comments")
    duration_seconds: int = Field(description="Video duration in seconds")
    duration_string: str = Field(description="Human-readable duration (e.g., '3:33')")


class VideoMetadata(BaseModel):
    """Core metadata for a YouTube video."""
    
    id: str = Field(description="YouTube video ID")
    title: str = Field(description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    upload_date: Optional[str] = Field(None, description="Upload date (YYYYMMDD format)")
    uploader: str = Field(description="Channel name")
    uploader_id: str = Field(description="Channel ID")
    uploader_url: str = Field(description="Channel URL")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    categories: List[str] = Field(default_factory=list, description="Video categories")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    
    @validator('upload_date')
    def validate_upload_date(cls, v):
        """Validate upload date format."""
        if v and len(v) != 8:
            raise ValueError("Upload date must be in YYYYMMDD format")
        return v


class VideoInfo(BaseModel):
    """Complete video information combining metadata and statistics."""
    
    metadata: VideoMetadata = Field(description="Video metadata")
    stats: VideoStats = Field(description="Video statistics")
    url: str = Field(description="Original video URL")
    webpage_url: str = Field(description="YouTube webpage URL")
    
    # Additional useful fields
    age_limit: int = Field(0, description="Age restriction (0 = no restriction)")
    availability: Optional[str] = Field(None, description="Video availability status")
    live_status: Optional[str] = Field(None, description="Live stream status")
    
    # Engagement metrics
    like_to_view_ratio: Optional[float] = Field(None, description="Like-to-view ratio")
    comment_to_view_ratio: Optional[float] = Field(None, description="Comment-to-view ratio")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculate engagement ratios
        if self.stats.like_count and self.stats.view_count > 0:
            self.like_to_view_ratio = self.stats.like_count / self.stats.view_count
        
        if self.stats.comment_count and self.stats.view_count > 0:
            self.comment_to_view_ratio = self.stats.comment_count / self.stats.view_count
    
    @classmethod
    def from_yt_dlp_data(cls, data: Dict[str, Any]) -> "VideoInfo":
        """Create VideoInfo from yt-dlp extracted data."""
        
        # Extract metadata
        metadata = VideoMetadata(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description"),
            upload_date=data.get("upload_date"),
            uploader=data.get("uploader", ""),
            uploader_id=data.get("uploader_id", ""),
            uploader_url=data.get("uploader_url", ""),
            tags=data.get("tags", []),
            categories=data.get("categories", []),
            thumbnail=data.get("thumbnail")
        )
        
        # Extract statistics
        stats = VideoStats(
            view_count=data.get("view_count", 0),
            like_count=data.get("like_count"),
            comment_count=data.get("comment_count"),
            duration_seconds=data.get("duration", 0),
            duration_string=data.get("duration_string", "0:00")
        )
        
        return cls(
            metadata=metadata,
            stats=stats,
            url=data.get("original_url", ""),
            webpage_url=data.get("webpage_url", ""),
            age_limit=data.get("age_limit", 0),
            availability=data.get("availability"),
            live_status=data.get("live_status")
        )
