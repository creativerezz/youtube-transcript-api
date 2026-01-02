# Redis Caching Setup Guide

This guide explains how to enable and configure Redis caching for the YouTube API Server.

## Overview

Redis caching significantly improves performance by:
- **Reducing API calls**: Cached responses avoid repeated calls to YouTube's APIs
- **Faster response times**: Cached data returns instantly instead of waiting for API responses
- **Cost savings**: Reduces proxy bandwidth usage and API rate limiting
- **Scalability**: Shared cache across multiple server instances

## Cache Behavior

All endpoints are cached with a 1-hour TTL (configurable):
- `POST /video-data` - Video metadata (title, author, thumbnail, etc.)
- `POST /video-captions` - Full video transcripts
- `POST /video-timestamps` - Timestamped transcripts
- `POST /video-transcript-languages` - Available language options

Cache keys are generated from the request URL and language parameters, so different URLs or language combinations are cached separately.

## Local Development Setup

### Option 1: Run Redis with Docker

```bash
# Start Redis container
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Set Redis URL in .env
echo "REDIS_URL=redis://localhost:6379" >> .env

# Optional: Set custom TTL (default: 3600 seconds = 1 hour)
echo "CACHE_TTL_SECONDS=3600" >> .env
```

### Option 2: Install Redis Locally

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
echo "REDIS_URL=redis://localhost:6379" >> .env
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
echo "REDIS_URL=redis://localhost:6379" >> .env
```

### Option 3: Disable Caching (Development)

Simply leave `REDIS_URL` empty or unset in your `.env` file. The server will work normally without caching.

```bash
# In .env file
REDIS_URL=
```

## Railway Deployment Setup

Railway provides managed Redis as a service. Here's how to set it up:

### Step 1: Add Redis Service

```bash
# Make sure you're in your project directory
cd /path/to/youtube-summaries-api

# Login to Railway (if not already)
railway login

# Link your project (if not already linked)
railway link

# Add Redis service to your project
railway add --plugin redis
```

Alternatively, use the Railway dashboard:
1. Go to your project at https://railway.app
2. Click **"+ New"**
3. Select **"Database" → "Add Redis"**

### Step 2: Configure Environment Variables

Railway automatically creates a `REDIS_URL` variable when you add Redis. You need to make it available to your API service:

**Via Railway CLI:**
```bash
# The Redis service creates a REDIS_URL, reference it in your API service
railway variables --set REDIS_URL='${{Redis.REDIS_URL}}'

# Optional: Set custom cache TTL
railway variables --set CACHE_TTL_SECONDS=3600
```

**Via Railway Dashboard:**
1. Open your project
2. Click on your API service
3. Go to **"Variables"** tab
4. Click **"+ New Variable"**
5. Add: `REDIS_URL` = `${{Redis.REDIS_URL}}` (reference to Redis service)
6. Optional: Add `CACHE_TTL_SECONDS` = `3600`

### Step 3: Deploy

```bash
# Deploy changes
railway up

# Or if already deployed, redeploy to pick up new variables
railway redeploy
```

### Step 4: Verify Redis Connection

```bash
# Check health endpoint
curl https://your-app.railway.app/health

# You should see:
# {
#   "status": "healthy",
#   "cache_status": "redis_enabled",
#   "cache_ttl_seconds": 3600,
#   ...
# }

