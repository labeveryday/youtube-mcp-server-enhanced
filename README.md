# YouTube MCP Server Enhanced 🚀

A comprehensive Micro-Conversational Processor (MCP) server for extracting and analyzing YouTube data using `yt-dlp`.

## 🚀 Features

### Core Extraction
- **Video Information**: Metadata, statistics, engagement metrics
- **Channel Information**: Stats, subscriber count, view count, verification status
- **Playlist Details**: Video lists, durations, total views
- **Comments**: Threaded comments with replies and engagement
- **Transcripts**: Auto-generated and manual subtitles

### Advanced Capabilities
- **YouTube Search**: Search for videos, channels, and playlists
- **Trending Videos**: Get trending content by region
- **Batch Processing**: Extract from multiple URLs concurrently
- **Intelligent Caching**: Configurable TTL-based caching
- **Automatic Retries**: Exponential backoff for failed requests
- **Health Monitoring**: Real-time extractor status and configuration

## 🛠️ Installation

### Prerequisites
- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/) package manager** (required)
- `yt-dlp` (automatically installed via uv)

**⚠️ Important: This project requires `uv` to run properly. Install it first:**

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew (macOS)
brew install uv

# Or via pip
pip install uv
```

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd youtube-mcp-server-enhanced

# Install yt-dlp and all dependencies
uv add yt-dlp
uv sync

# Verify installation
uv run yt-dlp --version
```

## ⚙️ Configuration

### Environment Variables (.env file)
Create a `.env` file in the project root to configure the server:

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred settings
nano .env
```

Example `.env` configuration:
```bash
# Rate limiting (e.g., "500K" for 500KB/s, "1M" for 1MB/s)
YOUTUBE_RATE_LIMIT=500K

# Retry configuration
YOUTUBE_MAX_RETRIES=5
YOUTUBE_RETRY_DELAY=2.0
YOUTUBE_TIMEOUT=600

# Caching
YOUTUBE_ENABLE_CACHE=true
YOUTUBE_CACHE_TTL=3600

# Logging level
LOG_LEVEL=INFO
```

### MCP Client Configuration

#### Claude Desktop (macOS)
Add to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "youtube-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/youtube-mcp-server-enhanced",
        "python",
        "-m",
        "src.youtube_mcp_server.server"
      ],
      "env": {
        "YOUTUBE_RATE_LIMIT": "500K",
        "YOUTUBE_MAX_RETRIES": "5",
        "YOUTUBE_RETRY_DELAY": "2.0",
        "YOUTUBE_TIMEOUT": "600",
        "YOUTUBE_ENABLE_CACHE": "true",
        "YOUTUBE_CACHE_TTL": "3600"
      }
    }
  }
}
```

#### Other MCP Clients
For other MCP clients, configure the server command as:
```bash
uv run --directory /path/to/youtube-mcp-server-enhanced python -m src.youtube_mcp_server.server
```

