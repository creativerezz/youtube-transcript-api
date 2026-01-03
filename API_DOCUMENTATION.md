# YouTube Summaries API - Complete Documentation

## Overview

A comprehensive FastAPI-based service for extracting, processing, and analyzing YouTube video transcripts with AI-powered features.

**Base URL:** `http://localhost:8000` (development)
**API Version:** 2.0.0
**Documentation:** `/docs` (Swagger UI) or `/redoc` (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Response Format](#response-format)
4. [Health & Cache Management](#health--cache-management)
5. [Video Data & Transcripts](#video-data--transcripts)
6. [AI-Powered Features](#ai-powered-features)
7. [Transcript Storage](#transcript-storage)
8. [Prompt Management](#prompt-management)
9. [Error Codes](#error-codes)
10. [Configuration](#configuration)

---

## Authentication

Most endpoints are public. AI-powered endpoints require the `OPENROUTER_API_KEY` environment variable to be configured.

**Required for:**
- `/video-notes`
- `/video-translate`
- `/openrouter-proxy`

---

## Rate Limiting

Rate limits are enforced per IP address:

| Tier | Limit | Applies To |
|------|-------|------------|
| Standard | 60/minute | Video data, captions, timestamps, languages, storage retrieval |
| Storage | 30/minute | Save, delete, list, stats, proxy |
| AI | 10/minute | Notes generation, translation |
| None | Unlimited | Health, cache stats, prompts |

**Rate Limit Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

---

## Response Format

All endpoints return JSON responses with appropriate HTTP status codes.

**Success Response (2xx):**
```json
{
  "status": "success",
  "data": {...}
}
```

**Error Response (4xx/5xx):**
```json
{
  "detail": "Error message description"
}
```

---

## Health & Cache Management

### GET `/`

Get API information and available endpoints.

**Response:**
```json
{
  "name": "YouTube Summaries API",
  "version": "2.0.0",
  "endpoints": {...},
  "docs": "/docs",
  "ai_features_available": true
}
```

**Status Codes:**
- `200 OK`: Success

---

### GET `/health`

Health check endpoint with service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-02T10:30:00",
  "proxy_status": "webshare_enabled",
  "proxy_username": "user123",
  "cache_status": "redis_enabled",
  "cache_ttl_seconds": 3600,
  "parallel_processing": "enabled"
}
```

**Status Codes:**
- `200 OK`: All services healthy

---

### GET `/cache/stats`

Get cache statistics and performance metrics.

**Response:**
```json
{
  "enabled": true,
  "total_keys": 1234,
  "hits": 5678,
  "misses": 890,
  "hit_rate": 0.864,
  "ttl_seconds": 3600
}
```

**Status Codes:**
- `200 OK`: Success

---

### POST `/cache/clear`

Clear all cached data.

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully",
  "timestamp": "2025-01-02T10:30:00"
}
```

**Status Codes:**
- `200 OK`: Cache cleared
- `400 Bad Request`: Cache not enabled

---

## Video Data & Transcripts

### POST `/video-data`

Get YouTube video metadata using oEmbed API.

**Rate Limit:** 60/minute

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "title": "Video Title",
  "author_name": "Channel Name",
  "author_url": "https://www.youtube.com/channel/...",
  "type": "video",
  "height": 113,
  "width": 200,
  "version": "1.0",
  "provider_name": "YouTube",
  "provider_url": "https://www.youtube.com/",
  "thumbnail_height": 360,
  "thumbnail_width": 480,
  "thumbnail_url": "https://i.ytimg.com/vi/...",
  "html": "<iframe width=\"200\" height=\"113\" src=\"...\"></iframe>"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid URL
- `404 Not Found`: Video not found
- `429 Too Many Requests`: Rate limit exceeded

---

### POST `/video-captions`

Get video transcript as plain text.

**Rate Limit:** 60/minute

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "languages": ["en", "es"]  // Optional, defaults to auto-detect
}
```

**Response:**
```json
{
  "captions": "Full transcript text here..."
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid URL
- `404 Not Found`: Transcript not available
- `429 Too Many Requests`: Rate limit exceeded

---

### POST `/video-timestamps`

Get timestamped transcript segments.

**Rate Limit:** 60/minute

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "languages": ["en"]
}
```

**Response:**
```json
{
  "timestamps": [
    "00:00 - Introduction to the topic",
    "01:23 - First main point",
    "03:45 - Second main point"
  ]
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid URL
- `404 Not Found`: Transcript not available

---

### POST `/video-transcript-languages`

List available transcript languages for a video.

**Rate Limit:** 60/minute

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "available_languages": [
    {
      "language": "English",
      "language_code": "en",
      "is_generated": false,
      "is_translatable": true
    },
    {
      "language": "Spanish",
      "language_code": "es",
      "is_generated": true,
      "is_translatable": false
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid URL

---

## AI-Powered Features

### POST `/video-notes`

Generate structured notes from video transcript using AI.

**Rate Limit:** 10/minute
**Requires:** `OPENROUTER_API_KEY`

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "languages": ["en"],
  "format": "structured"  // Options: "structured", "summary", "detailed"
}
```

**Response:**
```json
{
  "video_title": "Video Title",
  "channel": "Channel Name",
  "format": "structured",
  "notes": "# Main Ideas\n\n- Point 1...",
  "word_count": 450,
  "timestamp": "2025-01-02T10:30:00"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid URL or format
- `404 Not Found`: Transcript not available
- `500 Internal Server Error`: AI service unavailable
- `503 Service Unavailable`: OpenRouter API key not configured

---

### POST `/video-translate`

Translate video transcript to another language.

**Rate Limit:** 10/minute
**Requires:** `OPENROUTER_API_KEY`

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "source_languages": ["en"],
  "target_language": "Spanish"
}
```

**Response:**
```json
{
  "video_title": "Video Title",
  "channel": "Channel Name",
  "target_language": "Spanish",
  "translated_transcript": "Texto traducido...",
  "translated_timestamps": [
    "00:00 - Introducción al tema",
    "01:23 - Primer punto principal"
  ],
  "word_count": 423,
  "timestamp": "2025-01-02T10:30:00",
  "note": "Use this translated transcript with ElevenLabs voice cloning for dubbed audio"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `503 Service Unavailable`: AI service unavailable

---

### POST `/openrouter-proxy`

Proxy endpoint for direct OpenRouter API access.

**Rate Limit:** 30/minute
**Requires:** `OPENROUTER_API_KEY`

**Request Body:**
```json
{
  "prompt": "Your question or instruction",
  "model": "xiaomi/mimo-v2-flash:free",  // Optional
  "max_tokens": 1000  // Optional, default: 1000
}
```

**Response:**
```json
{
  "response": {
    "id": "chatcmpl-...",
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "AI response here..."
        },
        "finish_reason": "stop"
      }
    ],
    "model": "xiaomi/mimo-v2-flash:free",
    "usage": {
      "prompt_tokens": 15,
      "completion_tokens": 120,
      "total_tokens": 135
    }
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: OpenRouter API error

---

## Transcript Storage

### POST `/transcripts/save`

Save transcript to persistent Redis storage.

**Rate Limit:** 30/minute
**Requires:** Redis configured

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "languages": ["en"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transcript saved successfully",
  "video_id": "VIDEO_ID"
}
```

**Status Codes:**
- `200 OK`: Success (check `success` field)

---

### POST `/transcripts/get`

Retrieve stored transcript from Redis.

**Rate Limit:** 60/minute

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "languages": ["en"]
}
```

**Response:**
```json
{
  "video_id": "VIDEO_ID",
  "transcript": "Full transcript text...",
  "language": "en",
  "metadata": {
    "title": "Video Title",
    "author": "Channel Name",
    "thumbnail_url": "https://..."
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Transcript not in storage

---

### GET `/transcripts/list`

List all stored transcripts.

**Rate Limit:** 30/minute

**Response:**
```json
{
  "videos": [
    {
      "video_id": "VIDEO_ID_1",
      "title": "Video Title 1",
      "author": "Channel 1",
      "languages": ["en", "es"]
    }
  ],
  "count": 1
}
```

**Status Codes:**
- `200 OK`: Success

---

### POST `/transcripts/delete`

Delete stored transcript.

**Rate Limit:** 30/minute

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "languages": ["en"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transcript deleted successfully",
  "video_id": "VIDEO_ID"
}
```

**Status Codes:**
- `200 OK`: Success

---

### GET `/transcripts/stats`

Get storage statistics.

**Rate Limit:** 30/minute

**Response:**
```json
{
  "total_videos": 45,
  "total_transcripts": 67,
  "storage_enabled": true,
  "languages": ["en", "es", "fr"]
}
```

**Status Codes:**
- `200 OK`: Success

---

## Prompt Management

### GET `/prompts/`

List all available Fabric-style prompt templates.

**Response:**
```json
{
  "total": 30,
  "categories": ["extraction", "business", "development"],
  "prompts": [
    {
      "name": "extract_ideas",
      "category": "extraction",
      "path": "/path/to/prompt"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Success

---

### GET `/prompts/categories`

List prompt categories with counts.

**Response:**
```json
{
  "categories": ["extraction", "business", "development"],
  "counts": {
    "extraction": 12,
    "business": 8,
    "development": 10
  },
  "total_categories": 3
}
```

**Status Codes:**
- `200 OK`: Success

---

### GET `/prompts/category/{category}`

Get all prompts in a specific category.

**Parameters:**
- `category` (path): Category name

**Response:**
```json
{
  "category": "extraction",
  "count": 12,
  "prompts": [...]
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Category not found

---

### GET `/prompts/{name}`

Get full prompt template content.

**Parameters:**
- `name` (path): Prompt name

**Response:**
```json
{
  "name": "extract_ideas",
  "category": "extraction",
  "content": "# IDENTITY\n\nYou are an expert..."
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Prompt not found

---

### POST `/prompts/refresh`

Refresh prompt cache (reload from filesystem).

**Response:**
```json
{
  "message": "Prompt cache refreshed successfully",
  "total_prompts": 30
}
```

**Status Codes:**
- `200 OK`: Success

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Request successful |
| `400 Bad Request` | Invalid request parameters or URL |
| `404 Not Found` | Resource not found (video, transcript, prompt) |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Server error |
| `503 Service Unavailable` | Required service not configured |

**Common Error Messages:**
- `"Invalid YouTube URL"`: URL format is incorrect
- `"Video not found"`: YouTube video doesn't exist or is unavailable
- `"Transcript not available"`: No transcript found for video
- `"AI service unavailable"`: OpenRouter API key not configured
- `"Storage is not enabled"`: Redis not configured

---

## Configuration

### Environment Variables

```bash
# Required for AI features
OPENROUTER_API_KEY=your_api_key_here

# Optional: Redis for caching and storage
REDIS_URL=redis://localhost:6379/0

# Optional: Webshare proxy for rate limiting bypass
WEBSHARE_PROXY_USERNAME=your_username
WEBSHARE_PROXY_PASSWORD=your_password

# Optional: Server configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

### Cache Configuration

- **Default TTL:** 3600 seconds (1 hour)
- **Cache Strategy:** Redis-backed with automatic invalidation
- **Cached Endpoints:** All video data and transcript endpoints

### Proxy Configuration

When configured, the API uses Webshare rotating proxies to bypass YouTube rate limits:
- Automatic rotation per request
- Fallback to direct connection if proxy fails
- Status visible in `/health` endpoint

---

## Examples

### Basic Video Data Fetch
```bash
curl -X POST http://localhost:8000/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Generate Video Notes
```bash
curl -X POST http://localhost:8000/video-notes \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "structured"
  }'
```

### List Available Languages
```bash
curl -X POST http://localhost:8000/video-transcript-languages \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

---

## Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation:** `/docs` (Swagger UI)
- **Interactive API Explorer:** `/redoc` (ReDoc)

---

**Last Updated:** 2025-01-02
**API Version:** 2.0.0
