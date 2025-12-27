# Frontend Integration Guide

Complete reference for consuming the YouTube API Server from frontend applications.

## Base URL

```javascript
const API_BASE_URL = 'https://transcript.youtubesummaries.cc';
```

## API Endpoints Overview

| Endpoint | Method | Purpose | Cache | Response Time |
|----------|--------|---------|-------|---------------|
| `/health` | GET | Server health check | No | ~100ms |
| `/cache/stats` | GET | Cache statistics | No | ~100ms |
| `/cache/clear` | POST | Clear all cache | No | ~100ms |
| `/video-data` | POST | Video metadata | ✅ Yes | 50-100ms (cached) / 1-3s (uncached) |
| `/video-captions` | POST | Full transcript | ✅ Yes | 100-200ms (cached) / 5-15s (uncached) |
| `/video-timestamps` | POST | Timestamped transcript | ✅ Yes | 100-200ms (cached) / 5-15s (uncached) |
| `/video-transcript-languages` | POST | Available languages | ✅ Yes | 50-100ms (cached) / 1-3s (uncached) |

---

## JavaScript/TypeScript Examples

### Basic Fetch API

```javascript
// Get video metadata
async function getVideoData(youtubeUrl) {
  const response = await fetch('https://transcript.youtubesummaries.cc/video-data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: youtubeUrl })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// Usage
const data = await getVideoData('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
console.log(data.title); // "Rick Astley - Never Gonna Give You Up..."
```

### TypeScript with Type Definitions

```typescript
// Type definitions
interface VideoData {
  title: string;
  author_name: string;
  author_url: string;
  type: string;
  height: number;
  width: number;
  version: string;
  provider_name: string;
  provider_url: string;
  thumbnail_url: string;
}

interface CaptionsResponse {
  captions: string;
}

interface TimestampsResponse {
  timestamps: string[];
}

interface TranscriptLanguage {
  language: string;
  language_code: string;
  is_generated: boolean;
  is_translatable: boolean;
}

interface LanguagesResponse {
  available_languages: TranscriptLanguage[];
}

interface HealthResponse {
  status: string;
  timestamp: string;
  proxy_status: string;
  proxy_username: string | null;
  cache_status: string;
  cache_ttl_seconds: number | null;
  parallel_processing: string;
}

interface CacheStats {
  enabled: boolean;
  status: string;
  total_keys: number;
  ttl_seconds: number;
  keyspace_hits: number;
  keyspace_misses: number;
}

// API Client class
class YouTubeAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'https://transcript.youtubesummaries.cc') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    method: 'GET' | 'POST' = 'GET',
    body?: object
  ): Promise<T> {
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  }

  // Get video metadata
  async getVideoData(url: string): Promise<VideoData> {
    return this.request<VideoData>('/video-data', 'POST', { url });
  }

  // Get video captions/transcript
  async getCaptions(url: string, languages?: string[]): Promise<CaptionsResponse> {
    return this.request<CaptionsResponse>('/video-captions', 'POST', {
      url,
      languages,
    });
  }

  // Get timestamped transcript
  async getTimestamps(url: string, languages?: string[]): Promise<TimestampsResponse> {
    return this.request<TimestampsResponse>('/video-timestamps', 'POST', {
      url,
      languages,
    });
  }

  // Get available transcript languages
  async getLanguages(url: string): Promise<LanguagesResponse> {
    return this.request<LanguagesResponse>('/video-transcript-languages', 'POST', { url });
  }

  // Health check
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  // Cache statistics
  async cacheStats(): Promise<CacheStats> {
    return this.request<CacheStats>('/cache/stats');
  }

  // Clear cache (use sparingly)
  async clearCache(): Promise<{ success: boolean; message: string; timestamp: string }> {
    return this.request('/cache/clear', 'POST');
  }
}

// Usage
const api = new YouTubeAPIClient();

// Get video data
const videoData = await api.getVideoData('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
console.log(videoData.title);

// Get captions in specific language
const captions = await api.getCaptions(
  'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
  ['es', 'en'] // Spanish preferred, English fallback
);

// Get available languages first
const languages = await api.getLanguages('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
console.log(languages.available_languages);
```

---

## React Examples

### React Hooks

