#!/usr/bin/env python3
"""
MCP Prompts Examples for YouTube MCP Server Enhanced.

This script demonstrates how to use the MCP prompts for comprehensive
video analysis and comparison.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_mcp_server.server import (
    analyze_video_prompt,
    compare_videos_prompt
)


async def main():
    """Demonstrate usage of MCP prompts for video analysis."""
    
    print("🚀 YouTube MCP Server Enhanced - MCP Prompts Examples\n")
    
    # Example video URLs
    video_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - Gangnam Style
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk"   # Luis Fonsi - Despacito
    ]
    
    # Example 1: Comprehensive video analysis with comments and transcript
    print("📹 Example 1: Comprehensive Video Analysis")
    print("=" * 50)
    try:
        analysis = await analyze_video_prompt(
            url=video_urls[0],
            include_comments=True,
            include_transcript=True,
            max_comments=10
        )
        
        print(f"Video: {analysis['video_info']['title']}")
        print(f"Channel: {analysis['video_info']['channel']}")
        print(f"Views: {analysis['video_info']['views']:,}")
        print(f"Likes: {analysis['video_info']['likes']:,}")
        print(f"Comments: {analysis['video_info']['comments']:,}")
        print(f"Duration: {analysis['video_info']['duration']}")
        print(f"Upload Date: {analysis['video_info']['upload_date']}")
        print(f"Like Rate: {analysis['video_info']['like_rate']}")
        print(f"Comment Rate: {analysis['video_info']['comment_rate']}")
        
        if 'comments' in analysis:
            print(f"\nTop Comments ({len(analysis['comments'])}):")
            for i, comment in enumerate(analysis['comments'][:3], 1):
                print(f"  {i}. {comment['author']}: {comment['text']}")
                print(f"     Likes: {comment['likes']}, Replies: {comment['replies']}")
        
        if 'transcript' in analysis:
            print(f"\nTranscript Info:")
            print(f"  Language: {analysis['transcript']['language']}")
            print(f"  Auto-generated: {analysis['transcript']['auto_generated']}")
            print(f"  Entries: {analysis['transcript']['entries_count']}")
            print(f"  Preview: {analysis['transcript']['full_text']}")
        
        print()
        
    except Exception as e:
        print(f"Error in video analysis: {e}\n")
    
    # Example 2: Video comparison
    print("📊 Example 2: Video Comparison")
    print("=" * 50)
    try:
        comparison = await compare_videos_prompt(urls=video_urls)
        
        print(f"Comparison Results ({comparison['summary']['total_videos']} videos):")
        print(f"Highest Views: {comparison['summary']['highest_views']:,}")
        print(f"Average Like Rate: {comparison['summary']['average_like_rate']:.3f}")
        
        print("\nVideos by View Count:")
        for i, video in enumerate(comparison['comparison'], 1):
            print(f"  {i}. {video['title']}")
            print(f"     Channel: {video['channel']}")
            print(f"     Views: {video['views']:,}")
            print(f"     Likes: {video['likes']:,}")
            print(f"     Comments: {video['comments']:,}")
            print(f"     Like Rate: {video['like_rate']:.3f}")
            print(f"     Comment Rate: {video['comment_rate']:.3f}")
            print()
        
    except Exception as e:
        print(f"Error in video comparison: {e}\n")
    
    # Example 3: Video analysis without comments/transcript
    print("📹 Example 3: Basic Video Analysis (No Comments/Transcript)")
    print("=" * 50)
    try:
        basic_analysis = await analyze_video_prompt(
            url=video_urls[1],
            include_comments=False,
            include_transcript=False
        )
        
        print(f"Video: {basic_analysis['video_info']['title']}")
        print(f"Channel: {basic_analysis['video_info']['channel']}")
        print(f"Views: {basic_analysis['video_info']['views']:,}")
        print(f"Likes: {basic_analysis['video_info']['likes']:,}")
        print(f"Comments: {basic_analysis['video_info']['comments']:,}")
        print(f"Duration: {basic_analysis['video_info']['duration']}")
        print(f"Upload Date: {basic_analysis['video_info']['upload_date']}")
        print(f"Like Rate: {basic_analysis['video_info']['like_rate']}")
        print(f"Comment Rate: {basic_analysis['video_info']['comment_rate']}")
        
        # Verify no comments or transcript were included
        if 'comments' not in basic_analysis:
            print("\n✅ Comments were not included (as expected)")
        if 'transcript' not in basic_analysis:
            print("✅ Transcript was not included (as expected)")
        
        print()
        
    except Exception as e:
        print(f"Error in basic video analysis: {e}\n")
    
    print("✅ MCP Prompts Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