### Default Values
- **Rate Limit**: None (uses YouTube's default)
- **Max Retries**: 5 (increased from 3 for better reliability)
- **Retry Delay**: 2.0 seconds (with exponential backoff)
- **Timeout**: 600 seconds (10 minutes)
- **Cache TTL**: 3600 seconds (1 hour)
- **Cache**: Enabled by default

## 🎯 Available MCP Tools

### Data Extraction
| Tool | Description | Example |
|------|-------------|---------|
| `get_video_info()` | Extract comprehensive video metadata | `get_video_info("https://youtube.com/watch?v=...")` |
| `get_channel_info()` | Extract channel information and stats (supports multiple URL formats) | `get_channel_info("https://youtube.com/@channel")` or `get_channel_info("https://youtube.com/ChannelName")` |
| `get_playlist_info()` | Extract playlist details and video list | `get_playlist_info("https://youtube.com/playlist?list=...")` |
| `get_video_comments()` | Extract video comments and replies | `get_video_comments("https://youtube.com/watch?v=...", 50)` |
| `get_video_transcript()` | Extract video transcripts/subtitles | `get_video_transcript("https://youtube.com/watch?v=...")` |

### Search & Discovery
| Tool | Description | Example |
|------|-------------|---------|
| `search_youtube()` | Search for videos, channels, or playlists | `search_youtube("Python tutorials", "video", 20)` |
| `get_trending_videos()` | Get trending videos by region | `get_trending_videos("US", 15)` |

### Analysis & Insights
| Tool | Description | Example |
|------|-------------|---------|
| `analyze_video_engagement()` | Analyze engagement metrics with benchmarks | `analyze_video_engagement("https://youtube.com/watch?v=...")` |
| `search_transcript()` | Search for text within video transcripts | `search_transcript("https://youtube.com/watch?v=...", "query")` |

### Batch Operations
| Tool | Description | Example |
|------|-------------|---------|
| `batch_extract_urls()` | Process multiple URLs concurrently | `batch_extract_urls(["url1", "url2"], "video")` |

### System Management
| Tool | Description | Example |
|------|-------------|---------|
| `get_extractor_health()` | Monitor extractor health and status | `get_extractor_health()` |
| `get_extractor_config()` | View current configuration | `get_extractor_config()` |
| `clear_extractor_cache()` | Clear all cached data | `clear_extractor_cache()` |

### MCP Prompts
| Prompt | Description | Example |
|--------|-------------|---------|
| `analyze-video` | Comprehensive video analysis with optional comments/transcript | `analyze-video(url, include_comments=true, include_transcript=true)` |
| `compare-videos` | Compare engagement metrics across multiple videos | `compare-videos([url1, url2, url3])` |

## 📊 Data Models

### VideoInfo
```python
{
    "metadata": {
        "id": "video_id",
        "title": "Video Title",
        "description": "Video description...",
        "uploader": "Channel Name",
        "uploader_id": "channel_id",
        "upload_date": "20240101",
        "tags": ["tag1", "tag2"],
        "categories": ["Entertainment"],
        "thumbnail": "https://..."
    },
    "statistics": {
        "view_count": 1000,
        "like_count": 50,
        "comment_count": 25,
        "duration_seconds": 120,
        "duration_string": "2:00"
    },
    "engagement": {
        "like_to_view_ratio": 0.05,
        "comment_to_view_ratio": 0.025,
        "like_rate_percentage": "5.000%",
        "comment_rate_percentage": "2.500%"
    },
    "technical": {
        "age_limit": 0,
        "availability": "public",
        "live_status": "not_live"
    }
}
```

### ChannelInfo
```python
{
    "id": "channel_id",
    "name": "Channel Name",
    "url": "https://youtube.com/@channel",
    "description": "Channel description...",
    "avatar_url": "https://...",
    "banner_url": "https://...",
    "verified": true,
    "country": "US",
    "language": "en",
    "tags": ["tag1", "tag2"],
    "statistics": {
        "subscriber_count": 10000,
        "video_count": 150,
        "view_count": 500000
    }
}
```

### PlaylistInfo
```python
{
    "id": "playlist_id",
    "title": "Playlist Title",
    "description": "Playlist description...",
    "uploader": "Channel Name",
    "uploader_id": "channel_id",
    "video_count": 25,
    "total_duration_seconds": 7200,
    "total_duration_formatted": "2h 0m",
    "total_views": 50000,
    "videos": [
        {
            "video_id": "video_id",
            "title": "Video Title",
            "uploader": "Channel Name",
            "duration": 300,
            "view_count": 2000,
            "playlist_index": 1
        }
    ]
}
```

## 🔍 Usage Examples

### Basic Video Analysis
```python
# Get comprehensive video information
video_info = await get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Extract video comments
comments = await get_video_comments("https://www.youtube.com/watch?v=dQw4w9WgXcQ", max_comments=50)

# Get video transcript
transcript = await get_video_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Search within transcript
results = await search_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "never gonna")
```

### Channel and Playlist Analysis
```python
# Get channel information
channel_info = await get_channel_info("https://www.youtube.com/@RickAstleyYT")

# Get playlist details
playlist_info = await get_playlist_info("https://www.youtube.com/playlist?list=...")
```

### Search and Discovery
```python
# Search for videos
results = await search_youtube("Python programming tutorials", "video", 10)

# Get trending videos
trending = await get_trending_videos("US", 20)
```

### Advanced Analysis
```python
# Analyze video engagement with benchmarks
engagement = await analyze_video_engagement("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Compare multiple videos
comparison = await compare_videos([
    "https://youtube.com/watch?v=video1",
    "https://youtube.com/watch?v=video2"
])
```

### Batch Processing
```python
# Process multiple URLs concurrently
results = await batch_extract_urls([
    "https://youtube.com/watch?v=video1",
    "https://youtube.com/watch?v=video2"
], "video")
```

## ⚡ Performance Features

### Caching
- **In-Memory Cache**: Configurable TTL-based caching
- **Cache Keys**: Unique keys for each request type and parameters
- **Cache Management**: View stats, clear cache, configure TTL

### Retry Logic
- **Automatic Retries**: Configurable retry attempts
- **Exponential Backoff**: Increasing delay between retries
- **Error Handling**: Graceful degradation on failures

### Batch Processing
- **Concurrent Extraction**: Process multiple URLs simultaneously using asyncio
- **Async Operations**: Non-blocking I/O for better performance
- **Result Aggregation**: Combined results with success/failure counts

## 🏥 Health Monitoring

### Health Status
```python
health = await get_extractor_health()
# Returns:
{
    "health": {
        "status": "healthy",
        "yt_dlp_available": true,
        "yt_dlp_version": "2025.6.30",
        "cache": {"enabled": true, "size": 5, "ttl": 3600},
        "config": {"rate_limit": "1M", "max_retries": 3, "timeout": 300}
    },
    "cache": {
        "enabled": true,
        "size": 5,
        "ttl": 3600,
        "keys": ["key1", "key2"],
        "total_keys": 5
    },
    "server_version": "0.1.0",
    "mcp_version": "1.0.0"
}
```

### Configuration View
```python
config = await get_extractor_config()
# Returns current extractor settings and status
```

## 🚨 Error Handling

### Retry Strategy
- **Automatic Retries**: Up to 5 attempts by default (configurable)
- **Exponential Backoff**: 2s, 4s, 8s delays
- **Rate Limiting**: 500KB/s limit with 2-second sleep intervals
- **Graceful Degradation**: Return partial results when possible

### Error Types
- **YouTubeExtractorError**: Extraction-specific errors
- **InvalidURLError**: Invalid YouTube URL format
- **RuntimeError**: General execution errors

### Troubleshooting

#### Rate Limiting Issues
If you encounter rate limiting:
1. Increase sleep intervals in `.env`: `YOUTUBE_RETRY_DELAY=3.0`
2. Lower rate limit: `YOUTUBE_RATE_LIMIT=300K`
3. Reduce concurrent requests

#### yt-dlp Not Working
1. Ensure uv is installed: `uv --version`
2. Verify yt-dlp installation: `uv run yt-dlp --version`
3. The server automatically uses `uv run yt-dlp` if direct access fails

#### MCP Connection Issues
1. Restart your MCP client after code changes
2. Check logs for specific error messages
3. Verify environment variables are loaded correctly

## 🔧 Development

### Running the Server
**⚠️ Always use `uv run` to ensure proper dependency management:**

```bash
# Start the MCP server (recommended)
uv run python -m src.youtube_mcp_server.server

# Or if you have a run_server.py file
uv run python run_server.py
```

### Testing
```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_basic.py

# Run with coverage
uv run pytest --cov=src tests/
```

## 📈 Use Cases

### Content Analysis
- **Video Performance**: Analyze view counts, engagement metrics
- **Channel Growth**: Track subscriber and view count trends
- **Content Discovery**: Find trending and popular content

### Research & Analytics
- **Market Research**: Analyze competitor channels and content
- **Trend Analysis**: Identify trending topics and content types
- **Audience Insights**: Understand viewer preferences and behavior

### Content Management
- **Playlist Organization**: Manage and analyze video collections
- **Comment Moderation**: Extract and analyze user feedback
- **Transcript Analysis**: Process and search video content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **yt-dlp**: The core YouTube extraction engine
- **FastMCP**: The MCP server framework
- **Pydantic**: Data validation and serialization

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/labeveryday/youtube-mcp-server-enhanced/issues)
- **Discussions**: [GitHub Discussions](https://github.com/labeveryday/youtube-mcp-server-enhanced/discussions)
- **Email**: info@labeveryday.com

## 🗺️ Roadmap

- [x] **Batch processing** for multiple videos
- [x] **Caching layer** for improved performance
- [x] **Advanced analytics** (engagement analysis, benchmarks)
- [x] **Rate limiting** and quota management
- [ ] **Export functionality** (JSON, CSV, etc.)
- [ ] **WebSocket support** for real-time updates
- [ ] **Integration examples** with popular MCP clients

---

**Made with ❤️ by Du'An Lightfoot**

*Empowering developers to extract meaningful insights from YouTube content through the Model Context Protocol.* 