# Check cache statistics
curl https://your-app.railway.app/cache/stats
```

## Cache Management

### View Cache Statistics

```bash
curl https://your-api-url/cache/stats
```

Response:
```json
{
  "enabled": true,
  "status": "connected",
  "total_keys": 42,
  "ttl_seconds": 3600,
  "keyspace_hits": 156,
  "keyspace_misses": 42
}
```

### Clear Cache

```bash
curl -X POST https://your-api-url/cache/clear
```

Response:
```json
{
  "success": true,
  "message": "Cache cleared successfully",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Monitor Cache Performance

Watch your logs to see cache hits and misses:

```bash
# Railway
railway logs

# Look for lines like:
# [timestamp] Cache HIT: youtube_api:video_data:abc123
# [timestamp] Cache MISS: youtube_api:video_data:def456
# [timestamp] Cache SET: youtube_api:video_data:def456 (TTL: 3600s)
```

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | - | Redis connection URL. Leave empty to disable caching. |
| `CACHE_TTL_SECONDS` | No | 3600 | How long to cache responses (in seconds). |

### Cache TTL Recommendations

- **1 hour (3600)**: Good default - balances freshness and performance
- **24 hours (86400)**: Maximum performance, use if content rarely changes
- **15 minutes (900)**: More aggressive, use if you need fresher data
- **Development**: Use shorter TTLs like 60-300 seconds for testing

### Redis URL Format

```
redis://[username:password@]host:port[/db]
```

Examples:
```bash
# Local Redis (no auth)
REDIS_URL=redis://localhost:6379

# Railway managed Redis
REDIS_URL=${{Redis.REDIS_URL}}

# External Redis with auth
REDIS_URL=redis://default:password123@redis.example.com:6379

# Redis with specific database
REDIS_URL=redis://localhost:6379/1
```

## Troubleshooting

### Cache Not Working

**Check environment variables:**
```bash
# Railway
railway variables

# Local
cat .env | grep REDIS
```

**Check Redis connection:**
```bash
curl https://your-api-url/health

# Should show:
# "cache_status": "redis_enabled"
```

**Check logs for errors:**
```bash
railway logs

# Look for:
# "Redis cache connected successfully"
# or
# "WARNING: Redis connection failed: ..."
```

### Performance Not Improving

1. **Verify cache is hitting:**
   - Check `/cache/stats` endpoint
   - Look for increasing `keyspace_hits`
   - Look for cache HIT/MISS messages in logs

2. **Check TTL:**
   - Ensure `CACHE_TTL_SECONDS` is set appropriately
   - Too short TTL means frequent cache expiration

3. **Monitor cache size:**
   - Check `total_keys` in `/cache/stats`
   - If always low, cache might be expiring too quickly

### Railway-Specific Issues

**"Redis not found" error:**
- Ensure Redis service is added to your Railway project
- Check that `REDIS_URL` references the correct service: `${{Redis.REDIS_URL}}`

**Connection timeout:**
- Railway Redis is internal-only by default (good for security)
- Ensure both services are in the same Railway project
- Check network settings if using custom configuration

**Cache not shared between deployments:**
- This is expected when you redeploy with Railway's "new deployment" option
- Use the same Redis service, don't create a new one each time
- Cache will rebuild automatically as requests come in

## Cost Considerations

### Railway Pricing (as of 2024)

- **Redis Plugin**: Included in all plans, usage-based pricing
- **Free Tier**: $5/month credit (covers small Redis instances)
- **Pro Plan**: $20/month credit included

### Cache Performance Impact

With caching enabled:
- First request: Slow (calls YouTube API + saves to cache)
- Subsequent requests (within TTL): Very fast (served from Redis)
- Cache hit rate > 80% = significant performance improvement

Example: 1000 requests for same video
- Without cache: 1000 YouTube API calls (~10-30s total)
- With cache: 1 YouTube API call + 999 Redis reads (~1-2s total)

## Best Practices

1. **Start with defaults**: 1-hour TTL works for most use cases
2. **Monitor cache stats**: Check `/cache/stats` regularly
3. **Clear cache when needed**: After YouTube video updates
4. **Use Railway's managed Redis**: Easier than self-hosting
5. **Keep Redis and API in same region**: Reduces latency
6. **Don't cache errors**: Only successful responses are cached
7. **Test without cache first**: Ensure API works before adding caching

## Security

- **Railway Redis**: Internal-only by default, no public access
- **No sensitive data**: Only public YouTube data is cached
- **Authentication**: Use Redis AUTH in production (Railway handles this)
- **Encryption**: Enable TLS for Redis in production environments

## Migration and Backup

### Export Cache Data (if needed)

```bash
# Connect to Railway Redis
railway run redis-cli

# Export all keys
KEYS youtube_api:*

# Backup to file (requires redis-cli locally)
redis-cli --rdb /path/to/backup.rdb
```

### Switch Redis Instances

1. Deploy new Redis service
2. Update `REDIS_URL` to point to new instance
3. Redeploy application
4. Old cache will rebuild automatically

## Next Steps

- [Railway Deployment Guide](RAILWAY_DEPLOYMENT.md)
- [Quick Start Guide](QUICK_START.md)
- [Main README](README.md)
