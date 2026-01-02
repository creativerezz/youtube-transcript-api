# Local Development Setup Guide

This guide explains how to set up your local development environment and test the YouTube Summaries API endpoints.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- Railway CLI installed and authenticated
- Redis (optional, for caching)

## Quick Start

### 1. Pull Environment Variables from Railway

Use the provided script to pull environment variables from your Railway project:

```bash
./scripts/pull-env-from-railway.sh
```

This script will:
- Link to your Railway project (if not already linked)
- Pull environment variables from Railway
- Create a `.env` file with Redis configuration from `Services.md`
- Add common optional variables as comments

**Note**: The script requires a Railway service to be linked. If you see a warning about no service being linked, you can:
- Link a service manually: `railway service`
- Or manually add variables to the `.env` file

### 2. Review and Configure `.env` File

After running the script, review the generated `.env` file and add any missing variables:

```bash
# Required for Redis caching
REDIS_URL=redis://default:password@host:port

# Optional: Proxy Configuration (Webshare)
WEBSHARE_PROXY_USERNAME=your-username
WEBSHARE_PROXY_PASSWORD=your-password

# Optional: AI Features (OpenRouter)
OPENROUTER_API_KEY=your-api-key

# Optional: Cache Configuration
CACHE_TTL_SECONDS=3600
```

### 3. Start the Server

Start the development server:

```bash
# Default port 8000
uv run main.py

# Or specify custom port
PORT=8001 HOST=127.0.0.1 uv run main.py
```

The server will be available at:
- API: `http://localhost:8000` (or your custom port)
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Testing Endpoints

### Quick Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-02T15:30:11.087921",
  "proxy_status": "webshare_disabled",
  "cache_status": "redis_enabled",
  "cache_ttl_seconds": 3600,
  "parallel_processing": "enabled"
}
```

### Run Full Test Suite

Test all endpoints using the provided test script:

```bash
# Test against default localhost:8000
./scripts/test_endpoints.sh

# Or specify custom server URL
./scripts/test_endpoints.sh http://127.0.0.1:8001
```

The test script covers:
- ✅ Health check
- ✅ Video metadata (`/video-data`)
- ✅ Available languages (`/video-transcript-languages`)
- ✅ Video captions (`/video-captions`)
- ✅ Video timestamps (`/video-timestamps`)
- ✅ Error handling
- ✅ Invalid inputs

### Test AI Endpoints

Test AI-powered endpoints (requires `OPENROUTER_API_KEY`):

```bash
BASE_URL=http://localhost:8000 ./scripts/test_new_endpoints.sh
```

**Note**: AI endpoints require `OPENROUTER_API_KEY` to be set in your `.env` file.

## Available Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check with service status
- `GET /cache/stats` - Cache statistics
- `POST /cache/clear` - Clear all cached data

### Video Endpoints

- `POST /video-data` - Get video metadata (cached)
- `POST /video-captions` - Get video captions/transcripts (cached)
- `POST /video-timestamps` - Get timestamped transcripts (cached)
- `POST /video-transcript-languages` - List available languages (cached)

### AI Endpoints (Requires OPENROUTER_API_KEY)

- `POST /video-notes` - Generate structured notes from video
- `POST /video-translate` - Translate video transcript

### Storage Endpoints

- `POST /transcripts/save` - Save transcript to persistent storage
- `POST /transcripts/get` - Retrieve stored transcript
- `GET /transcripts/list` - List all stored transcripts
- `POST /transcripts/delete` - Delete stored transcript
- `GET /transcripts/stats` - Get storage statistics

## Environment Variables

### Required

None (server works without any configuration, but caching improves performance)

### Optional but Recommended

- `REDIS_URL` - Redis connection URL for caching
  - Format: `redis://default:password@host:port`
  - Get from Railway dashboard or `Services.md`

### Optional

- `WEBSHARE_PROXY_USERNAME` - Webshare proxy username
- `WEBSHARE_PROXY_PASSWORD` - Webshare proxy password
- `OPENROUTER_API_KEY` - OpenRouter API key for AI features
- `CACHE_TTL_SECONDS` - Cache expiration time (default: 3600)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `JSON_LOGS` - Enable JSON logging (default: false)

## Railway Integration

### Link Project

```bash
railway link -p 8f6a7da7-ccc0-49b7-ba09-cc932b93d39b
```

### Link Service

```bash
railway service
# Select your service from the list
```

### Pull Variables

```bash
./scripts/pull-env-from-railway.sh
```

### View Variables

```bash
railway variables
```

### Set Variables

```bash
railway variables set OPENROUTER_API_KEY=your-key
```

## Troubleshooting

### Server Won't Start

1. Check if port is already in use:
   ```bash
   lsof -ti:8000
   ```
2. Use a different port:
   ```bash
   PORT=8001 uv run main.py
   ```

### Redis Connection Issues

1. Verify Redis URL is correct in `.env`
2. Test Redis connection:
   ```bash
   redis-cli -u $REDIS_URL ping
   ```
3. Check cache status:
   ```bash
   curl http://localhost:8000/cache/stats
   ```

### AI Endpoints Return 503

AI endpoints require `OPENROUTER_API_KEY`. Check:
1. Variable is set in `.env`
2. Key is valid
3. Server was restarted after adding the key

### Tests Fail

1. Ensure server is running:
   ```bash
   curl http://localhost:8000/health
   ```
2. Check server logs for errors
3. Verify environment variables are loaded

## Next Steps

- Review [API Documentation](api/QUICK_REFERENCE.md) for detailed endpoint usage
- Check [Deployment Guide](deployment/RAILWAY_DEPLOYMENT.md) for production setup
- See [Redis Setup](setup/REDIS_SETUP.md) for caching configuration
