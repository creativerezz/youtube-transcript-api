# Quick Start - Deploy to Railway

Your YouTube API Server is ready to deploy! I've already prepared everything you need.

## What's Been Configured

1. **Procfile** - Tells Railway how to start your app
2. **nixpacks.toml** - Configures the build process with Python 3.12 and uv
3. **GitHub Repository** - Already pushed and ready at https://github.com/creativerezz/youtube-api-server-1
4. **Railway CLI** - Already authenticated as Reza Jafar (jafar.reza@icloud.com)

## Deploy Now (2 Minutes)

### Step 1: Create Railway Project (Browser should be open)

The Railway deployment page should already be open in your browser. If not:

1. Visit: https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select: `creativerezz/youtube-api-server-1`
4. Click "Deploy Now"

Railway will automatically:
- Detect it's a Python project
- Use the nixpacks.toml configuration
- Install dependencies with `uv sync`
- Start the server with uvicorn
- Assign a public URL

### Step 2: Get Your Deployment URL

Once deployment completes (usually 1-2 minutes):
1. Click on your project in Railway dashboard
2. Click on the service/deployment
3. Copy the public URL (format: `https://your-app.up.railway.app`)

### Step 3: Test Your API

```bash
# Replace with your actual Railway URL
export RAILWAY_URL="https://your-app.up.railway.app"

# Test health endpoint
curl $RAILWAY_URL/health

# Test video data endpoint
curl -X POST $RAILWAY_URL/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Step 4: Link Your Local Environment (Optional)

After creating the project in Railway:

```bash
# Link to your Railway project
railway link

# View logs in real-time
railway logs --follow

# Check deployment status
railway status
```

## Optional: Configure Proxy (If You Have Credentials)

If you have Webshare proxy credentials:

1. In Railway dashboard, go to your project
2. Click on "Variables" tab
3. Add:
   - `WEBSHARE_PROXY_USERNAME` = your-username
   - `WEBSHARE_PROXY_PASSWORD` = your-password
4. Railway will automatically redeploy

## Auto-Deploy

Every time you push to the `main` branch, Railway will automatically:
1. Detect the push
2. Build your app
3. Run tests (if configured)
4. Deploy the new version
5. Notify you of success/failure

## Monitoring

View logs:
```bash
railway logs
```

Or view them in the Railway dashboard under "Deployments" > "Logs"

## API Endpoints

Once deployed, your API will have:

- `GET /health` - Health check with proxy status
- `POST /video-data` - Get YouTube video metadata
- `POST /video-captions` - Get video captions/transcripts
- `POST /video-timestamps` - Get timestamped transcript
- `POST /video-transcript-languages` - List available languages

## Need Help?

- Detailed guide: See `RAILWAY_DEPLOYMENT.md`
- Run helper script: `./deploy-to-railway.sh`
- Railway docs: https://docs.railway.app
- GitHub repo: https://github.com/creativerezz/youtube-api-server-1

## Summary

Your app is fully configured and ready! Just:
1. Create the Railway project (browser should be open)
2. Wait for deployment (1-2 mins)
3. Get your URL and test it
4. Done!

The Railway project will automatically use:
- Python 3.12
- uv package manager
- uvicorn ASGI server
- PORT environment variable from Railway
- /health endpoint for health checks
