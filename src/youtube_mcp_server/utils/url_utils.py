"""
URL utility functions for YouTube URLs.
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Optional


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats.
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or None if not found
    """
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def is_valid_youtube_url(url: str) -> bool:
    """
    Check if URL is a valid YouTube URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube URL
    """
    try:
        parsed = urlparse(url)
        valid_domains = [
            "youtube.com",
            "www.youtube.com", 
            "youtu.be",
            "m.youtube.com"
        ]
        
        return parsed.netloc in valid_domains
    except Exception:
        return False


def normalize_youtube_url(url: str) -> Optional[str]:
    """
    Normalize YouTube URL to standard format.
    
    Args:
        url: YouTube URL to normalize
        
    Returns:
        Normalized URL or None if invalid
    """
    video_id = extract_video_id(url)
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    
    return None


def extract_playlist_id(url: str) -> Optional[str]:
    """
    Extract playlist ID from YouTube URL.
    
    Args:
        url: YouTube playlist URL
        
    Returns:
        Playlist ID or None if not found
    """
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        if 'list' in query_params:
            return query_params['list'][0]
    except Exception:
        pass
    
    return None


def extract_channel_id(url: str) -> Optional[str]:
    """
    Extract channel ID from YouTube URL.
    
    Args:
        url: YouTube channel URL
        
    Returns:
        Channel ID or None if not found
    """
    patterns = [
        r'youtube\.com\/channel\/([a-zA-Z0-9_-]+)',
        r'youtube\.com\/c\/([a-zA-Z0-9_-]+)',
        r'youtube\.com\/@([a-zA-Z0-9_-]+)',
        r'youtube\.com\/user\/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None
