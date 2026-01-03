-- YouTube Summaries API - D1 Database Schema
-- Migration: 0001_initial_schema
-- Description: Initial schema for persistent transcript storage and video metadata

-- Persistent transcript storage
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    transcript_text TEXT NOT NULL,
    word_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(video_id, language)
);

CREATE INDEX idx_transcripts_video_id ON transcripts(video_id);
CREATE INDEX idx_transcripts_language ON transcripts(language);
CREATE INDEX idx_transcripts_created_at ON transcripts(created_at);

-- Video metadata cache
CREATE TABLE video_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT UNIQUE NOT NULL,
    title TEXT,
    author TEXT,
    thumbnail_url TEXT,
    duration INTEGER,
    metadata_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_video_metadata_video_id ON video_metadata(video_id);
CREATE INDEX idx_video_metadata_created_at ON video_metadata(created_at);

-- Edge analytics (optional - for monitoring cache performance)
CREATE TABLE edge_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    video_id TEXT,
    cache_tier TEXT, -- 'kv', 'upstash', 'origin'
    cache_hit BOOLEAN,
    response_time_ms INTEGER,
    region TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_edge_analytics_endpoint ON edge_analytics(endpoint);
CREATE INDEX idx_edge_analytics_timestamp ON edge_analytics(timestamp);
CREATE INDEX idx_edge_analytics_cache_hit ON edge_analytics(cache_hit);
