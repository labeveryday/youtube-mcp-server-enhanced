"""
Basic tests for the YouTube MCP Server Enhanced.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_mcp_server.models.video import VideoInfo, VideoStats, VideoMetadata
from youtube_mcp_server.utils.url_utils import extract_video_id, is_valid_youtube_url
from youtube_mcp_server.utils.format_utils import format_duration, format_number


class TestURLUtils:
    """Test URL utility functions."""
    
    def test_extract_video_id(self):
        """Test video ID extraction from various URL formats."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=dQw4w9WgXcQ&t=30s", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("invalid-url", None),
        ]
        
        for url, expected in test_cases:
            result = extract_video_id(url)
            assert result == expected, f"Failed for URL: {url}"
    
    def test_is_valid_youtube_url(self):
        """Test YouTube URL validation."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        ]
        
        invalid_urls = [
            "https://example.com/video",
            "not-a-url",
            "https://vimeo.com/123456",
        ]
        
        for url in valid_urls:
            assert is_valid_youtube_url(url), f"Should be valid: {url}"
        
        for url in invalid_urls:
            assert not is_valid_youtube_url(url), f"Should be invalid: {url}"


class TestFormatUtils:
    """Test formatting utility functions."""
    
    def test_format_duration(self):
        """Test duration formatting."""
        test_cases = [
            (0, "0:00"),
            (30, "0:30"),
            (90, "1:30"),
            (3661, "1:01:01"),
            (7200, "2:00:00"),
        ]
        
        for seconds, expected in test_cases:
            result = format_duration(seconds)
            assert result == expected, f"Failed for {seconds} seconds"
    
    def test_format_number(self):
        """Test number formatting."""
        test_cases = [
            (None, "Unknown"),
            (500, "500"),
            (1500, "1.5K"),
            (1500000, "1.5M"),
            (1500000000, "1.5B"),
        ]
        
        for number, expected in test_cases:
            result = format_number(number)
            assert result == expected, f"Failed for {number}"


class TestVideoModels:
    """Test video data models."""
    
    def test_video_stats_creation(self):
        """Test VideoStats model creation."""
        stats = VideoStats(
            view_count=1000000,
            like_count=50000,
            comment_count=5000,
            duration_seconds=213,
            duration_string="3:33"
        )
        
        assert stats.view_count == 1000000
        assert stats.like_count == 50000
        assert stats.comment_count == 5000
        assert stats.duration_seconds == 213
        assert stats.duration_string == "3:33"
    
    def test_video_metadata_creation(self):
        """Test VideoMetadata model creation."""
        metadata = VideoMetadata(
            id="dQw4w9WgXcQ",
            title="Test Video",
            uploader="Test Channel",
            uploader_id="UC123",
            uploader_url="https://youtube.com/@test",
            upload_date="20091025"
        )
        
        assert metadata.id == "dQw4w9WgXcQ"
        assert metadata.title == "Test Video"
        assert metadata.upload_date == "20091025"
    
    def test_video_info_engagement_calculation(self):
        """Test engagement ratio calculations in VideoInfo."""
        metadata = VideoMetadata(
            id="test",
            title="Test",
            uploader="Test",
            uploader_id="test",
            uploader_url="test"
        )
        
        stats = VideoStats(
            view_count=1000,
            like_count=50,
            comment_count=10,
            duration_seconds=60,
            duration_string="1:00"
        )
        
        video_info = VideoInfo(
            metadata=metadata,
            stats=stats,
            url="https://youtube.com/watch?v=test",
            webpage_url="https://youtube.com/watch?v=test"
        )
        
        assert video_info.like_to_view_ratio == 0.05  # 50/1000
        assert video_info.comment_to_view_ratio == 0.01  # 10/1000


if __name__ == "__main__":
    pytest.main([__file__])
