"""
Formatting utility functions for displaying YouTube data.
"""

from typing import Optional


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1:23:45" or "3:33")
    """
    if seconds < 0:
        return "0:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def format_number(number: Optional[int]) -> str:
    """
    Format large numbers with appropriate suffixes.
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string (e.g., "1.2M", "345K")
    """
    if number is None:
        return "Unknown"
    
    if number < 1000:
        return str(number)
    elif number < 1_000_000:
        return f"{number / 1000:.1f}K"
    elif number < 1_000_000_000:
        return f"{number / 1_000_000:.1f}M"
    else:
        return f"{number / 1_000_000_000:.1f}B"


def format_engagement_rate(rate: float) -> str:
    """
    Format engagement rate as percentage with appropriate precision.
    
    Args:
        rate: Engagement rate (0.0 to 1.0)
        
    Returns:
        Formatted percentage string
    """
    percentage = rate * 100
    
    if percentage < 0.01:
        return f"{percentage:.3f}%"
    elif percentage < 0.1:
        return f"{percentage:.2f}%"
    else:
        return f"{percentage:.1f}%"


def format_upload_date(date_str: Optional[str]) -> str:
    """
    Format upload date from YYYYMMDD to readable format.
    
    Args:
        date_str: Date string in YYYYMMDD format
        
    Returns:
        Formatted date string
    """
    if not date_str or len(date_str) != 8:
        return "Unknown"
    
    try:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        
        # Convert month number to name
        months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        
        month_name = months[int(month) - 1]
        return f"{month_name} {int(day)}, {year}"
    except (ValueError, IndexError):
        return date_str


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def format_view_count_with_context(views: int, upload_date: Optional[str] = None) -> str:
    """
    Format view count with additional context like daily average.
    
    Args:
        views: Total view count
        upload_date: Upload date in YYYYMMDD format
        
    Returns:
        Formatted view count with context
    """
    formatted_views = format_number(views)
    
    if upload_date and len(upload_date) == 8:
        try:
            from datetime import datetime
            upload_dt = datetime.strptime(upload_date, "%Y%m%d")
            days_since_upload = (datetime.now() - upload_dt).days
            
            if days_since_upload > 0:
                daily_avg = views / days_since_upload
                return f"{formatted_views} ({format_number(int(daily_avg))}/day avg)"
        except ValueError:
            pass
    
    return formatted_views
