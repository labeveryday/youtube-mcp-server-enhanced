# YouTube MCP Server Enhanced 🚀

A comprehensive **Model Context Protocol (MCP) server** for YouTube data extraction and analysis. Extract video metadata, comments, transcripts, channel information, and perform engagement analysis - all without requiring API keys!

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🎥 Video Analysis
- **Comprehensive metadata** extraction (title, description, tags, statistics)
- **Engagement metrics** analysis (like rates, comment rates, benchmarking)
- **Upload performance** tracking and daily view averages

### 💬 Comment Extraction
- **Threaded comments** with replies
- **Configurable limits** to control extraction volume
- **Author information** and engagement metrics per comment

### 📝 Transcript Processing
- **Auto-generated and manual** subtitle extraction
- **Timestamped entries** with precise timing
- **Full-text search** within transcripts
- **Text-at-timestamp** lookup functionality

### 📺 Channel & Playlist Analysis
- **Channel statistics** and metadata
- **Playlist analysis** with total duration and view counts
- **Video listing** with individual metrics

### 🔧 Developer-Friendly
- **Type-safe** with Pydantic models
- **Async/await** support for better performance
- **Comprehensive error handling**
- **Extensible architecture**

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/labeveryday/youtube-mcp-server-enhanced.git
cd youtube-mcp-server-enhanced

# Install dependencies
pip install -e .

# Or install in development mode
pip install -e ".[dev]"
```

### Running as MCP Server

```bash
# Start the MCP server
uv run run_server.py
```

### Testing with MCP Inspector

You can test the server using the MCP Inspector tool:

```bash
# Test with uv (recommended)
npx @modelcontextprotocol/inspector uv --directory ./ "run" "run_server.py"

# Or test with direct Python execution
npx @modelcontextprotocol/inspector python run_server.py
```

The MCP Inspector provides a web interface to:
- View available tools and their schemas
- Test tool execution with sample inputs
- Debug server responses and error handling
- Validate MCP protocol compliance

### Using with MCP Clients

#### Integration with Amazon Q CLI

To integrate this MCP server with Amazon Q CLI, configure the MCP server in your AWS configuration:

Create or update the file at `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "youtube-enhanced": {
      "command": "uv",
      "args": ["--directory", "/path/to/youtube-mcp-server-enhanced", "run", "run_server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Replace `/path/to/youtube-mcp-server-enhanced` with the actual path to your repository.

#### Other MCP Clients

For other MCP clients, use the standard configuration:

```json
{
  "mcpServers": {
    "youtube-enhanced": {
      "command": "uv",
      "args": ["run", "run_server.py"],
      "cwd": "/path/to/youtube-mcp-server-enhanced"
    }
  }
}
```

## 🛠️ Available Tools

### 1. `get_video_info`
Extract comprehensive video information including metadata and statistics.

**Parameters:**
- `url` (string, required): YouTube video URL

**Example:**
```json
{
  "name": "get_video_info",
  "arguments": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }
}
```

### 2. `get_video_comments`
Extract comments from a YouTube video with optional limits.

**Parameters:**
- `url` (string, required): YouTube video URL
- `max_comments` (integer, optional): Maximum comments to extract (default: 100)

### 3. `get_video_transcript`
Extract transcript/subtitles from a YouTube video.

**Parameters:**
- `url` (string, required): YouTube video URL

### 4. `analyze_video_engagement`
Analyze engagement metrics with industry benchmarks.

**Parameters:**
- `url` (string, required): YouTube video URL

### 5. `search_transcript`
Search for specific text within a video's transcript.

**Parameters:**
- `url` (string, required): YouTube video URL
- `query` (string, required): Text to search for
- `case_sensitive` (boolean, optional): Case-sensitive search (default: false)

### 6. `get_channel_info`
Extract information about a YouTube channel.

**Parameters:**
- `url` (string, required): YouTube channel URL

### 7. `get_playlist_info`
Extract information about a YouTube playlist.

**Parameters:**
- `url` (string, required): YouTube playlist URL

## 📊 Example Outputs

### Video Information
```markdown
# Video Information

## Basic Details
- **Title**: Rick Astley - Never Gonna Give You Up (Official Video)
- **Channel**: Rick Astley
- **Duration**: 3:33
- **Upload Date**: Oct 25, 2009

## Statistics
- **Views**: 1,670,334,246
- **Likes**: 18,439,766 (1.104% of views)
- **Comments**: 2,300,000 (0.138% of views)

## Engagement Analysis
- **Like Rate**: Excellent (above 1%)
- **Comment Rate**: Good (above 0.1%)
```

### Transcript Search
```markdown
# Transcript Search Results

## Query: "never gonna"
- **Matches Found**: 8

## Results
**1. 00:48**: Never gonna give you up
**2. 01:02**: Never gonna let you down
**3. 01:15**: Never gonna run around and desert you
```

## 🏗️ Architecture

```
youtube-mcp-server-enhanced/
├── src/youtube_mcp_server/
│   ├── models/           # Pydantic data models
│   │   ├── video.py      # Video-related models
│   │   ├── comment.py    # Comment models
│   │   ├── transcript.py # Transcript models
│   │   ├── channel.py    # Channel models
│   │   └── playlist.py   # Playlist models
│   ├── extractors/       # Data extraction logic
│   │   └── youtube_extractor.py
│   ├── utils/           # Utility functions
│   │   ├── url_utils.py  # URL parsing utilities
│   │   ├── format_utils.py # Formatting helpers
│   │   └── errors.py     # Custom exceptions
│   └── server.py        # MCP server implementation
├── tests/               # Test suite
├── examples/            # Usage examples
└── run_server.py        # Server entry point
```

## 🔧 Development

### Setting up Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/labeveryday/youtube-mcp-server-enhanced.git
cd youtube-mcp-server-enhanced
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=youtube_mcp_server

# Run specific test file
pytest tests/test_extractor.py
```

## 📋 Requirements

- **Python 3.10+**
- **yt-dlp** - YouTube data extraction
- **mcp** - Model Context Protocol support
- **pydantic** - Data validation and serialization
- **asyncio-throttle** - Rate limiting support

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format your code (`black`, `isort`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **yt-dlp** team for the excellent YouTube extraction library
- **MCP** team for the Model Context Protocol specification
- **Pydantic** team for the fantastic data validation library

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/labeveryday/youtube-mcp-server-enhanced/issues)
- **Discussions**: [GitHub Discussions](https://github.com/labeveryday/youtube-mcp-server-enhanced/discussions)
- **Email**: duanlig@amazon.com

## 🗺️ Roadmap

- [ ] **Batch processing** for multiple videos
- [ ] **Caching layer** for improved performance
- [ ] **Export functionality** (JSON, CSV, etc.)
- [ ] **Advanced analytics** (sentiment analysis, trending topics)
- [ ] **Rate limiting** and quota management
- [ ] **WebSocket support** for real-time updates
- [ ] **Integration examples** with popular MCP clients

---

**Made with ❤️ by Du'An Lightfoot**

*Empowering developers to extract meaningful insights from YouTube content through the Model Context Protocol.* 
