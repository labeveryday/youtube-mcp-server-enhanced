"""
Channel-related data models for YouTube content.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChannelStats(BaseModel):
    """Statistics for a YouTube channel."""
    
    subscriber_count: Optional[int] = Field(None, description="Number of subscribers")
    video_count: Optional[int] = Field(None, description="Total number of videos")
    view_count: Optional[int] = Field(None, description="Total channel views")


class ChannelInfo(BaseModel):
    """Complete YouTube channel information."""
    
    id: str = Field(description="Channel ID")
    name: str = Field(description="Channel name")
    url: str = Field(description="Channel URL")
    description: Optional[str] = Field(None, description="Channel description")
    avatar_url: Optional[str] = Field(None, description="Channel avatar/profile picture URL")
    banner_url: Optional[str] = Field(None, description="Channel banner URL")
    stats: Optional[ChannelStats] = Field(None, description="Channel statistics")
    verified: bool = Field(False, description="Whether channel is verified")
    
    # Additional metadata
    country: Optional[str] = Field(None, description="Channel country")
    language: Optional[str] = Field(None, description="Primary channel language")
    tags: List[str] = Field(default_factory=list, description="Channel tags/keywords")
