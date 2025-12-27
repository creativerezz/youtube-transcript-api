# Railway Deployment Guide for YouTube API Server

This guide will walk you through deploying the YouTube API Server to Railway.

## Prerequisites

- Railway account (sign up at https://railway.app)
- GitHub repository connected (already set up: https://github.com/creativerezz/youtube-api-server-1.git)
- Railway CLI installed (already installed and authenticated)

## Deployment Steps

### Step 1: Create a New Railway Project

Since the Railway CLI requires interactive input, we'll use the Railway web dashboard:

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository: `creativerezz/youtube-api-server-1`
4. Railway will automatically detect the Python project

### Step 2: Add Redis for Caching (Recommended)

Redis caching dramatically improves performance. To add Redis:

**Via Railway Dashboard:**
1. In your Railway project, click **"+ New"**
2. Select **"Database" → "Add Redis"**
3. Wait for Redis to provision (takes ~30 seconds)

**Via Railway CLI:**
```bash
railway add --plugin redis
```

The Redis service automatically creates a `REDIS_URL` variable that your API service can reference.

### Step 3: Configure Environment Variables

**Required for Redis Caching:**
1. In your Railway project dashboard, click on your API service
2. Go to the "Variables" tab
3. Add: `REDIS_URL` = `${{Redis.REDIS_URL}}`
   - This references the Redis service you just created
   - Railway will automatically inject the correct URL

**Optional - Proxy Configuration:**
If you have Webshare proxy credentials:
- `WEBSHARE_PROXY_USERNAME` - Your Webshare proxy username
- `WEBSHARE_PROXY_PASSWORD` - Your Webshare proxy password

**Optional - Cache Configuration:**
- `CACHE_TTL_SECONDS` - Cache expiration time (default: 3600)

**Automatically Set by Railway:**
- `PORT` - Railway automatically provides this (no need to set)
- `HOST` - Defaults to 0.0.0.0 in the application

### Step 4: Deploy Configuration

Railway will automatically use the deployment configuration from:

1. **nixpacks.toml** - Defines the build process:
   - Python 3.12 runtime
   - Installation via `uv` package manager
   - Start command with uvicorn

2. **Procfile** - Backup start command configuration:
   - `web: uv run uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 5: Deploy

Railway will automatically deploy when you:
- Push to the main branch (already set up)
- Or click "Deploy" in the Railway dashboard

The deployment process:
1. Railway detects the push to GitHub
2. Builds the project using nixpacks
3. Installs dependencies with `uv sync`
4. Starts the server with uvicorn
5. Exposes the service on a public URL

### Step 6: Verify Deployment

After deployment completes:

1. Railway will provide a public URL (format: `https://your-app.up.railway.app`)
2. Test the health endpoint:
   ```bash
   curl https://your-app.up.railway.app/health
   ```
3. Verify Redis cache is working:
   ```bash
   curl https://your-app.up.railway.app/cache/stats
   ```
   Should show: `"status": "connected"` and `"enabled": true`

4. Your API will be available at the following endpoints:
   - `GET /health` - Health check with cache status
   - `GET /cache/stats` - Cache statistics
   - `POST /cache/clear` - Clear cache
   - `POST /video-data` - Get video metadata (cached)
   - `POST /video-captions` - Get video captions (cached)
   - `POST /video-timestamps` - Get video timestamps (cached)
   - `POST /video-transcript-languages` - List available languages (cached)

### Step 7: Link Local Environment to Railway (Optional)

To manage your deployment from the CLI:

```bash
# The project ID will be shown in your Railway dashboard URL
railway link

# View logs
railway logs

# Check status
railway status

# Set environment variables
railway variables set WEBSHARE_PROXY_USERNAME=your-username
railway variables set WEBSHARE_PROXY_PASSWORD=your-password
```

## Deployment Verification

Test your deployed API:

```bash
# Health check (should show cache_status: "redis_enabled")
curl https://your-app.up.railway.app/health

# Check cache statistics
curl https://your-app.up.railway.app/cache/stats

# Test video data endpoint (first request - cache MISS)
curl -X POST https://your-app.up.railway.app/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Run the same request again (second request - cache HIT, much faster!)
curl -X POST https://your-app.up.railway.app/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## Monitoring and Logs

View logs in real-time:
```bash
railway logs --follow
```

Look for cache-related log messages:
- `[timestamp] Redis cache connected successfully`
- `[timestamp] Cache HIT: youtube_api:video_data:abc123` (cached response served)
- `[timestamp] Cache MISS: youtube_api:video_data:def456` (fetching from YouTube)
- `[timestamp] Cache SET: youtube_api:video_data:def456 (TTL: 3600s)` (saving to cache)

Or view them in the Railway dashboard under the "Deployments" tab.

## Troubleshooting

### Build Failures

If the build fails:
1. Check Railway build logs in the dashboard
2. Verify all dependencies are in pyproject.toml
3. Ensure Python 3.12 compatibility

### Port Binding Issues

Railway automatically sets the PORT environment variable. The application is configured to:
- Use `os.getenv("PORT", 8000)` to read the port
- Bind to `0.0.0.0` for external access

### Health Check Failures

The health check endpoint `/health` is configured in nixpacks.toml. If it fails:
1. Verify the endpoint returns 200 status
2. Check application startup logs
3. Ensure uvicorn is starting correctly

### Redis Cache Issues

**Cache shows "disabled" in health check:**
1. Verify Redis service is running: Check Railway dashboard
2. Check `REDIS_URL` environment variable is set: `railway variables`
3. Ensure `REDIS_URL` references correct service: `${{Redis.REDIS_URL}}`
4. Check logs for "Redis cache connected successfully" message

**Cache not improving performance:**
1. Check `/cache/stats` endpoint - look for increasing `keyspace_hits`
2. Verify same requests are being made (cache keys are URL-based)
3. Check `CACHE_TTL_SECONDS` is appropriate (default: 3600)
4. Monitor logs for cache HIT vs MISS messages

**Redis connection errors:**
1. Ensure both services (API + Redis) are in same Railway project
2. Check Redis service logs for errors
3. Restart Redis service if needed
4. Verify network connectivity between services

## Auto-Deployment

Railway is now configured for automatic deployments:
- Every push to `main` branch triggers a new deployment
- Railway will build, test, and deploy automatically
- You'll receive notifications about deployment status

## Costs

Railway offers:
- Free tier: $5 credit per month
- Usage-based pricing after free tier
- Sleep mode for inactive services

Monitor your usage in the Railway dashboard.

## Next Steps

1. Visit https://railway.app/new to create your project
2. Connect your GitHub repository
3. Configure environment variables (optional)
4. Deploy and get your public URL
5. Test the API endpoints

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/creativerezz/youtube-api-server-1/issues