```tsx
import { useState, useEffect } from 'react';

// Custom hook for video data
function useVideoData(youtubeUrl: string | null) {
  const [data, setData] = useState<VideoData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!youtubeUrl) return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('https://transcript.youtubesummaries.cc/video-data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: youtubeUrl }),
        });

        if (!response.ok) throw new Error('Failed to fetch video data');

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [youtubeUrl]);

  return { data, loading, error };
}

// Usage in component
function VideoInfo({ url }: { url: string }) {
  const { data, loading, error } = useVideoData(url);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return null;

  return (
    <div>
      <h2>{data.title}</h2>
      <p>By: {data.author_name}</p>
      <img src={data.thumbnail_url} alt={data.title} />
    </div>
  );
}
```

### React Component with Captions

```tsx
import { useState } from 'react';

function TranscriptViewer() {
  const [url, setUrl] = useState('');
  const [captions, setCaptions] = useState('');
  const [loading, setLoading] = useState(false);
  const [cached, setCached] = useState(false);

  const fetchCaptions = async () => {
    setLoading(true);
    const startTime = Date.now();

    try {
      const response = await fetch('https://transcript.youtubesummaries.cc/video-captions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();
      setCaptions(data.captions);

      // If response was very fast, it was likely cached
      const responseTime = Date.now() - startTime;
      setCached(responseTime < 500);
    } catch (error) {
      console.error('Error fetching captions:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="YouTube URL"
      />
      <button onClick={fetchCaptions} disabled={loading}>
        {loading ? 'Loading...' : 'Get Transcript'}
      </button>

      {cached && <span style={{ color: 'green' }}>⚡ Cached (Fast!)</span>}

      {captions && (
        <div style={{ whiteSpace: 'pre-wrap', marginTop: '20px' }}>
          {captions}
        </div>
      )}
    </div>
  );
}
```

---

## Vue.js Examples

### Vue 3 Composition API

```vue
<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{ youtubeUrl: string }>();

const videoData = ref<VideoData | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

async function fetchVideoData() {
  if (!props.youtubeUrl) return;

  loading.value = true;
  error.value = null;

  try {
    const response = await fetch('https://transcript.youtubesummaries.cc/video-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: props.youtubeUrl }),
    });

    if (!response.ok) throw new Error('Failed to fetch');

    videoData.value = await response.json();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error';
  } finally {
    loading.value = false;
  }
}

watch(() => props.youtubeUrl, fetchVideoData, { immediate: true });
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else-if="videoData">
      <h2>{{ videoData.title }}</h2>
      <p>{{ videoData.author_name }}</p>
      <img :src="videoData.thumbnail_url" :alt="videoData.title" />
    </div>
  </div>
</template>
```

---

## Next.js Examples

### Server-Side Rendering (App Router)

```typescript
// app/video/[id]/page.tsx
import { YouTubeAPIClient } from '@/lib/youtube-api';

interface PageProps {
  params: { id: string };
}

export default async function VideoPage({ params }: PageProps) {
  const api = new YouTubeAPIClient();
  const url = `https://www.youtube.com/watch?v=${params.id}`;

  // Server-side fetch (benefits from caching)
  const [videoData, languages] = await Promise.all([
    api.getVideoData(url),
    api.getLanguages(url),
  ]);

  return (
    <div>
      <h1>{videoData.title}</h1>
      <p>By: {videoData.author_name}</p>

      <h2>Available Languages:</h2>
      <ul>
        {languages.available_languages.map((lang) => (
          <li key={lang.language_code}>
            {lang.language} ({lang.language_code})
            {lang.is_generated && ' - Auto-generated'}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Enable Next.js caching (revalidate every hour to match API cache)
export const revalidate = 3600;
```

### API Route (Pages Router)

```typescript
// pages/api/transcript/[videoId].ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { videoId } = req.query;
  const url = `https://www.youtube.com/watch?v=${videoId}`;

  try {
    const response = await fetch('https://transcript.youtubesummaries.cc/video-captions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();

    // Set cache headers to match API cache (1 hour)
    res.setHeader('Cache-Control', 'public, s-maxage=3600, stale-while-revalidate=7200');
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch transcript' });
  }
}
```

---

## Error Handling

### Comprehensive Error Handling

```typescript
class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function safeAPICall<T>(
  endpoint: string,
  options: RequestInit
): Promise<T> {
  try {
    const response = await fetch(endpoint, options);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || 'API request failed',
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Network errors
    if (error instanceof TypeError) {
      throw new APIError('Network error - check your connection', 0);
    }

    throw new APIError('Unknown error occurred', 500, error);
  }
}

// Usage with error handling
try {
  const data = await safeAPICall<VideoData>(
    'https://transcript.youtubesummaries.cc/video-data',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: youtubeUrl }),
    }
  );
  console.log(data);
} catch (error) {
  if (error instanceof APIError) {
    if (error.statusCode === 400) {
      console.error('Invalid YouTube URL');
    } else if (error.statusCode === 500) {
      console.error('Server error:', error.message);
    }
  }
}
```

---

## Performance Optimization

### Caching Strategy

```typescript
// Client-side cache layer (in addition to server-side Redis)
class CachedYouTubeAPI extends YouTubeAPIClient {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private cacheDuration = 5 * 60 * 1000; // 5 minutes

  private getCacheKey(endpoint: string, params: object): string {
    return `${endpoint}:${JSON.stringify(params)}`;
  }

  async getVideoData(url: string): Promise<VideoData> {
    const cacheKey = this.getCacheKey('/video-data', { url });
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheDuration) {
      return cached.data;
    }

    const data = await super.getVideoData(url);
    this.cache.set(cacheKey, { data, timestamp: Date.now() });
    return data;
  }
}
```

### Request Deduplication

```typescript
class RequestDeduplicator {
  private pending = new Map<string, Promise<any>>();

