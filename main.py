import json
import os
import asyncio
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import urlopen
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from anthropic import Anthropic

# Import caching utilities
from cache import get_cache, cached

# Load environment variables from .env file
try:
    from load_env import load_env_file
    load_env_file()
    print(f"[{datetime.now()}] Environment variables loaded from .env file")
except ImportError:
    print(f"[{datetime.now()}] load_env.py not found - using system environment variables only")
except Exception as e:
    print(f"[{datetime.now()}] Error loading .env file: {e}")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import WebshareProxyConfig
    print(f"[{datetime.now()}] Successfully imported YouTubeTranscriptApi and WebshareProxyConfig")
except ImportError:
    print(f"[{datetime.now()}] ERROR: Failed to import youtube_transcript_api")
    raise ImportError(
        "`youtube_transcript_api` not installed. Please install using `pip install youtube_transcript_api`"
    )

# Configure Webshare proxy to avoid IP blocking using environment variables
def get_webshare_config():
    """Get Webshare proxy configuration from environment variables."""
    username = os.getenv("WEBSHARE_PROXY_USERNAME")
    password = os.getenv("WEBSHARE_PROXY_PASSWORD")

    if not username or not password:
        print(f"[{datetime.now()}] WARNING: Webshare proxy credentials not found in environment variables")
        print(f"[{datetime.now()}] Set WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD to enable proxy")
        return None

    print(f"[{datetime.now()}] Webshare proxy configuration loaded from environment variables")
    return WebshareProxyConfig(
        proxy_username=username,
        proxy_password=password,
        filter_ip_locations=["de", "us"],
    )

WEBSHARE_PROXY_CONFIG = get_webshare_config()

