#!/bin/bash

# Railway Deployment Script for YouTube API Server
# This script helps deploy the application to Railway

set -e

echo "=================================================="
echo "YouTube API Server - Railway Deployment"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI is not installed.${NC}"
    echo "Install it with: npm install -g @railway/cli"
    echo "Or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI is installed${NC}"

# Check if authenticated
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}You are not logged in to Railway.${NC}"
    echo "Please run: railway login"
    exit 1
fi

RAILWAY_USER=$(railway whoami 2>/dev/null)
echo -e "${GREEN}✓ Logged in as: $RAILWAY_USER${NC}"
echo ""

# Check if project is already linked
if railway status &> /dev/null; then
    echo -e "${BLUE}Project is already linked to Railway${NC}"
    echo "Current status:"
    railway status
    echo ""
    read -p "Do you want to deploy now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Deploying to Railway...${NC}"
        railway up
    fi
else
    echo -e "${YELLOW}No Railway project linked yet.${NC}"
    echo ""
    echo "To deploy this application to Railway, you have two options:"
    echo ""
    echo -e "${BLUE}Option 1: Create via Web Dashboard (Recommended)${NC}"
    echo "1. Visit: https://railway.app/new"
    echo "2. Click 'Deploy from GitHub repo'"
    echo "3. Select: creativerezz/youtube-api-server-1"
    echo "4. Railway will automatically deploy"
    echo "5. Get your deployment URL from the dashboard"
    echo ""
    echo -e "${BLUE}Option 2: Link to existing project${NC}"
    echo "1. Create a project in Railway dashboard first"
    echo "2. Run: railway link"
    echo "3. Select your project"
    echo "4. Run: railway up"
    echo ""
    echo -e "${GREEN}Quick Link:${NC} https://railway.app/new?template=https://github.com/creativerezz/youtube-api-server-1"
    echo ""

    # Try to open the Railway new project page
    if command -v open &> /dev/null; then
        read -p "Would you like to open Railway in your browser? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "https://railway.app/new"
        fi
    fi
fi

echo ""
echo -e "${BLUE}Configuration files ready:${NC}"
echo "  - nixpacks.toml (Build configuration)"
echo "  - Procfile (Start command)"
echo "  - /health endpoint (Health check)"
echo ""

echo -e "${BLUE}Environment Variables (Optional):${NC}"
echo "  - WEBSHARE_PROXY_USERNAME"
echo "  - WEBSHARE_PROXY_PASSWORD"
echo "  - PORT (automatically set by Railway)"
echo "  - HOST (defaults to 0.0.0.0)"
echo ""

echo -e "${GREEN}For detailed instructions, see: RAILWAY_DEPLOYMENT.md${NC}"
echo "=================================================="
