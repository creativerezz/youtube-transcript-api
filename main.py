"""
YouTube API Server - Entry Point

This is a thin wrapper that imports and runs the FastAPI application.
The actual application logic is in src/youtube_api/
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.youtube_api.app import app  # noqa: E402

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(app, host=host, port=port)