# Initialize Anthropic client for LLM features
def get_anthropic_client():
    """Get Anthropic API client from environment variables."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print(f"[{datetime.now()}] WARNING: Anthropic API key not found in environment variables")
        print(f"[{datetime.now()}] Set ANTHROPIC_API_KEY to enable /video-notes and /video-translate endpoints")
        return None

    print(f"[{datetime.now()}] Anthropic API client initialized")
    return Anthropic(api_key=api_key)

ANTHROPIC_CLIENT = get_anthropic_client()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[{datetime.now()}] ========================================")
    print(f"[{datetime.now()}] YouTube API Server Starting Up")
    print(f"[{datetime.now()}] ========================================")
    print(f"[{datetime.now()}] Available endpoints:")
    print(f"[{datetime.now()}]   - GET  /health")
    print(f"[{datetime.now()}]   - GET  /cache/stats")
    print(f"[{datetime.now()}]   - POST /cache/clear")
    print(f"[{datetime.now()}]   - POST /video-data")
    print(f"[{datetime.now()}]   - POST /video-captions")
    print(f"[{datetime.now()}]   - POST /video-timestamps")
    print(f"[{datetime.now()}]   - POST /video-transcript-languages")
    print(f"[{datetime.now()}]   - POST /video-notes (requires ANTHROPIC_API_KEY)")
    print(f"[{datetime.now()}]   - POST /video-translate (requires ANTHROPIC_API_KEY)")

    # Initialize cache
    cache = get_cache()
    cache_status = "enabled" if cache.enabled else "disabled"
    print(f"[{datetime.now()}] Cache Status: Redis {cache_status}")
    if cache.enabled:
        print(f"[{datetime.now()}] Cache TTL: {cache.cache_ttl} seconds")

    proxy_status = "enabled" if WEBSHARE_PROXY_CONFIG else "disabled"
    print(f"[{datetime.now()}] Proxy Status: Webshare proxy {proxy_status}")
    print(f"[{datetime.now()}] Parallel Processing: Enabled with asyncio.to_thread()")
    print(f"[{datetime.now()}] ========================================")

    yield

    # Shutdown
    print(f"[{datetime.now()}] ========================================")
    print(f"[{datetime.now()}] YouTube API Server Shutting Down")
    print(f"[{datetime.now()}] ========================================")

app = FastAPI(title="YouTube Tools API", lifespan=lifespan)
print(f"[{datetime.now()}] FastAPI app initialized")

class YouTubeTools:
    @staticmethod
    def get_youtube_video_id(url_or_id: str) -> Optional[str]:
        """
        Function to get the video ID from a YouTube URL or extract from various URL formats.
        Also accepts direct video IDs (11 characters).

        Supported formats:
        - Direct video ID: "dQw4w9WgXcQ"
        - Standard: https://www.youtube.com/watch?v=VIDEO_ID
        - Short: https://youtu.be/VIDEO_ID
        - Embed: https://www.youtube.com/embed/VIDEO_ID
        - Short format: https://youtube.com/shorts/VIDEO_ID
        - Live: https://www.youtube.com/live/VIDEO_ID
        - Mobile: https://m.youtube.com/watch?v=VIDEO_ID
        - With timestamp: https://youtu.be/VIDEO_ID?t=123
        - With playlist: https://www.youtube.com/watch?v=VIDEO_ID&list=...
        """
        print(f"[{datetime.now()}] get_youtube_video_id called with input: {url_or_id}")

        # Check if it's already a video ID (11 characters, alphanumeric with - and _)
        if len(url_or_id) == 11 and all(c.isalnum() or c in '-_' for c in url_or_id):
            print(f"[{datetime.now()}] Input appears to be a direct video ID: {url_or_id}")
            return url_or_id

        # Try to parse as URL
        try:
            parsed_url = urlparse(url_or_id)
            hostname = parsed_url.hostname

            # Handle missing scheme
            if not hostname:
                # Try adding https:// if it looks like a URL
                if 'youtube.com' in url_or_id or 'youtu.be' in url_or_id:
                    parsed_url = urlparse(f"https://{url_or_id}")
                    hostname = parsed_url.hostname
                else:
                    print(f"[{datetime.now()}] ERROR: Could not parse hostname from: {url_or_id}")
                    return None

            print(f"[{datetime.now()}] Parsed hostname: {hostname}")

            # youtu.be format (short links)
            if hostname in ("youtu.be", "www.youtu.be"):
                # Extract video ID from path (remove leading slash and any query params)
                video_id = parsed_url.path[1:].split('?')[0].split('&')[0]
                print(f"[{datetime.now()}] Extracted video ID from youtu.be: {video_id}")
                return video_id

            # youtube.com formats
            if hostname in ("www.youtube.com", "youtube.com", "m.youtube.com", "music.youtube.com"):
                # Standard watch URL: /watch?v=VIDEO_ID
                if parsed_url.path == "/watch" or parsed_url.path.startswith("/watch?"):
                    query_params = parse_qs(parsed_url.query)
                    video_id = query_params.get("v", [None])[0]
                    print(f"[{datetime.now()}] Extracted video ID from watch URL: {video_id}")
                    return video_id

                # Embed URL: /embed/VIDEO_ID
                if parsed_url.path.startswith("/embed/"):
                    video_id = parsed_url.path.split("/")[2].split('?')[0]
                    print(f"[{datetime.now()}] Extracted video ID from embed URL: {video_id}")
                    return video_id

                # Old format: /v/VIDEO_ID
                if parsed_url.path.startswith("/v/"):
                    video_id = parsed_url.path.split("/")[2].split('?')[0]
                    print(f"[{datetime.now()}] Extracted video ID from /v/ URL: {video_id}")
                    return video_id

                # Shorts format: /shorts/VIDEO_ID
                if parsed_url.path.startswith("/shorts/"):
                    video_id = parsed_url.path.split("/")[2].split('?')[0]
                    print(f"[{datetime.now()}] Extracted video ID from shorts URL: {video_id}")
                    return video_id

                # Live format: /live/VIDEO_ID
                if parsed_url.path.startswith("/live/"):
                    video_id = parsed_url.path.split("/")[2].split('?')[0]
                    print(f"[{datetime.now()}] Extracted video ID from live URL: {video_id}")
                    return video_id

        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while parsing URL: {str(e)}")
            return None

        print(f"[{datetime.now()}] ERROR: Could not extract video ID from input: {url_or_id}")
        return None

    @staticmethod
    @cached(prefix="video_data", ttl=3600)
    def get_video_data(url: str) -> dict:
        """Function to get video data from a YouTube URL."""
        print(f"[{datetime.now()}] get_video_data called with URL: {url}")

        if not url:
            print(f"[{datetime.now()}] ERROR: No URL provided to get_video_data")
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                print(f"[{datetime.now()}] ERROR: Invalid YouTube URL: {url}")
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
            print(f"[{datetime.now()}] Video ID extracted: {video_id}")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while getting video ID: {str(e)}")
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            params = {"format": "json", "url": f"https://www.youtube.com/watch?v={video_id}"}
            oembed_url = "https://www.youtube.com/oembed"
            query_string = urlencode(params)
            full_url = oembed_url + "?" + query_string
            print(f"[{datetime.now()}] Making request to oEmbed API: {full_url}")

            with urlopen(full_url) as response:
                response_text = response.read()
                print(f"[{datetime.now()}] Received response from oEmbed API")
                video_data = json.loads(response_text.decode())
                print(f"[{datetime.now()}] Successfully parsed video data JSON")

                clean_data = {
                    "title": video_data.get("title"),
                    "author_name": video_data.get("author_name"),
                    "author_url": video_data.get("author_url"),
                    "type": video_data.get("type"),
                    "height": video_data.get("height"),
                    "width": video_data.get("width"),
                    "version": video_data.get("version"),
                    "provider_name": video_data.get("provider_name"),
                    "provider_url": video_data.get("provider_url"),
                    "thumbnail_url": video_data.get("thumbnail_url"),
                }
                print(f"[{datetime.now()}] Video data retrieved: Title='{clean_data.get('title')}', Author='{clean_data.get('author_name')}'")
                return clean_data
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while getting video data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting video data: {str(e)}")

    @staticmethod
    def _create_youtube_api():
        """Create a YouTubeTranscriptApi instance with proxy config."""
        if WEBSHARE_PROXY_CONFIG:
            return YouTubeTranscriptApi(proxy_config=WEBSHARE_PROXY_CONFIG)
        else:
            print(f"[{datetime.now()}] WARNING: Creating YouTubeTranscriptApi without proxy - may be subject to IP blocking")
            return YouTubeTranscriptApi()

    @staticmethod
    def _get_transcript_with_fallback(video_id: str, languages: Optional[List[str]] = None):
        """Get transcript with language fallback logic."""
        ytt_api = YouTubeTools._create_youtube_api()

        # First, list available transcripts
        transcript_list = ytt_api.list(video_id)
        available_languages = [t.language_code for t in transcript_list]

        # Determine which language to use and fetch transcript
        if languages:
            # Try requested languages first
            for lang in languages:
                if lang in available_languages:
                    fetched_transcript = ytt_api.fetch(video_id, languages=[lang])
                    return fetched_transcript, available_languages
            # If none found, use first available
            fetched_transcript = ytt_api.fetch(video_id, languages=[available_languages[0]])
            return fetched_transcript, available_languages
        else:
            # No languages specified, prefer English
            if 'en' in available_languages:
                fetched_transcript = ytt_api.fetch(video_id, languages=['en'])
                return fetched_transcript, available_languages
            else:
                fetched_transcript = ytt_api.fetch(video_id, languages=[available_languages[0]])
                return fetched_transcript, available_languages

    @staticmethod
    @cached(prefix="video_captions", ttl=3600)
    async def get_video_captions(url: str, languages: Optional[List[str]] = None) -> str:
        """Get captions from a YouTube video using the new API."""
        print(f"[{datetime.now()}] get_video_captions called with URL: {url}, languages: {languages}")

        if not url:
            print(f"[{datetime.now()}] ERROR: No URL provided to get_video_captions")
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                print(f"[{datetime.now()}] ERROR: Invalid YouTube URL: {url}")
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
            print(f"[{datetime.now()}] Video ID extracted: {video_id}")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while getting video ID: {str(e)}")
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            print(f"[{datetime.now()}] Fetching transcript in background thread...")

            # Run the blocking operation in a background thread
            fetched_transcript, available_languages = await asyncio.to_thread(
                YouTubeTools._get_transcript_with_fallback, video_id, languages
            )

            print(f"[{datetime.now()}] Available transcript languages: {available_languages}")

            if fetched_transcript:
                print(f"[{datetime.now()}] Transcript fetched successfully")
                print(f"[{datetime.now()}] Transcript info - Language: {fetched_transcript.language}, Code: {fetched_transcript.language_code}, Generated: {fetched_transcript.is_generated}")
                print(f"[{datetime.now()}] Number of snippets: {len(fetched_transcript)}")

                # Extract text from the fetched transcript object
                caption_text = " ".join(snippet.text for snippet in fetched_transcript)
                print(f"[{datetime.now()}] Combined caption text length: {len(caption_text)} characters")
                return caption_text

            print(f"[{datetime.now()}] WARNING: No captions found for video")
            return "No captions found for video"
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while getting captions: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting captions for video: {str(e)}")

    @staticmethod
    @cached(prefix="video_timestamps", ttl=3600)
    async def get_video_timestamps(url: str, languages: Optional[List[str]] = None) -> List[str]:
        """Generate timestamps for a YouTube video based on captions using the new API."""
        print(f"[{datetime.now()}] get_video_timestamps called with URL: {url}, languages: {languages}")

        if not url:
            print(f"[{datetime.now()}] ERROR: No URL provided to get_video_timestamps")
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                print(f"[{datetime.now()}] ERROR: Invalid YouTube URL: {url}")
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
            print(f"[{datetime.now()}] Video ID extracted: {video_id}")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while getting video ID: {str(e)}")
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            print(f"[{datetime.now()}] Fetching transcript in background thread...")

            # Run the blocking operation in a background thread
            fetched_transcript, available_languages = await asyncio.to_thread(
                YouTubeTools._get_transcript_with_fallback, video_id, languages
            )

            print(f"[{datetime.now()}] Available transcript languages: {available_languages}")
            print(f"[{datetime.now()}] Transcript fetched successfully")
            print(f"[{datetime.now()}] Processing {len(fetched_transcript)} snippets into timestamps")

            timestamps = []
            for i, snippet in enumerate(fetched_transcript):
                start = int(snippet.start)
                minutes, seconds = divmod(start, 60)
                timestamp = f"{minutes}:{seconds:02d} - {snippet.text}"
                timestamps.append(timestamp)

                if i < 5:  # Log first 5 timestamps as sample
                    print(f"[{datetime.now()}] Sample timestamp [{i}]: {timestamp}")

            print(f"[{datetime.now()}] Generated {len(timestamps)} timestamps")
            return timestamps
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while generating timestamps: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating timestamps: {str(e)}")

    @staticmethod
    @cached(prefix="video_languages", ttl=3600)
    async def get_video_transcript_languages(url: str) -> List[dict]:
        """List available transcript languages for a video."""
        print(f"[{datetime.now()}] get_video_transcript_languages called with URL: {url}")

        if not url:
            print(f"[{datetime.now()}] ERROR: No URL provided")
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                print(f"[{datetime.now()}] ERROR: Invalid YouTube URL: {url}")
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
            print(f"[{datetime.now()}] Video ID extracted: {video_id}")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while getting video ID: {str(e)}")
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            print(f"[{datetime.now()}] Listing available transcripts in background thread...")

            def list_transcripts(video_id):
                ytt_api = YouTubeTools._create_youtube_api()
                return ytt_api.list(video_id)

            # Run the blocking operation in a background thread
            transcript_list = await asyncio.to_thread(list_transcripts, video_id)

            languages_info = []
            for transcript in transcript_list:
                lang_info = {
                    "language": transcript.language,
                    "language_code": transcript.language_code,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable
                }
                languages_info.append(lang_info)
                print(f"[{datetime.now()}] Found transcript: {transcript.language} ({transcript.language_code}) - Generated: {transcript.is_generated}")

            print(f"[{datetime.now()}] Found {len(languages_info)} available transcript languages")
            return languages_info

        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Exception while listing transcript languages: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing transcript languages: {str(e)}")

class YouTubeRequest(BaseModel):
    url: str
    languages: Optional[List[str]] = None

class VideoNotesRequest(BaseModel):
    url: str
    languages: Optional[List[str]] = None
    format: Optional[str] = "structured"  # structured, summary, or detailed

class VideoTranslateRequest(BaseModel):
    url: str
    target_language: str  # e.g., "Spanish", "French", "Japanese"
    source_languages: Optional[List[str]] = None

@app.post("/video-data")
async def get_video_data(request: YouTubeRequest):
    """Endpoint to get video metadata"""
    print(f"[{datetime.now()}] POST /video-data endpoint called")
    print(f"[{datetime.now()}] Request data: url={request.url}, languages={request.languages}")

    result = YouTubeTools.get_video_data(request.url)
    print(f"[{datetime.now()}] Returning video data response")
    return result

@app.post("/video-captions")
async def get_video_captions(request: YouTubeRequest):
    """Endpoint to get video captions"""
    print(f"[{datetime.now()}] POST /video-captions endpoint called")
    print(f"[{datetime.now()}] Request data: url={request.url}, languages={request.languages}")

    captions = await YouTubeTools.get_video_captions(request.url, request.languages)
    print(f"[{datetime.now()}] Returning captions response")
    return {"captions": captions}

@app.post("/video-timestamps")
async def get_video_timestamps(request: YouTubeRequest):
    """Endpoint to get video timestamps"""
    print(f"[{datetime.now()}] POST /video-timestamps endpoint called")
    print(f"[{datetime.now()}] Request data: url={request.url}, languages={request.languages}")

    timestamps = await YouTubeTools.get_video_timestamps(request.url, request.languages)
    print(f"[{datetime.now()}] Returning timestamps response")
    return {"timestamps": timestamps}

@app.post("/video-transcript-languages")
async def get_video_transcript_languages(request: YouTubeRequest):
    """Endpoint to list available transcript languages for a video"""
    print(f"[{datetime.now()}] POST /video-transcript-languages endpoint called")
    print(f"[{datetime.now()}] Request data: url={request.url}")

    languages_info = await YouTubeTools.get_video_transcript_languages(request.url)
    print(f"[{datetime.now()}] Returning transcript languages response")
    return {"available_languages": languages_info}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify server and proxy status"""
    print(f"[{datetime.now()}] GET /health endpoint called")

    proxy_status = "enabled" if WEBSHARE_PROXY_CONFIG else "disabled"
    proxy_username = os.getenv("WEBSHARE_PROXY_USERNAME", "not_set")

    cache = get_cache()
    cache_status = "enabled" if cache.enabled else "disabled"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "proxy_status": f"webshare_{proxy_status}",
        "proxy_username": proxy_username if WEBSHARE_PROXY_CONFIG else None,
        "cache_status": f"redis_{cache_status}",
        "cache_ttl_seconds": cache.cache_ttl if cache.enabled else None,
        "parallel_processing": "enabled"
    }

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    print(f"[{datetime.now()}] GET /cache/stats endpoint called")
    cache = get_cache()
    return cache.get_stats()

