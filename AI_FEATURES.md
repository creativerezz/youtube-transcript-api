# AI-Powered Features

## Overview

The YouTube API Server now includes AI-powered features for generating structured notes and translating video transcripts using Claude AI (Anthropic). These features are perfect for building YouTube video translation tools and note-taking applications.

## 🔑 Setup

### Get an Anthropic API Key

1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Add to your `.env` file:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

### Pricing (as of Dec 2025)

- **Claude 3.5 Sonnet**: $3 per million input tokens, $15 per million output tokens
- **Claude 3.5 Haiku**: $0.80 per million input tokens, $4 per million output tokens

**Estimated costs per request:**
- `/video-notes`: ~$0.03-0.10 per video (depending on transcript length)
- `/video-translate`: ~$0.05-0.15 per video (transcript + timestamps)

## 📝 POST /video-notes

Generate structured notes, summaries, or detailed outlines from YouTube videos.

### Request Body

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "languages": ["en"],  // Optional: language preference
  "format": "structured"  // Options: "structured", "summary", "detailed"
}
```

### Format Options

#### `"structured"` (Default)
Well-organized notes with:
- Overview
- Main topics with key points
- Key takeaways
- Conclusion

#### `"summary"`
Concise summary with:
- 2-3 sentence executive summary
- 3-5 key takeaways
- Main topics covered

#### `"detailed"`
Comprehensive notes with:
- Executive summary
- Detailed outline with sections
- Key concepts explained
- Important quotes
- Action items

### Response

```json
{
  "video_title": "Never Gonna Give You Up",
  "channel": "Rick Astley",
  "format": "structured",
  "notes": "# Overview\n\nThis video features...\n\n## Main Topics\n...",
  "word_count": 427,
  "timestamp": "2025-12-27T01:30:00"
}
```

### Example Usage

**Bash:**
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-notes \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "summary"
  }'
```

**JavaScript:**
```javascript
const response = await fetch('https://transcript.youtubesummaries.cc/video-notes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    format: 'detailed'
  })
});

const data = await response.json();
console.log(data.notes);  // Markdown-formatted notes
```

**Python:**
```python
import requests

response = requests.post(
    'https://transcript.youtubesummaries.cc/video-notes',
    json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'format': 'structured'
    }
)

notes = response.json()['notes']
print(notes)
```

---

## 🌍 POST /video-translate

Translate YouTube video transcripts to any language using AI. Perfect for creating dubbed content or making videos accessible to global audiences.

### Request Body

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "target_language": "Spanish",
  "source_languages": ["en"]  // Optional: source language preference
}
```

### Supported Languages

Any language that Claude supports:
- Spanish, French, German, Italian, Portuguese
- Japanese, Korean, Chinese (Simplified/Traditional)
- Arabic, Hindi, Russian, Turkish
- And many more...

Just specify the language name in English (e.g., "Spanish", "Japanese", "Arabic")

### Response

```json
{
  "video_title": "Never Gonna Give You Up",
  "channel": "Rick Astley",
  "target_language": "Spanish",
  "translated_transcript": "Nunca te voy a abandonar...",
  "translated_timestamps": [
    "0:00 - Nunca te voy a abandonar",
    "0:15 - Nunca te voy a decepcionar"
  ],
  "word_count": 342,
  "timestamp": "2025-12-27T01:30:00",
  "note": "Use this translated transcript with ElevenLabs voice cloning for dubbed audio"
}
```

### Example Usage

**Bash:**
```bash
curl -X POST https://transcript.youtubesummaries.cc/video-translate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "target_language": "Japanese"
  }'
```

**JavaScript:**
```javascript
const response = await fetch('https://transcript.youtubesummaries.cc/video-translate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    target_language: 'French'
  })
});

const data = await response.json();

// Use the translated transcript for dubbing
console.log('Translated:', data.translated_transcript);
console.log('Timestamps:', data.translated_timestamps);
```

**Python:**
```python
import requests

response = requests.post(
    'https://transcript.youtubesummaries.cc/video-translate',
    json={
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'target_language': 'German'
    }
)

data = response.json()
translated_text = data['translated_transcript']
timestamps = data['translated_timestamps']

