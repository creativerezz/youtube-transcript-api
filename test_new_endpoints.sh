#!/bin/bash

echo "Testing new AI-powered endpoints"
echo "=================================="
echo ""

BASE_URL="http://localhost:8000"
TEST_VIDEO="dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up

echo "1. Testing /video-notes endpoint (structured format)..."
echo "------------------------------------------------------"
curl -X POST "$BASE_URL/video-notes" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$TEST_VIDEO\", \"format\": \"structured\"}" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo ""
echo "2. Testing /video-notes endpoint (summary format)..."
echo "----------------------------------------------------"
curl -X POST "$BASE_URL/video-notes" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$TEST_VIDEO\", \"format\": \"summary\"}" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo ""
echo "3. Testing /video-translate endpoint (Spanish)..."
echo "--------------------------------------------------"
curl -X POST "$BASE_URL/video-translate" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$TEST_VIDEO\", \"target_language\": \"Spanish\"}" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo ""
echo "4. Checking root endpoint for AI features status..."
echo "---------------------------------------------------"
curl -X GET "$BASE_URL/" | python3 -m json.tool

echo ""
echo "Testing complete!"
