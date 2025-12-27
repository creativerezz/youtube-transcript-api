# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
A FastAPI-based server that extracts YouTube video information including metadata, captions, transcripts, and timestamps. The server uses async processing with `asyncio.to_thread()` for parallel execution of blocking YouTube API calls and supports Webshare proxy integration to avoid IP blocking.

## Development Commands

### Environment Setup
```bash
# Install dependencies (using uv - recommended)
uv sync

# Verify environment configuration
python load_env.py
```

### Running the Server
```bash
# Start the development server
uv run main.py

# Or run directly with Python
python main.py

# Customize host/port via environment variables
export PORT=8080
export HOST=127.0.0.1
uv run main.py
```

### Testing
```bash
# Run the comprehensive endpoint test script
chmod +x test_endpoints.sh
./test_endpoints.sh

# Test against a custom server
./test_endpoints.sh http://your-server:8000
```

## Architecture

### Core Components

**YouTubeTools Class** (main.py:81-337)
- Static utility class that handles all YouTube operations
- Key methods:
  - `get_youtube_video_id()`: Extracts video ID from various YouTube URL formats (youtu.be, /watch, /embed, /v/)
  - `get_video_data()`: Fetches metadata via YouTube oEmbed API (synchronous)
  - `get_video_captions()`: Async wrapper using `asyncio.to_thread()` for transcript fetching
  - `get_video_timestamps()`: Async method that generates timestamped transcript
  - `get_video_transcript_languages()`: Lists available transcript languages
  - `_create_youtube_api()`: Factory method for YouTubeTranscriptApi with optional proxy config
  - `_get_transcript_with_fallback()`: Implements language fallback logic (prefers English, falls back to first available)

**API Endpoints** (main.py:343-397)
- All endpoints use Pydantic's `YouTubeRequest` model for validation
- `POST /video-data`: Video metadata (synchronous)
- `POST /video-captions`: Full transcript text (async)
- `POST /video-timestamps`: Timestamped transcript segments (async)
- `POST /video-transcript-languages`: Available language list (async)
- `GET /health`: Server and proxy status check

### Async Processing Pattern
The server uses a specific pattern for handling blocking YouTube API operations:
```python
# Blocking operations are offloaded to background threads
result = await asyncio.to_thread(blocking_function, args)
```
This approach keeps FastAPI's async event loop responsive while allowing synchronous libraries (youtube-transcript-api) to run in parallel.

### Proxy Configuration
- Webshare proxy support is configured globally via `WEBSHARE_PROXY_CONFIG` 
- Proxy config is loaded from environment variables at startup
- The proxy uses IP filtering for "de" and "us" locations (hardcoded in main.py:49)
- Without proxy credentials, server works but may face IP blocking after several requests

### Environment Variables
Required for proxy (optional but recommended):
- `WEBSHARE_PROXY_USERNAME`: Webshare proxy username
- `WEBSHARE_PROXY_PASSWORD`: Webshare proxy password

Optional:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Error Handling Strategy
- Invalid URLs return 400 Bad Request
- Missing/unavailable captions return 500 Internal Server Error
- Malformed requests return 422 Unprocessable Entity (automatic Pydantic validation)
- Extensive logging with timestamps for debugging

## Key Implementation Notes

### URL Parsing
The `get_youtube_video_id()` method supports multiple URL formats:
- Standard: `youtube.com/watch?v=VIDEO_ID`
- Short: `youtu.be/VIDEO_ID`
- Embed: `youtube.com/embed/VIDEO_ID`
- Old: `youtube.com/v/VIDEO_ID`

### Language Fallback Behavior
When fetching transcripts with multiple language preferences:
1. Tries each requested language in order
2. If none found, uses first available language
3. If no languages specified, prefers English, then first available

### Logging
Every operation logs with timestamp using `datetime.now()`. Log messages follow the pattern:
```python
print(f"[{datetime.now()}] Log message here")
```

## Dependencies
- `fastapi==0.116.1`: Web framework
- `uvicorn==0.35.0`: ASGI server
- `youtube_transcript_api==1.2.1`: YouTube transcript extraction with proxy support
- `gunicorn==21.2.0`: Production WSGI server (not used in development)
- `pydantic==2.11.7`: Data validation

## Testing Strategy
The `test_endpoints.sh` script tests:
- All 5 endpoints (health, video-data, captions, timestamps, languages)
- Multiple video types (English, Hindi, various URL formats)
- Language fallback scenarios
- Error cases (invalid URLs, missing parameters, malformed JSON)
- Timeout handling (30 second default)

Test videos are defined at the top of the script and include edge cases like short URLs and non-English content.
