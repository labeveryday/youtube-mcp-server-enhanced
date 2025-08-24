"""
Comment-related data models for YouTube content.
"""

from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class Comment(BaseModel):
    """Individual YouTube comment."""
    
    id: str = Field(description="Comment ID")
    text: str = Field(description="Comment text content")
    author: str = Field(description="Comment author name")
    author_id: Optional[str] = Field(None, description="Author channel ID")
    like_count: int = Field(0, description="Number of likes on comment")
    timestamp: Optional[Union[str, int]] = Field(None, description="Comment timestamp")
    is_pinned: bool = Field(False, description="Whether comment is pinned")
    is_favorited: bool = Field(False, description="Whether comment is favorited by creator")
    parent_id: Optional[str] = Field(None, description="Parent comment ID (for replies)")
    
    @field_validator('timestamp')
    @classmethod
    def convert_timestamp(cls, v):
        """Convert integer timestamp to string if needed."""
        if isinstance(v, int):
            return str(v)
        return v


class CommentThread(BaseModel):
    """YouTube comment thread with replies."""
    
    top_comment: Comment = Field(description="Top-level comment")
    replies: List[Comment] = Field(default_factory=list, description="Reply comments")
    total_reply_count: int = Field(0, description="Total number of replies")
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement (likes) for the entire thread."""
        total = self.top_comment.like_count
        total += sum(reply.like_count for reply in self.replies)
        return total