  async request<T>(key: string, fn: () => Promise<T>): Promise<T> {
    // If request is already pending, return the same promise
    if (this.pending.has(key)) {
      return this.pending.get(key)!;
    }

    const promise = fn()
      .finally(() => this.pending.delete(key));

    this.pending.set(key, promise);
    return promise;
  }
}

const deduplicator = new RequestDeduplicator();

// Usage - multiple calls will only trigger one request
async function getVideoDataDeduplicated(url: string) {
  return deduplicator.request(`video-data:${url}`, async () => {
    const response = await fetch('https://transcript.youtubesummaries.cc/video-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    return response.json();
  });
}
```

---

## Best Practices

### 1. URL Validation

```typescript
function isValidYouTubeUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return (
      (parsed.hostname === 'www.youtube.com' || parsed.hostname === 'youtube.com') &&
      (parsed.pathname === '/watch' || parsed.pathname.startsWith('/embed/'))
    ) || parsed.hostname === 'youtu.be';
  } catch {
    return false;
  }
}

// Usage
if (!isValidYouTubeUrl(userInput)) {
  throw new Error('Invalid YouTube URL');
}
```

### 2. Loading States

```typescript
interface LoadingState {
  idle: boolean;
  loading: boolean;
  success: boolean;
  error: string | null;
}

function useAPIState<T>() {
  const [state, setState] = useState<LoadingState>({
    idle: true,
    loading: false,
    success: false,
    error: null,
  });
  const [data, setData] = useState<T | null>(null);

  const execute = async (apiCall: () => Promise<T>) => {
    setState({ idle: false, loading: true, success: false, error: null });

    try {
      const result = await apiCall();
      setData(result);
      setState({ idle: false, loading: false, success: true, error: null });
      return result;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setState({ idle: false, loading: false, success: false, error: message });
      throw error;
    }
  };

  return { state, data, execute };
}
```

### 3. Retry Logic

```typescript
async function fetchWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  delay = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;

      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
  throw new Error('Max retries exceeded');
}