# Ready to use with ElevenLabs for voice dubbing!
```

---

## 🎤 Integration with ElevenLabs (Voice Dubbing)

The `/video-translate` endpoint is designed to work seamlessly with ElevenLabs for creating dubbed videos.

### Workflow

1. **Get original video audio sample** (for voice cloning)
   ```bash
   # Use yt-dlp or similar tool
   yt-dlp -x --audio-format mp3 --postprocessor-args "-ss 00:00:10 -t 00:00:30" \
     "https://www.youtube.com/watch?v=VIDEO_ID"
   ```

2. **Translate transcript**
   ```bash
   curl -X POST https://transcript.youtubesummaries.cc/video-translate \
     -H "Content-Type: application/json" \
     -d '{"url": "VIDEO_ID", "target_language": "Spanish"}' \
     > translation.json
   ```

3. **Clone voice with ElevenLabs**
   ```python
   from elevenlabs import clone, generate, set_api_key

   set_api_key("your-elevenlabs-api-key")

   # Clone the original speaker's voice
   voice = clone(
       name="Original Speaker",
       files=["audio_sample.mp3"]
   )

   # Generate dubbed audio
   translated_text = translation['translated_transcript']
   audio = generate(
       text=translated_text,
       voice=voice,
       model="eleven_multilingual_v2"
   )
   ```

4. **Sync with video** (using FFmpeg or video editing tools)

### Complete Example App

See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) for a full React/Next.js example of building a video translation app.

---

## 🚀 Use Cases

### 1. YouTube-to-Notes App
Convert any YouTube video into structured notes for studying, content creation, or research.

**Target users:**
- Students creating study notes
- Content creators researching topics
- Professionals summarizing talks/tutorials

### 2. Video Translation Tool
Translate YouTube videos to any language and create dubbed versions using AI voice cloning.

**Target users:**
- Content creators expanding to international audiences
- Educators making courses accessible globally
- Media companies localizing content

### 3. YouTube Chapter Generator
Auto-generate chapter markers and descriptions for YouTube videos.

**Target users:**
- YouTubers improving video navigation
- Podcast creators adding timestamps
- Educational content creators

---

## ⚠️ Error Handling

### AI Features Not Available (503)
```json
{
  "detail": "AI features not available. Please configure ANTHROPIC_API_KEY environment variable."
}
```

**Fix:** Set the `ANTHROPIC_API_KEY` in your environment variables.

### Invalid Video URL (400)
```json
{
  "detail": "Invalid YouTube URL"
}
```

**Fix:** Ensure the URL is a valid YouTube video URL or video ID.

### Translation Failed (500)
```json
{
  "detail": "Error translating transcript: ..."
}
```

**Common causes:**
- Video has no captions/transcript
- API rate limit exceeded
- Network timeout

**Fix:** Check video has captions, verify API key is valid, retry request.

---

## 💡 Best Practices

1. **Cache translations** - Store translated transcripts to avoid re-translating
2. **Batch processing** - Use async/await to translate multiple videos in parallel
3. **Language detection** - Check available languages first with `/video-transcript-languages`
4. **Cost optimization** - Use "summary" format for cheaper note generation
5. **Quality check** - Always review AI-generated content before publishing
6. **Rate limiting** - Anthropic has rate limits; implement retry logic

---

## 📊 Performance & Costs

### Response Times
- `/video-notes`: 5-15 seconds (depending on transcript length)
- `/video-translate`: 10-25 seconds (transcript + timestamps)

### Token Usage Estimates
| Video Length | Transcript Tokens | Notes Cost | Translation Cost |
|--------------|------------------|------------|------------------|
| 5 minutes    | ~800 tokens      | $0.01      | $0.02            |
| 15 minutes   | ~2,400 tokens    | $0.04      | $0.07            |
| 30 minutes   | ~5,000 tokens    | $0.08      | $0.13            |
| 60 minutes   | ~10,000 tokens   | $0.15      | $0.25            |

*Costs based on Claude 3.5 Sonnet pricing*

### Optimization Tips
- Use `/video-data` and `/video-captions` first (cached, free)
- Only call AI endpoints when needed
- Consider using Claude Haiku for simpler tasks (cheaper)
- Implement client-side caching of AI responses

---

## 🔗 Related Documentation

- [API Quick Reference](API_QUICK_REFERENCE.md) - All endpoint examples
- [Frontend Integration Guide](FRONTEND_INTEGRATION.md) - React/Vue/Next.js examples
- [Redis Caching](REDIS_SETUP.md) - Speed up non-AI endpoints
- [Changelog](CHANGELOG.md) - Version history

---

## 🎯 Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Add API key to `.env`:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

3. **Start server:**
   ```bash
   uv run python main.py
   ```

4. **Test AI endpoints:**
   ```bash
   ./test_new_endpoints.sh
   ```

5. **Build your app!** 🚀

---

**Questions?** Check out the [main README](README.md) or open an issue!
