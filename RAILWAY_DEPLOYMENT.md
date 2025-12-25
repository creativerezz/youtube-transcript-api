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

### Step 2: Configure Environment Variables (Optional)

The proxy credentials are optional. If you have Webshare proxy credentials:

1. In your Railway project dashboard, go to the "Variables" tab
2. Add the following environment variables:
   - `WEBSHARE_PROXY_USERNAME` - Your Webshare proxy username
   - `WEBSHARE_PROXY_PASSWORD` - Your Webshare proxy password

The following variables are automatically set by Railway:
- `PORT` - Railway automatically provides this (no need to set)
- `HOST` - Defaults to 0.0.0.0 in the application

### Step 3: Deploy Configuration

Railway will automatically use the deployment configuration from:

1. **nixpacks.toml** - Defines the build process:
   - Python 3.12 runtime
   - Installation via `uv` package manager
   - Start command with uvicorn

2. **Procfile** - Backup start command configuration:
   - `web: uv run uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Deploy

Railway will automatically deploy when you:
- Push to the main branch (already set up)
- Or click "Deploy" in the Railway dashboard

The deployment process:
1. Railway detects the push to GitHub
2. Builds the project using nixpacks
3. Installs dependencies with `uv sync`
4. Starts the server with uvicorn
5. Exposes the service on a public URL

### Step 5: Access Your Deployed API

After deployment completes:

1. Railway will provide a public URL (format: `https://your-app.up.railway.app`)
2. Your API will be available at the following endpoints:
   - `GET /health` - Health check
   - `POST /video-data` - Get video metadata
   - `POST /video-captions` - Get video captions
   - `POST /video-timestamps` - Get video timestamps
   - `POST /video-transcript-languages` - List available languages

### Step 6: Link Local Environment to Railway (Optional)

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
# Health check
curl https://your-app.up.railway.app/health

# Test video data endpoint
curl -X POST https://your-app.up.railway.app/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## Monitoring and Logs

View logs in real-time:
```bash
railway logs --follow
```

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
