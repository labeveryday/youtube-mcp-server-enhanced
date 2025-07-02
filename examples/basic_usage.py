#!/usr/bin/env python3
"""
Basic usage examples for the YouTube MCP Server Enhanced.

This script demonstrates how to use the YouTubeExtractor class directly
for programmatic access to YouTube data.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_mcp_server import YouTubeExtractor


async def main():
    """Demonstrate basic usage of the YouTube extractor."""
    
    # Initialize the extractor
    extractor = YouTubeExtractor()
    
    # Example video URL (Rick Astley - Never Gonna Give You Up)
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print("🚀 YouTube MCP Server Enhanced - Basic Usage Examples\n")
    
    # Example 1: Get video information
    print("📹 Example 1: Getting video information...")
    try:
        video_info = await extractor.get_video_info(video_url)
        
        print(f"Title: {video_info.metadata.title}")
        print(f"Channel: {video_info.metadata.uploader}")
        print(f"Views: {video_info.stats.view_count:,}")
        print(f"Likes: {video_info.stats.like_count:,}")
        print(f"Duration: {video_info.stats.duration_string}")
        print(f"Like Rate: {video_info.like_to_view_ratio:.3%}")
        print()
        
    except Exception as e:
        print(f"Error getting video info: {e}\n")
    
    # Example 2: Get video transcript
    print("📝 Example 2: Getting video transcript...")
    try:
        transcript = await extractor.get_video_transcript(video_url)
        
        if transcript:
            print(f"Language: {transcript.language}")
            print(f"Auto-generated: {transcript.is_auto_generated}")
            print(f"Total entries: {len(transcript.entries)}")
            print(f"Duration: {transcript.total_duration:.1f} seconds")
            
            # Show first few entries
            print("\nFirst few transcript entries:")
            for entry in transcript.entries[:5]:
                print(f"  {entry.formatted_time}: {entry.text}")
            
            # Search for specific text
            search_results = transcript.search_text("never gonna")
            print(f"\nFound {len(search_results)} matches for 'never gonna':")
            for result in search_results[:3]:
                print(f"  {result.formatted_time}: {result.text}")
        else:
            print("No transcript available for this video.")
        print()
        
    except Exception as e:
        print(f"Error getting transcript: {e}\n")
    
    # Example 3: Get limited comments
    print("💬 Example 3: Getting video comments (limited to 5)...")
    try:
        comments = await extractor.get_video_comments(video_url, max_comments=5)
        
        print(f"Retrieved {len(comments)} comment threads:")
        for i, thread in enumerate(comments, 1):
            comment = thread.top_comment
            print(f"  {i}. {comment.author}: {comment.text[:100]}...")
            print(f"     Likes: {comment.like_count}, Replies: {len(thread.replies)}")
        print()
        
    except Exception as e:
        print(f"Error getting comments: {e}\n")
    
    # Example 4: Channel information
    print("📺 Example 4: Getting channel information...")
    try:
        channel_info = await extractor.get_channel_info(video_url)
        
        print(f"Channel Name: {channel_info.name}")
        print(f"Channel ID: {channel_info.id}")
        print(f"Channel URL: {channel_info.url}")
        if channel_info.stats and channel_info.stats.subscriber_count:
            print(f"Subscribers: {channel_info.stats.subscriber_count:,}")
        print()
        
    except Exception as e:
        print(f"Error getting channel info: {e}\n")
    
    print("✅ Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
