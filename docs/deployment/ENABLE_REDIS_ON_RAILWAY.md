# Enable Redis Caching on Railway - Quick Guide

Your YouTube API Server is ready for Redis caching! Follow these simple steps to enable it on Railway.

## Project Information
- **Project**: soothing-energy
- **Service**: youtube-api-server-v1
- **Environment**: production

## Step 1: Add Redis Service (2 minutes)

### Option A: Via Railway Dashboard (Recommended - Easiest)

1. **Open your Railway project**:
   - Go to: https://railway.app/project/soothing-energy
   - Or navigate to: Railway Dashboard → Your Projects → "soothing-energy"

2. **Add Redis Database**:
   - Click the **"+ New"** button in your project
   - Select **"Database"**
   - Click **"Add Redis"**
   - Wait ~30 seconds for Redis to provision

3. **Verify Redis is running**:
   - You should see a new "Redis" service card in your project
   - It should show status: "Active" or "Deployed"

### Option B: Via Railway CLI (Alternative)

If you prefer using the CLI, you'll need to run this in an interactive terminal:

```bash
# This requires interactive input
railway add -d redis
```

Then select "Database" → "Redis"

## Step 2: Configure Environment Variables (1 minute)

Now link your API service to the Redis database:

1. **Open your API service settings**:
   - Click on your **"youtube-api-server-v1"** service card
   - Click the **"Variables"** tab

2. **Add REDIS_URL variable**:
   - Click **"+ New Variable"** button
   - Variable name: `REDIS_URL`
   - Variable value: `${{Redis.REDIS_URL}}`

   > **Important**: Railway's Redis service creates a `REDIS_URL` variable automatically with this format:
   > `redis://${{REDISUSER}}:${{REDIS_PASSWORD}}@${{REDISHOST}}:${{REDISPORT}}`
   >
   > By using `${{Redis.REDIS_URL}}`, you're referencing that variable from the Redis service.
   > Railway will automatically resolve it to the full connection string.

3. **Optional - Customize cache TTL**:
   - Click **"+ New Variable"** again
   - Variable name: `CACHE_TTL_SECONDS`
   - Variable value: `3600` (or your preferred duration in seconds)

4. **Save changes**:
   - Railway auto-saves variables
   - Your service will automatically redeploy with the new configuration

## Step 3: Verify Deployment (1 minute)

Wait for the deployment to complete (usually 1-2 minutes), then:

### Check Health Endpoint

```bash
# Replace with your actual Railway URL
curl https://your-app.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T...",
  "proxy_status": "webshare_enabled",
  "cache_status": "redis_enabled",   ← Should say "enabled"
  "cache_ttl_seconds": 3600,         ← Should show your TTL
  "parallel_processing": "enabled"
}
```

### Check Cache Statistics

```bash
curl https://your-app.up.railway.app/cache/stats
```

**Expected response:**
```json
{
  "enabled": true,                    ← Should be true
  "status": "connected",              ← Should be "connected"
  "total_keys": 0,
  "ttl_seconds": 3600,
  "keyspace_hits": 0,
  "keyspace_misses": 0
}
```

## Step 4: Test Cache Performance (Optional)

Make the same request twice to see caching in action:

```bash
# First request (cache MISS - slower)
time curl -X POST https://your-app.up.railway.app/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Second request (cache HIT - much faster!)
time curl -X POST https://your-app.up.railway.app/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

The second request should be **10-30x faster**!

## Monitoring Cache Performance

### View Logs

Check your Railway deployment logs for cache activity:

```bash
railway logs
```

Look for these messages:
- `[timestamp] Redis cache connected successfully` ✅
- `[timestamp] Cache Status: Redis enabled` ✅
- `[timestamp] Cache HIT: youtube_api:video_data:...` (serving from cache)
- `[timestamp] Cache MISS: youtube_api:video_data:...` (fetching from YouTube)
- `[timestamp] Cache SET: youtube_api:video_data:... (TTL: 3600s)` (saving to cache)

### Monitor via API

```bash
# Check cache stats periodically
watch -n 5 'curl -s https://your-app.up.railway.app/cache/stats | jq .'
```

Key metrics to watch:
- **keyspace_hits**: Number of cache hits (good!)
- **keyspace_misses**: Number of cache misses (calls to YouTube)
- **Hit rate**: `hits / (hits + misses)` - aim for > 80%

## Troubleshooting

### Cache shows "disabled" in health check

**Problem**: `"cache_status": "redis_disabled"`

**Solutions**:
1. Verify Redis service is running in Railway dashboard
2. Check `REDIS_URL` variable is set: Go to Variables tab
3. Ensure format is exactly: `${{Redis.REDIS_URL}}`
4. Check deployment logs for connection errors
5. Try redeploying: Click "Deploy" → "Redeploy"

### Redis connection errors in logs

**Problem**: `WARNING: Redis connection failed: ...`

**Solutions**:
1. Ensure Redis and API services are in the same Railway project
2. Check Redis service status (should be "Active")
3. Verify variable reference syntax: `${{Redis.REDIS_URL}}`
4. Check Redis service name matches (default: "Redis")
5. Restart both services if needed

### Cache not improving performance

**Problem**: Requests still slow even with cache enabled

**Solutions**:
1. Check `/cache/stats` - verify `keyspace_hits` is increasing
2. Ensure you're making identical requests (same URL)
3. Verify cache isn't expiring too quickly (check `CACHE_TTL_SECONDS`)
4. Look at logs for cache HIT vs MISS ratio
5. Try clearing cache: `curl -X POST https://your-app.up.railway.app/cache/clear`

