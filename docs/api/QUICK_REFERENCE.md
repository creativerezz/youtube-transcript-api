# API Quick Reference

Fast reference cards for integrating with the YouTube API Server.

## 🔗 Base URL
```
https://transcript.youtubesummaries.cc
```

---

## 📋 Quick Examples

### 1️⃣ Get Video Metadata (Fastest)

**Using full URL:**
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Using just the video ID:**
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "dQw4w9WgXcQ"}'
```

**Response:**
```json
{
  "title": "Video Title",
  "author_name": "Channel Name",
  "thumbnail_url": "https://...",
  "author_url": "https://www.youtube.com/@channel"
}
```

**Performance:**
- First request: ~1-3 seconds
- Cached: ~50-100ms ⚡

---

### 2️⃣ Get Full Transcript
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-captions \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

**Response:**
```json
{
  "captions": "Full transcript text here..."
}
```

**Performance:**
- First request: ~5-15 seconds
- Cached: ~100-200ms ⚡

---

### 3️⃣ Get Transcript with Specific Language
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-captions \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "languages": ["es", "en"]
  }'
```

**Language codes:** es (Spanish), fr (French), de (German), ja (Japanese), etc.

---

### 4️⃣ Check Available Languages
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-transcript-languages \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
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
    }
  ]
}
```

---

### 5️⃣ Get Timestamped Transcript
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-timestamps \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

**Response:**
```json
{
  "timestamps": [
    "0:00 - Introduction text",
    "0:15 - Next segment text",
    "1:30 - Another segment"
  ]
}
```

---

---

## 🤖 AI-Powered Endpoints (New!)

### 6️⃣ Generate Video Notes
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-notes \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "format": "structured"
  }'
```

**Format options:** `"structured"`, `"summary"`, `"detailed"`

**Response:**
```json
{
  "video_title": "Video Title",
  "channel": "Channel Name",
  "format": "structured",
  "notes": "# Overview\n\nThis video covers...\n\n## Main Topics\n...",
  "word_count": 427,
  "timestamp": "2025-12-27T01:30:00"
}
```

**Performance:**
- First request: ~5-15 seconds
- Cost: ~$0.03-0.10 per video

---

### 7️⃣ Translate Video Transcript
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-translate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "target_language": "Spanish"
  }'
```

**Supported languages:** Spanish, French, German, Japanese, Korean, Chinese, Arabic, and many more!

**Response:**
```json
{
  "video_title": "Video Title",
  "channel": "Channel Name",
  "target_language": "Spanish",
  "translated_transcript": "Texto traducido aquí...",
  "translated_timestamps": [
    "0:00 - Texto traducido",
    "0:15 - Más texto traducido"
  ],
  "word_count": 342,
  "note": "Use with ElevenLabs for voice dubbing"
}
```

**Performance:**
- First request: ~10-25 seconds
- Cost: ~$0.05-0.15 per video

**💡 Pro tip:** Use translated transcript with ElevenLabs voice cloning to create dubbed videos!

---

## ⚡ Cache Endpoints

### Check Cache Status
```bash
curl https://transcript.youtubesummaries.cc/health
```

**Response:**
```json
{
  "status": "healthy",
  "cache_status": "redis_enabled",
  "cache_ttl_seconds": 3600
}
```

---

### Get Cache Statistics
```bash
curl https://transcript.youtubesummaries.cc/cache/stats
```

**Response:**
```json
{
  "enabled": true,
  "status": "connected",
  "total_keys": 42,
  "keyspace_hits": 156,
  "keyspace_misses": 42
}
```

**Hit rate calculation:** `hits / (hits + misses) = 156 / 198 = 78.8%`

---

### Clear Cache (Use Sparingly!)
```bash
curl -X POST https://transcript.youtubesummaries.cc/cache/clear
```

---

## 🚀 JavaScript One-Liners

### Fetch Video Data
```javascript
fetch('https://transcript.youtubesummaries.cc/video-data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://www.youtube.com/watch?v=VIDEO_ID' })
}).then(r => r.json()).then(console.log);
```

### Fetch Captions
```javascript
fetch('https://transcript.youtubesummaries.cc/video-captions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://www.youtube.com/watch?v=VIDEO_ID' })
}).then(r => r.json()).then(d => console.log(d.captions));
```

### Check Cache Stats
```javascript
fetch('https://transcript.youtubesummaries.cc/cache/stats')
  .then(r => r.json())
  .then(console.log);
