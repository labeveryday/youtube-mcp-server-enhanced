"""
Transcript-related data models for YouTube content.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TranscriptEntry(BaseModel):
    """Individual transcript entry with timing."""
    
    start_time: float = Field(description="Start time in seconds")
    end_time: float = Field(description="End time in seconds") 
    text: str = Field(description="Transcript text")
    duration: float = Field(description="Duration of this segment")
    
    @property
    def formatted_time(self) -> str:
        """Format start time as MM:SS."""
        minutes = int(self.start_time // 60)
        seconds = int(self.start_time % 60)
        return f"{minutes:02d}:{seconds:02d}"


class Transcript(BaseModel):
    """Complete video transcript."""
    
    video_id: str = Field(description="YouTube video ID")
    language: str = Field(description="Transcript language code")
    is_auto_generated: bool = Field(description="Whether transcript is auto-generated")
    entries: List[TranscriptEntry] = Field(description="Transcript entries")
    
    @property
    def full_text(self) -> str:
        """Get complete transcript as single text."""
        return " ".join(entry.text for entry in self.entries)
    
    @property
    def total_duration(self) -> float:
        """Get total transcript duration."""
        if not self.entries:
            return 0.0
        return max(entry.end_time for entry in self.entries)
    
    def get_text_at_time(self, timestamp: float) -> Optional[str]:
        """Get transcript text at specific timestamp."""
        for entry in self.entries:
            if entry.start_time <= timestamp <= entry.end_time:
                return entry.text
        return None
    
    def search_text(self, query: str, case_sensitive: bool = False) -> List[TranscriptEntry]:
        """Search for text in transcript entries."""
        if not case_sensitive:
            query = query.lower()
        
        results = []
        for entry in self.entries:
            text = entry.text if case_sensitive else entry.text.lower()
            if query in text:
                results.append(entry)
        
        return results
