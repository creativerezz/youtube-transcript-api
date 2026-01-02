# Services Documentation

This document explains how each service is used in the YouTube Summaries API project, including connection methods, configuration, and integration details.

## Table of Contents

- [Railway (Deployment Platform)](#railway-deployment-platform)
- [Redis (Caching Layer)](#redis-caching-layer)
- [Cloudflare Workers (Edge Services)](#cloudflare-workers-edge-services)
- [Supabase (Database/Backend)](#supabase-databasebackend)
- [GitHub Repositories](#github-repositories)

---

## Railway (Deployment Platform)

### Purpose

Railway is the primary deployment platform for the FastAPI application. It hosts both the main API server and the Redis caching service.

### Project Information

- **Project ID**: `8f6a7da7-ccc0-49b7-ba09-cc932b93d39b`
- **Link Command**: 
  ```bash
  railway link -p 8f6a7da7-ccc0-49b7-ba09-cc932b93d39b
  ```

### Usage

Railway provides:
- **Application Hosting**: Deploys the FastAPI server automatically from GitHub
- **Redis Service**: Managed Redis instance for caching
- **Environment Variables**: Secure configuration management
- **Auto-deployment**: Automatic deployments on git push
- **Logging & Monitoring**: Built-in log viewing and metrics

### Configuration

The application is configured for Railway via:
- **`nixpacks.toml`**: Defines the build process (Python 3.12, uv package manager)
- **`Procfile`**: Backup start command configuration
- **Environment Variables**: Set via Railway dashboard or CLI

### Redis Integration

Redis is provisioned as a separate service within the Railway project:
- Railway automatically creates a `REDIS_URL` environment variable
- The API service references it via: `REDIS_URL=${{Redis.REDIS_URL}}`
- Both services run in the same Railway project for network connectivity

### Connection Methods

**Link to Railway Project:**
```bash
railway link -p 8f6a7da7-ccc0-49b7-ba09-cc932b93d39b
```

**Connect to Redis Service:**
```bash
railway connect Redis
```

**View Logs:**
```bash
railway logs --follow
```

**Set Environment Variables:**
```bash
railway variables set KEY=value
```

### Documentation

For detailed deployment instructions, see:
- [Railway Deployment Guide](../deployment/RAILWAY_DEPLOYMENT.md)
- [Enable Redis on Railway](../deployment/ENABLE_REDIS_ON_RAILWAY.md)
- [Railway Redis Quick Start](../deployment/RAILWAY_REDIS_QUICK_START.md)

---

## Redis (Caching Layer)

### Purpose

Redis provides high-performance caching for YouTube API responses, dramatically improving response times and reducing API calls.

### Implementation

The Redis caching layer is implemented in:
- **Service**: [`src/youtube_api/services/cache.py`](../../src/youtube_api/services/cache.py)
- **Storage**: [`src/youtube_api/services/storage.py`](../../src/youtube_api/services/storage.py)
- **Configuration**: [`src/youtube_api/config.py`](../../src/youtube_api/config.py)

### Connection Details

**Connection URL:**
```
redis://default:YjxVPvvpKLskUcKvusxcIFrgaPRgQCPF@shortline.proxy.rlwy.net:40311
```

### Connection Methods

**Via Railway CLI:**
```bash
railway connect Redis
```

**Via redis-cli (Direct Connection):**
```bash
redis-cli -u redis://default:YjxVPvvpKLskUcKvusxcIFrgaPRgQCPF@shortline.proxy.rlwy.net:40311
```

### What Gets Cached

The following endpoints are cached with a 1-hour TTL (configurable):

1. **Video Metadata** (`POST /video-data`)
   - Title, author, thumbnails, duration, etc.
   - Cache key format: `youtube_api:video_data:{hash}`

2. **Video Transcripts** (`POST /video-captions`)
   - Full transcript text with language support
   - Cache key format: `youtube_api:captions:{hash}`

3. **Timestamped Transcripts** (`POST /video-timestamps`)
   - Transcripts with timing information
   - Cache key format: `youtube_api:timestamps:{hash}`

4. **Available Languages** (`POST /video-transcript-languages`)
   - List of available transcript languages
   - Cache key format: `youtube_api:languages:{hash}`

### Persistent Storage

Redis also provides persistent transcript storage via the storage service:
- **Storage Endpoints**: `/transcripts/save`, `/transcripts/get`, `/transcripts/list`
- **Storage Keys**: `transcript_storage:{video_id}:{language}`
- **Metadata Keys**: `transcript_metadata:{video_id}`
- **TTL**: 10 years (effectively permanent)

### Cache Behavior

- **TTL**: Default 3600 seconds (1 hour), configurable via `CACHE_TTL_SECONDS`
- **Key Generation**: Automatic hash-based keys from function arguments
- **Graceful Degradation**: Application works normally if Redis is unavailable
- **Cache Statistics**: Available via `GET /cache/stats` endpoint

### Configuration

**Environment Variables:**
- `REDIS_URL`: Redis connection URL (required for caching)
- `CACHE_TTL_SECONDS`: Cache expiration time in seconds (default: 3600)

**In Railway:**
The `REDIS_URL` is automatically set when Redis service is added:
```bash
railway variables set REDIS_URL='${{Redis.REDIS_URL}}'
```

### Performance Benefits

- **10-56x faster** response times for cached requests
- **Reduced API calls** to YouTube's servers
- **Lower bandwidth usage** and proxy costs
- **Shared cache** across multiple server instances

### Monitoring

**Check Cache Status:**
```bash
curl https://your-api.railway.app/cache/stats
```

**View Cache Statistics:**
- `keyspace_hits`: Number of successful cache retrievals
- `keyspace_misses`: Number of cache misses
- `total_keys`: Number of cached items
- `hit_rate`: `hits / (hits + misses)` - aim for > 80%

### Documentation

For detailed setup and configuration, see:
- [Redis Setup Guide](../setup/REDIS_SETUP.md)
- [Caching Improvements](../setup/CACHING_IMPROVEMENTS.md)

---

## Cloudflare Workers (Edge Services)

### Purpose

Cloudflare Workers provide edge-cached services that complement the main API. These are separate services that may integrate with the main API or serve as standalone edge endpoints.

### Services

1. **Transcript Storage Worker**
   - **URL**: `https://youtube-transcript-storage.automatehub.workers.dev/`
   - **Purpose**: Edge-cached transcript storage service
   - **Usage**: Likely used for fast global access to stored transcripts

2. **AI Platform Edge Worker**
   - **URL**: `https://youtube-ai-platform-edge-worker.automatehub.workers.dev/#/YouTube`
   - **Purpose**: Edge-cached AI platform worker for YouTube features
   - **Usage**: Provides AI-powered features at the edge

### Integration Status

These services are **external** to the main API codebase:
- Not directly integrated in the FastAPI application
- May be used by frontend applications or other services
- Provide edge caching and global distribution
- Likely part of a larger ecosystem of services

### Notes

- These workers are hosted on Cloudflare's edge network
- They provide low-latency access from anywhere in the world
- May integrate with the main API or serve as alternative endpoints
- Configuration and management are separate from the main Railway deployment

---

## Supabase (Database/Backend)

### Purpose

Supabase provides database and backend services, likely for a frontend application or separate service that uses the YouTube Summaries API.

### Configuration

**Supabase URL:**
```
https://wofbgydhrsdnolrvtzbc.supabase.co
```

**Publishable Key:**
```
sb_publishable_DrdCSjy12dIWe6bAA4h_pg_WjgmYDrO
```

### Environment Variables

For frontend applications using Supabase:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://wofbgydhrsdnolrvtzbc.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=sb_publishable_DrdCSjy12dIWe6bAA4h_pg_WjgmYDrO
```

### Integration Status

Supabase is **not directly used** in the main API codebase:
- Likely used by a frontend application (Next.js, React, etc.)
- May store user data, preferences, or application state
- Could be used for authentication or user management
- Separate from the FastAPI backend service

### Notes

- These credentials are for a frontend/separate service
- The main API server does not require Supabase configuration
- Supabase may be used for building a web interface or mobile app
- Keep these credentials secure and use environment variables

---

## GitHub Repositories

### Purpose

GitHub repositories host the source code and enable version control, collaboration, and automated deployments.

### Repositories

1. **youtube-summaries-api** (Current Project)
   - **URL**: `https://github.com/creativerezz/youtube-summaries-api`
   - **Purpose**: Main API server (this project)
   - **Description**: FastAPI-based YouTube transcript extraction, summaries, and AI-powered features API with Redis caching

2. **fast-youtube-proxy**
   - **URL**: `https://github.com/creativerezz/fast-youtube-proxy`
   - **Purpose**: Proxy service for YouTube API access
   - **Description**: Likely used to avoid IP blocking and rate limits

3. **youtubesummaries**
   - **URL**: `https://github.com/creativerezz/youtubesummaries`
   - **Purpose**: Related project for YouTube video summarization
   - **Description**: May use the transcript API for generating summaries

### Integration

**Railway Auto-Deployment:**
- Railway is connected to the main repository
- Pushes to the main branch trigger automatic deployments
- No manual deployment steps required

**Version Control:**
- All code changes are tracked in Git
- Pull requests for code review
- Issue tracking for bugs and features

### Usage

**Clone Repository:**
```bash
git clone https://github.com/creativerezz/youtube-summaries-api.git
cd youtube-summaries-api
```

**Check Deployment Status:**
- Railway automatically deploys from GitHub
- Check Railway dashboard for deployment logs
- See [Deployment Status](../deployment/DEPLOYMENT_STATUS.md) for details

---

## Service Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repositories                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │ youtube-transcript│  │ fast-youtube-proxy│ │youtubesummaries│
│  │     -api         │  │                  │ │             │ │
│  └──────────────────┘  └──────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Auto-deploy
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Railway Platform                          │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │   FastAPI Server     │◄────►│   Redis Service      │   │
│  │  (Main Application)   │      │   (Caching Layer)    │   │
│  └──────────────────────┘      └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare Workers (Edge)                      │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │ Transcript Storage  │      │  AI Platform Worker   │   │
│  │      Worker         │      │                       │   │
│  └──────────────────────┘      └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (Optional)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supabase (Frontend)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database & Backend Services                         │  │
│  │  (For frontend applications)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### Railway Commands
```bash
# Link to project
railway link -p 8f6a7da7-ccc0-49b7-ba09-cc932b93d39b

# Connect to Redis
railway connect Redis

# View logs
railway logs --follow

# Set variables
railway variables set KEY=value
```

### Redis Commands
```bash
# Direct connection
redis-cli -u redis://default:YjxVPvvpKLskUcKvusxcIFrgaPRgQCPF@shortline.proxy.rlwy.net:40311

# Via Railway
railway connect Redis
```

### Service URLs
- **Railway API**: Check Railway dashboard for deployment URL
- **Redis**: `redis://default:YjxVPvvpKLskUcKvusxcIFrgaPRgQCPF@shortline.proxy.rlwy.net:40311`
- **Cloudflare Workers**: 
  - Transcript Storage: `https://youtube-transcript-storage.automatehub.workers.dev/`
  - AI Platform: `https://youtube-ai-platform-edge-worker.automatehub.workers.dev/#/YouTube`
- **Supabase**: `https://wofbgydhrsdnolrvtzbc.supabase.co`

---

## Security Notes

⚠️ **Important**: The credentials in this documentation are sensitive:
- **Redis Password**: Keep the Redis connection URL secure
- **Supabase Keys**: Use environment variables, never commit to Git
- **Service URLs**: Some may contain authentication tokens

**Best Practices:**
- Use environment variables for all credentials
- Never commit secrets to version control
- Rotate credentials regularly
- Use Railway's secure variable management
- Restrict access to service dashboards

---

## Troubleshooting

### Railway Connection Issues
- Verify Railway CLI is installed: `railway --version`
- Check authentication: `railway whoami`
- Ensure project ID is correct

### Redis Connection Issues
- Verify Redis service is running in Railway dashboard
- Check `REDIS_URL` environment variable is set
- Test connection: `railway connect Redis`
- Review logs: `railway logs`

### Service Integration Issues
- Verify environment variables are set correctly
- Check service status in Railway dashboard
- Review application logs for connection errors
- Ensure services are in the same Railway project

For more detailed troubleshooting, see:
- [Railway Deployment Guide](../deployment/RAILWAY_DEPLOYMENT.md)
- [Redis Setup Guide](../setup/REDIS_SETUP.md)