```

---

## 🎨 React Hook (Copy & Paste)

```jsx
function useYouTubeData(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!url) return;

    setLoading(true);
    fetch('https://transcript.youtubesummaries.cc/video-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })
      .then(r => r.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
}
```

**Usage:**
```jsx
function MyComponent() {
  const { data, loading } = useYouTubeData('https://youtube.com/watch?v=...');

  if (loading) return <div>Loading...</div>;
  return <h1>{data?.title}</h1>;
}
```

---

## 📊 Performance Reference

| Endpoint | Uncached | Cached | Cache Duration |
|----------|----------|--------|----------------|
| `/video-data` | 1-3s | ~100ms | 1 hour |
| `/video-captions` | 5-15s | ~200ms | 1 hour |
| `/video-timestamps` | 5-15s | ~200ms | 1 hour |
| `/video-transcript-languages` | 1-3s | ~100ms | 1 hour |

**Cache speedup:** **10-56x faster** for cached requests! ⚡

---

## 🔍 Supported YouTube URL Formats

✅ **All these formats work** (20+ variations supported):

**Direct video IDs:**
```
dQw4w9WgXcQ
```

**Standard URLs:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtube.com/watch?v=dQw4w9WgXcQ
http://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Short URLs:**
```
https://youtu.be/dQw4w9WgXcQ
http://youtu.be/dQw4w9WgXcQ
youtu.be/dQw4w9WgXcQ
```

**With query parameters:**
```
https://youtu.be/dQw4w9WgXcQ?t=123
https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest
https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s
```

**Embed URLs:**
```
https://www.youtube.com/embed/dQw4w9WgXcQ
https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1
```

**Special formats:**
```
https://www.youtube.com/shorts/dQw4w9WgXcQ      (Shorts)
https://www.youtube.com/live/dQw4w9WgXcQ        (Live)
https://m.youtube.com/watch?v=dQw4w9WgXcQ       (Mobile)
https://music.youtube.com/watch?v=dQw4w9WgXcQ   (Music)
https://www.youtube.com/v/dQw4w9WgXcQ           (Old format)
```

**Without protocol:**
```
www.youtube.com/watch?v=dQw4w9WgXcQ
youtube.com/watch?v=dQw4w9WgXcQ
```

**✨ Pro tip:** You can pass just the video ID instead of the full URL!

---

## ⚠️ Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "detail": "Invalid YouTube URL"
}
```
→ Check URL format

**500 Internal Server Error**
```json
{
  "detail": "Error getting captions for video: ..."
}
```
→ Video may not have captions, or YouTube blocking

---

## 💡 Best Practices

1. **Always check cache status first** - Use `/health` to verify caching is enabled
2. **Handle slow first requests** - Show loading state for uncached data (5-15s)
3. **Leverage caching** - Don't add random parameters to bypass cache
4. **Validate URLs client-side** - Check format before sending request
5. **Monitor cache hit rate** - Use `/cache/stats` to verify performance
6. **Use language fallbacks** - Request multiple languages: `["es", "en"]`
7. **Batch parallel requests** - Use `Promise.all()` for metadata + captions

---

## 🔗 CORS

✅ CORS is enabled - you can call this API from any frontend domain.

---

## 📚 Full Documentation

- **Frontend Integration:** [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
- **API Server:** [README.md](README.md)
- **Caching Details:** [CACHING_IMPROVEMENTS.md](CACHING_IMPROVEMENTS.md)
- **Redis Setup:** [REDIS_SETUP.md](REDIS_SETUP.md)

---

## 🎯 Quick Test

Test the API right now:

```bash
# Get video info for Rick Astley
curl -X POST https://transcript.youtubesummaries.cc/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Check if it's cached (second request will be much faster)
curl -X POST https://transcript.youtubesummaries.cc/video-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# View cache stats
curl https://transcript.youtubesummaries.cc/cache/stats
```

You should see `keyspace_hits` increase on the second request! 🎉