// Usage
const data = await fetchWithRetry(() =>
  api.getVideoData('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
);
```

---

## Complete Example Application

```typescript
// Complete React component with all features
import React, { useState } from 'react';

interface VideoAnalyzerProps {
  apiUrl?: string;
}

export function VideoAnalyzer({ apiUrl = 'https://transcript.youtubesummaries.cc' }: VideoAnalyzerProps) {
  const [url, setUrl] = useState('');
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [captions, setCaptions] = useState('');
  const [languages, setLanguages] = useState<TranscriptLanguage[]>([]);
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['en']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);

  const fetchAll = async () => {
    if (!url) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch video data and available languages in parallel
      const [video, langs] = await Promise.all([
        fetch(`${apiUrl}/video-data`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url }),
        }).then(r => r.json()),
        fetch(`${apiUrl}/video-transcript-languages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url }),
        }).then(r => r.json()),
      ]);

      setVideoData(video);
      setLanguages(langs.available_languages);

      // Fetch captions with selected languages
      const captionsResponse = await fetch(`${apiUrl}/video-captions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, languages: selectedLanguages }),
      });
      const captionsData = await captionsResponse.json();
      setCaptions(captionsData.captions);

      // Update cache stats
      const stats = await fetch(`${apiUrl}/cache/stats`).then(r => r.json());
      setCacheStats(stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>YouTube Video Analyzer</h1>

      {/* Cache Stats */}
      {cacheStats && (
        <div style={{ background: '#f0f0f0', padding: '10px', marginBottom: '20px' }}>
          <strong>Cache Performance:</strong> {cacheStats.keyspace_hits} hits, {cacheStats.keyspace_misses} misses
          ({cacheStats.total_keys} items cached)
        </div>
      )}

      {/* Input */}
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="YouTube URL"
          style={{ width: '100%', padding: '10px', fontSize: '16px' }}
        />
        <button
          onClick={fetchAll}
          disabled={loading || !url}
          style={{ marginTop: '10px', padding: '10px 20px', fontSize: '16px' }}
        >
          {loading ? 'Loading...' : 'Analyze Video'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          Error: {error}
        </div>
      )}

      {/* Video Info */}
      {videoData && (
        <div style={{ marginBottom: '20px' }}>
          <img
            src={videoData.thumbnail_url}
            alt={videoData.title}
            style={{ width: '100%', maxWidth: '400px' }}
          />
          <h2>{videoData.title}</h2>
          <p>By: {videoData.author_name}</p>
        </div>
      )}

      {/* Languages */}
      {languages.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h3>Available Languages:</h3>
          <div>
            {languages.map(lang => (
              <label key={lang.language_code} style={{ display: 'block', margin: '5px 0' }}>
                <input
                  type="checkbox"
                  checked={selectedLanguages.includes(lang.language_code)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedLanguages([...selectedLanguages, lang.language_code]);
                    } else {
                      setSelectedLanguages(selectedLanguages.filter(l => l !== lang.language_code));
                    }
                  }}
                />
                {lang.language} ({lang.language_code})
                {lang.is_generated && ' - Auto-generated'}
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Captions */}
      {captions && (
        <div>
          <h3>Transcript:</h3>
          <div style={{
            whiteSpace: 'pre-wrap',
            background: '#f9f9f9',
            padding: '15px',
            borderRadius: '5px',
            maxHeight: '400px',
            overflow: 'auto'
          }}>
            {captions}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Testing

### Example Test Suite (Jest + React Testing Library)

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VideoAnalyzer } from './VideoAnalyzer';

// Mock fetch
global.fetch = jest.fn();

describe('VideoAnalyzer', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  it('fetches and displays video data', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        title: 'Test Video',
        author_name: 'Test Author',
        thumbnail_url: 'https://example.com/thumb.jpg',
      }),
    });

    render(<VideoAnalyzer />);

    const input = screen.getByPlaceholderText('YouTube URL');
    await userEvent.type(input, 'https://www.youtube.com/watch?v=test');

    const button = screen.getByText('Analyze Video');
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Test Video')).toBeInTheDocument();
    });
  });
});
```

---

## Rate Limiting & Best Practices

1. **Respect the cache**: Don't bypass caching by adding random parameters
2. **Use proper HTTP status codes**: Handle 400, 500 errors appropriately
3. **Implement client-side caching**: Add an additional cache layer for frequently accessed data
4. **Monitor cache hit rate**: Use `/cache/stats` to verify caching is working
5. **Handle slow first requests**: Show appropriate loading states for uncached requests
6. **Batch requests**: Use Promise.all() when fetching multiple endpoints

---

## Resources

- **API Base URL**: https://transcript.youtubesummaries.cc
- **API Documentation**: `/docs` (FastAPI auto-generated)
- **Health Check**: `/health`
- **Cache Statistics**: `/cache/stats`

For more information, see:
- [Main README](README.md)
- [Redis Setup Guide](REDIS_SETUP.md)
- [Caching Implementation Details](CACHING_IMPROVEMENTS.md)
