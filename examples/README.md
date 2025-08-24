# YouTube MCP Server Enhanced - Examples

This directory contains examples demonstrating how to use the YouTube MCP Server Enhanced.

## 📁 Files

### `basic_usage.py`
Demonstrates the core MCP tools for YouTube data extraction and analysis:
- Video information extraction
- Comment retrieval
- Transcript extraction and search
- Channel information
- Video engagement analysis
- YouTube search functionality
- Trending videos
- Batch processing
- System health monitoring

**Usage:**
```bash
cd examples
python basic_usage.py
```

### `mcp_prompts_example.py`
Shows how to use the MCP prompts for comprehensive video analysis:
- `analyze-video` prompt with optional comments and transcript
- `compare-videos` prompt for multi-video comparison
- Different analysis configurations

**Usage:**
```bash
cd examples
python mcp_prompts_example.py
```

### `mcp_config.json`
Example MCP client configuration file showing how to configure the server:
- Command and arguments for running the server
- Environment variables for configuration
- Server settings

**Usage:**
Copy this file to your MCP client configuration directory and adjust the paths as needed.

## 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   # From project root
   uv sync
   
   # Install yt-dlp
   uv add yt-dlp
   ```

3. **Run Examples:**
   ```bash
   cd examples
   uv run python basic_usage.py
   uv run python mcp_prompts_example.py
   ```

## 🔧 Configuration

The examples use default configuration, but you can customize by setting environment variables:

```bash
export YOUTUBE_RATE_LIMIT="1M"
export YOUTUBE_MAX_RETRIES="3"
export YOUTUBE_RETRY_DELAY="1.0"
export YOUTUBE_TIMEOUT="300"
export YOUTUBE_ENABLE_CACHE="true"
export YOUTUBE_CACHE_TTL="3600"
```

## 📝 Notes

- Examples use real YouTube URLs (Rick Astley, PSY, Luis Fonsi videos)
- All examples are async and use `asyncio.run()`
- Error handling is included for robustness
- Examples demonstrate both successful and error cases
- The server must be running for MCP tools to work

## 🐛 Troubleshooting

If you encounter errors:

1. **Check yt-dlp installation:**
   ```bash
   uv run yt-dlp --version
   ```

2. **Verify Python path:**
   The examples add the `src` directory to the Python path automatically.

3. **Check network connectivity:**
   Examples require internet access to fetch YouTube data.

4. **Review error messages:**
   Most errors include helpful debugging information.
