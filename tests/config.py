"""
Test configuration and settings.
"""
import os

# Base API URL
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Test YouTube video URLs
TEST_VIDEOS = {
    "short": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    "medium": "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo (first YouTube video)
    "long": "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style
}

# Performance thresholds (in seconds)
PERFORMANCE_THRESHOLDS = {
    "health": 0.1,
    "cache_stats": 1.5,  # Increased - Redis stats can be slow on first call
    "video_data": 2.0,
    "video_captions": 5.0,
    "video_timestamps": 5.0,
    "video_languages": 3.0,
    "video_notes": 30.0,
    "video_translate": 45.0,
    "openrouter_proxy": 10.0,
    "storage_save": 3.0,
    "storage_get": 0.5,
    "storage_list": 1.0,
    "storage_delete": 0.5,
    "storage_stats": 1.5,  # Increased - Redis stats can vary
    "prompts_list": 0.5,
    "prompts_get": 0.2,
}

# Test languages
TEST_LANGUAGES = {
    "primary": ["en"],
    "fallback": ["en", "es", "fr"],
}

# Number of iterations for performance tests
PERFORMANCE_ITERATIONS = 5

# Request timeout (seconds)
REQUEST_TIMEOUT = 60

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
