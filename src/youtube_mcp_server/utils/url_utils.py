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


def normalize_channel_url(url: str) -> Optional[str]:
    """
    Normalize YouTube channel URL to modern @handle format.
    
    Converts various channel URL formats to the modern @handle format:
    - youtube.com/ChannelName -> youtube.com/@ChannelName
    - youtube.com/c/ChannelName -> youtube.com/@ChannelName  
    - youtube.com/user/ChannelName -> youtube.com/@ChannelName
    - youtube.com/channel/UCxxx -> youtube.com/channel/UCxxx (keep channel ID format)
    
    Args:
        url: YouTube channel URL to normalize
        
    Returns:
        Normalized channel URL or original URL if no normalization needed
    """
    if not is_valid_youtube_url(url):
        return None
    
    # Pattern to match old-style channel URLs without @ symbol
    # Matches: youtube.com/ChannelName (but not youtube.com/@ChannelName, youtube.com/watch, etc.)
    old_format_pattern = r'(https?://)?(www\.)?youtube\.com/([a-zA-Z0-9_-]+)(?:/.*)?$'
    match = re.match(old_format_pattern, url)
    
    if match:
        channel_name = match.group(3)
        # Don't convert if it's already a known path (watch, playlist, etc.) or starts with UC (channel ID)
        if channel_name not in ['watch', 'playlist', 'embed', 'v', 'shorts', 'live', 'channel', 'c', 'user'] and not channel_name.startswith('UC'):
            return f"https://www.youtube.com/@{channel_name}"
    
    # Handle /c/ format
    if '/c/' in url:
        channel_name = extract_channel_id(url)
        if channel_name:
            return f"https://www.youtube.com/@{channel_name}"
    
    # Handle /user/ format  
    if '/user/' in url:
        channel_name = extract_channel_id(url)
        if channel_name:
            return f"https://www.youtube.com/@{channel_name}"
    
    # Return original URL if no normalization needed
    return url
