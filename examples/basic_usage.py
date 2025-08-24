#!/usr/bin/env python3
"""
Basic usage examples for the YouTube MCP Server Enhanced.

This script demonstrates how to use the YouTube MCP Server tools
for extracting and analyzing YouTube data.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_mcp_server.server import (
    get_video_info,
    get_video_comments,
    get_video_transcript,
    get_channel_info,
    get_playlist_info,
    search_youtube,
    get_trending_videos,
    analyze_video_engagement,
    search_transcript,
    batch_extract_urls,
    get_extractor_health,
    get_extractor_config
)


async def main():
    """Demonstrate basic usage of the YouTube MCP Server tools."""
    
    # Example video URL (Rick Astley - Never Gonna Give You Up)
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print("🚀 YouTube MCP Server Enhanced - Basic Usage Examples\n")
    
    # Example 1: Get video information
    print("📹 Example 1: Getting video information...")
    try:
        video_info = await get_video_info(video_url)
        
        print(f"Title: {video_info['metadata']['title']}")
        print(f"Channel: {video_info['metadata']['uploader']}")
        print(f"Views: {video_info['statistics']['view_count']:,}")
        print(f"Likes: {video_info['statistics']['like_count']:,}")
        print(f"Duration: {video_info['statistics']['duration_string']}")
        print(f"Like Rate: {video_info['engagement']['like_rate_percentage']}")
        print()
        
    except Exception as e:
        print(f"Error getting video info: {e}\n")
    
    # Example 2: Get video transcript
    print("📝 Example 2: Getting video transcript...")
    try:
        transcript = await get_video_transcript(video_url)
        
        if transcript:
            print(f"Language: {transcript['language']}")
            print(f"Auto-generated: {transcript['is_auto_generated']}")
            print(f"Total entries: {transcript['entries_count']}")
            print(f"Duration: {transcript['total_duration']:.1f} seconds")
            
            # Show first few entries
            print("\nFirst few transcript entries:")
            for entry in transcript['entries'][:5]:
                print(f"  {entry['formatted_time']}: {entry['text']}")
            
            # Search for specific text
            search_results = await search_transcript(video_url, "never gonna")
            print(f"\nFound {len(search_results)} matches for 'never gonna':")
            for result in search_results[:3]:
                print(f"  {result['formatted_time']}: {result['text']}")
        else:
            print("No transcript available for this video.")
        print()
        
    except Exception as e:
        print(f"Error getting transcript: {e}\n")
    
    # Example 3: Get limited comments
    print("💬 Example 3: Getting video comments (limited to 5)...")
    try:
        comments = await get_video_comments(video_url, max_comments=5)
        
        print(f"Retrieved {len(comments)} comment threads:")
        for i, thread in enumerate(comments, 1):
            print(f"  {i}. {thread['author']}: {thread['text'][:100]}...")
            print(f"     Likes: {thread['like_count']}, Replies: {thread['reply_count']}")
        print()
        
    except Exception as e:
        print(f"Error getting comments: {e}\n")
    
    # Example 4: Channel information
    print("📺 Example 4: Getting channel information...")
    try:
        channel_info = await get_channel_info(video_url)
        
        print(f"Channel Name: {channel_info['name']}")
        print(f"Channel ID: {channel_info['id']}")
        print(f"Channel URL: {channel_info['url']}")
        if channel_info['statistics']['subscriber_count']:
            print(f"Subscribers: {channel_info['statistics']['subscriber_count']:,}")
        print()
        
    except Exception as e:
        print(f"Error getting channel info: {e}\n")
    
    # Example 5: Video engagement analysis
    print("📊 Example 5: Analyzing video engagement...")
    try:
        engagement = await analyze_video_engagement(video_url)
        
        print(f"Video: {engagement['video']['title']}")
        print(f"Like Rate: {engagement['engagement_rates']['like_rate']:.3f}%")
        print(f"Comment Rate: {engagement['engagement_rates']['comment_rate']:.3f}%")
        print(f"Like Performance: {engagement['benchmarks']['like_performance']}")
        print(f"Comment Performance: {engagement['benchmarks']['comment_performance']}")
        print(f"Overall Assessment: {engagement['benchmarks']['overall_assessment']}")
        print()
        
    except Exception as e:
        print(f"Error analyzing engagement: {e}\n")
    
    # Example 6: YouTube search
    print("🔍 Example 6: Searching YouTube...")
    try:
        search_results = await search_youtube("Python programming", "video", 5)
        
        print(f"Found {search_results['result_count']} videos:")
        for i, video in enumerate(search_results['results'][:3], 1):
            print(f"  {i}. {video.get('title', 'No title')}")
            print(f"     Channel: {video.get('uploader', 'Unknown')}")
            print(f"     Duration: {video.get('duration_string', 'Unknown')}")
        print()
        
    except Exception as e:
        print(f"Error searching YouTube: {e}\n")
    
    # Example 7: Trending videos
    print("📈 Example 7: Getting trending videos...")
    try:
        trending = await get_trending_videos("US", 5)
        
        print(f"Found {trending['result_count']} trending videos in US:")
        for i, video in enumerate(trending['trending_videos'][:3], 1):
            print(f"  {i}. {video.get('title', 'No title')}")
            print(f"     Channel: {video.get('uploader', 'Unknown')}")
            print(f"     Views: {video.get('view_count', 0):,}")
        print()
        
    except Exception as e:
        print(f"Error getting trending videos: {e}\n")
    
    # Example 8: Batch processing
    print("⚡ Example 8: Batch processing multiple URLs...")
    try:
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=9bZkp7q19f0"  # PSY - Gangnam Style
        ]
        
        batch_results = await batch_extract_urls(urls, "video")
        
        print(f"Processed {batch_results['total_urls']} URLs:")
        print(f"Successful: {batch_results['successful_extractions']}")
        print(f"Failed: {batch_results['failed_extractions']}")
        
        for i, result in enumerate(batch_results['results'][:2], 1):
            if isinstance(result, dict) and 'metadata' in result:
                print(f"  {i}. {result['metadata']['title']}")
            else:
                print(f"  {i}. [Error or invalid result]")
        print()
        
    except Exception as e:
        print(f"Error in batch processing: {e}\n")
    
    # Example 9: System health and configuration
    print("🏥 Example 9: Checking system health...")
    try:
        health = await get_extractor_health()
        config = await get_extractor_config()
        
        print(f"Status: {health['health']['status']}")
        print(f"yt-dlp Version: {health['health']['yt_dlp_version']}")
        print(f"Cache Enabled: {health['cache']['enabled']}")
        print(f"Cache Size: {health['cache']['size']} items")
        print(f"Max Retries: {config['max_retries']}")
        print(f"Timeout: {config['timeout']} seconds")
        print()
        
    except Exception as e:
        print(f"Error checking health: {e}\n")
    
    print("✅ Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