### "Service variable reference not found" error

**Problem**: `${{Redis.REDIS_URL}}` doesn't resolve

**Solutions**:
1. Check Redis service name in Railway dashboard (usually "Redis")
2. If Redis service has different name (e.g., "redis-1"), use: `${{redis-1.REDIS_URL}}`
3. Alternative: Build the URL manually using Redis service variables:
   ```
   redis://${{Redis.REDISUSER}}:${{Redis.REDIS_PASSWORD}}@${{Redis.REDISHOST}}:${{Redis.REDISPORT}}
   ```
4. Or use the private domain format:
   ```
   redis://default:${{Redis.REDIS_PASSWORD}}@${{Redis.RAILWAY_PRIVATE_DOMAIN}}:6379
   ```
5. Ensure Redis service exists in the same project and environment

## Quick Reference

### Railway Project URLs
- **Dashboard**: https://railway.app/project/soothing-energy
- **Service Settings**: Click on "youtube-api-server-v1" card
- **Redis Settings**: Click on "Redis" card (after adding)

### Environment Variables Summary
| Variable | Value | Required |
|----------|-------|----------|
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Yes (for caching) |
| `CACHE_TTL_SECONDS` | `3600` | No (default: 3600) |

### Cache Management Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check cache status |
| `/cache/stats` | GET | View cache metrics |
| `/cache/clear` | POST | Clear all cache |

### Expected Performance
- **First request**: 1-3 seconds (YouTube API call)
- **Cached requests**: 50-100ms (10-30x faster)
- **Cache hit rate**: Target > 80%
- **Cache duration**: 1 hour (default)

## What Happens Next?

Once Redis is enabled:

1. ✅ **All API responses are automatically cached**
   - Video metadata
   - Captions/transcripts
   - Timestamps
   - Language lists

2. ✅ **Performance improves dramatically**
   - First request: Normal speed (cache MISS)
   - Repeat requests: 10-30x faster (cache HIT)

3. ✅ **Reduced costs**
   - Fewer YouTube API calls
   - Less proxy bandwidth
   - Lower server load

4. ✅ **Better scalability**
   - Handle more concurrent requests
   - Shared cache across instances
   - Automatic cache management

## Estimated Costs

**Railway Redis Pricing** (as of 2024):
- **Free tier**: $5/month credit (covers small Redis)
- **Typical cost**: $2-5/month for small-medium traffic
- **ROI**: Usually positive within days (reduced API calls)

## Need Help?

- **Redis Setup Guide**: See [REDIS_SETUP.md](REDIS_SETUP.md)
- **Deployment Guide**: See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
- **Cache Details**: See [CACHING_IMPROVEMENTS.md](CACHING_IMPROVEMENTS.md)
- **Railway Docs**: https://docs.railway.app/databases/redis

---

## Summary Checklist

- [ ] Add Redis service to Railway project
- [ ] Set `REDIS_URL` = `${{Redis.REDIS_URL}}` in API service variables
- [ ] Wait for automatic redeployment (~2 minutes)
- [ ] Verify health endpoint shows `"cache_status": "redis_enabled"`
- [ ] Test cache with duplicate requests
- [ ] Monitor logs for cache HIT/MISS messages
- [ ] Check `/cache/stats` for performance metrics

**Total setup time**: ~5 minutes
**Performance improvement**: 10-30x faster for cached requests

🚀 Your YouTube API Server will be significantly faster once Redis is enabled!