@app.post("/cache/clear")
async def cache_clear():
    """Clear all cached data"""
    print(f"[{datetime.now()}] POST /cache/clear endpoint called")
    cache = get_cache()

    if not cache.enabled:
        return {
            "success": False,
            "message": "Cache is not enabled"
        }

    success = cache.clear_all()
    return {
        "success": success,
        "message": "Cache cleared successfully" if success else "Failed to clear cache",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/video-notes")
async def generate_video_notes(request: VideoNotesRequest):
    """Generate structured notes from a YouTube video transcript"""
    print(f"[{datetime.now()}] POST /video-notes endpoint called")
    print(f"[{datetime.now()}] Request data: url={request.url}, format={request.format}")

    if not ANTHROPIC_CLIENT:
        raise HTTPException(
            status_code=503,
            detail="AI features not available. Please configure ANTHROPIC_API_KEY environment variable."
        )

    try:
        # Get video metadata
        video_data = YouTubeTools.get_video_data(request.url)

        # Get transcript
        captions = await YouTubeTools.get_video_captions(request.url, request.languages)

        # Get timestamps for context
        timestamps = await YouTubeTools.get_video_timestamps(request.url, request.languages)

        print(f"[{datetime.now()}] Generating notes with Claude API...")

        # Create prompt based on format
        if request.format == "summary":
            prompt = f"""Create a concise summary of this YouTube video.

Video Title: {video_data.get('title')}
Channel: {video_data.get('author_name')}

Transcript:
{captions}

Provide:
1. A 2-3 sentence executive summary
2. 3-5 key takeaways as bullet points
3. Main topics covered

Format the response in clean markdown."""

        elif request.format == "detailed":
            prompt = f"""Create detailed notes from this YouTube video transcript.

Video Title: {video_data.get('title')}
Channel: {video_data.get('author_name')}

Transcript:
{captions}

Provide:
1. Executive Summary (3-4 sentences)
2. Detailed outline with main sections and subsections
3. Key concepts explained
4. Important quotes or statements
5. Action items or recommendations (if applicable)

Format the response in clean markdown with proper headings."""

        else:  # structured (default)
            prompt = f"""Convert this YouTube video transcript into well-structured notes.

Video Title: {video_data.get('title')}
Channel: {video_data.get('author_name')}

Transcript:
{captions}

Create structured notes with:
1. Overview: Brief description of video content
2. Main Topics: Organized by sections with key points
3. Key Takeaways: Most important information
4. Conclusion: Final thoughts or summary

Format the response in clean markdown with proper headings and bullet points."""

        # Call Claude API
        message = ANTHROPIC_CLIENT.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        notes = message.content[0].text

        print(f"[{datetime.now()}] Notes generated successfully ({len(notes)} characters)")

        return {
            "video_title": video_data.get('title'),
            "channel": video_data.get('author_name'),
            "format": request.format,
            "notes": notes,
            "word_count": len(notes.split()),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Exception while generating notes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating notes: {str(e)}")

@app.post("/video-translate")
async def translate_video_transcript(request: VideoTranslateRequest):
    """Translate a YouTube video transcript to another language"""
    print(f"[{datetime.now()}] POST /video-translate endpoint called")
    print(f"[{datetime.now()}] Request data: url={request.url}, target_language={request.target_language}")

    if not ANTHROPIC_CLIENT:
        raise HTTPException(
            status_code=503,
            detail="AI features not available. Please configure ANTHROPIC_API_KEY environment variable."
        )

    try:
        # Get video metadata
        video_data = YouTubeTools.get_video_data(request.url)

        # Get transcript
        captions = await YouTubeTools.get_video_captions(request.url, request.source_languages)

        # Get timestamps for alignment
        timestamps = await YouTubeTools.get_video_timestamps(request.url, request.source_languages)

        print(f"[{datetime.now()}] Translating transcript to {request.target_language} with Claude API...")

        prompt = f"""Translate this YouTube video transcript to {request.target_language}.

Video Title: {video_data.get('title')}
Channel: {video_data.get('author_name')}

Original Transcript:
{captions}

Requirements:
1. Translate the entire transcript naturally and accurately
2. Maintain the original tone and style
3. Preserve technical terms appropriately
4. Keep the translation conversational as if spoken
5. Do not add explanations or notes - only provide the translation

Provide ONLY the translated transcript, nothing else."""

        # Call Claude API
        message = ANTHROPIC_CLIENT.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        translated_text = message.content[0].text

        # Also translate timestamps
        print(f"[{datetime.now()}] Translating timestamps...")

        # Sample first 20 timestamps for translation (to keep costs reasonable)
        sample_timestamps = timestamps[:20] if len(timestamps) > 20 else timestamps
        timestamps_text = "\n".join(sample_timestamps)

        timestamp_prompt = f"""Translate these video timestamps to {request.target_language}.

Original Timestamps:
{timestamps_text}

Requirements:
1. Keep the timestamp format (MM:SS - text)
2. Only translate the text part, not the timestamps
3. Maintain natural speech patterns
4. Provide ONLY the translated timestamps, one per line

Translated timestamps:"""

        timestamp_message = ANTHROPIC_CLIENT.messages.create(
            model="claude-3-5-haiku-20241022",  # Use Haiku for faster/cheaper timestamp translation
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": timestamp_prompt
            }]
        )

        translated_timestamps = timestamp_message.content[0].text.strip().split('\n')

        print(f"[{datetime.now()}] Translation completed successfully")

        return {
            "video_title": video_data.get('title'),
            "channel": video_data.get('author_name'),
            "target_language": request.target_language,
            "translated_transcript": translated_text,
            "translated_timestamps": translated_timestamps,
            "word_count": len(translated_text.split()),
            "timestamp": datetime.now().isoformat(),
            "note": "Use this translated transcript with ElevenLabs voice cloning for dubbed audio"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Exception while translating transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error translating transcript: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "YouTube Tools API",
        "version": "1.1.0",
        "endpoints": {
            "GET /": "This info",
            "GET /health": "Health check",
            "GET /cache/stats": "Cache statistics",
            "POST /cache/clear": "Clear cache",
            "POST /video-data": "Get video metadata (cached)",
            "POST /video-captions": "Get video captions/transcripts (cached)",
            "POST /video-timestamps": "Get timestamped transcripts (cached)",
            "POST /video-transcript-languages": "List available languages (cached)",
            "POST /video-notes": "Generate structured notes from video (requires ANTHROPIC_API_KEY)",
            "POST /video-translate": "Translate video transcript (requires ANTHROPIC_API_KEY)"
        },
        "docs": "/docs",
        "ai_features_available": ANTHROPIC_CLIENT is not None
    }

if __name__ == "__main__":
    # Use environment variable for port, default to 8000 if not set
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"[{datetime.now()}] ========================================")
    print(f"[{datetime.now()}] Starting YouTube API Server")
    print(f"[{datetime.now()}] Host: {host}")
    print(f"[{datetime.now()}] Port: {port}")

    if WEBSHARE_PROXY_CONFIG:
        username = os.getenv("WEBSHARE_PROXY_USERNAME", "unknown")
        print(f"[{datetime.now()}] Proxy: Webshare enabled (username: {username})")
    else:
        print(f"[{datetime.now()}] Proxy: Disabled - set WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD to enable")

    print(f"[{datetime.now()}] Environment Variables:")
    print(f"[{datetime.now()}]   - WEBSHARE_PROXY_USERNAME: {'Set' if os.getenv('WEBSHARE_PROXY_USERNAME') else 'Not Set'}")
    print(f"[{datetime.now()}]   - WEBSHARE_PROXY_PASSWORD: {'Set' if os.getenv('WEBSHARE_PROXY_PASSWORD') else 'Not Set'}")
    print(f"[{datetime.now()}] ========================================")

    uvicorn.run(app, host=host, port=port)
