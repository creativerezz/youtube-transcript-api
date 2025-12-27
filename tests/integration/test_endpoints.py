"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health and info endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "YouTube Tools API"
        assert "version" in data
        assert "endpoints" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "cache_status" in data
        assert "proxy_status" in data

    def test_cache_stats_endpoint(self, client):
        """Test cache stats endpoint."""
        response = client.get("/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "status" in data


class TestVideoEndpoints:
    """Test video data endpoints."""

    def test_video_data_missing_url(self, client):
        """Test video-data endpoint with missing URL."""
        response = client.post("/video-data", json={})
        assert response.status_code == 422  # Validation error

    def test_video_captions_missing_url(self, client):
        """Test video-captions endpoint with missing URL."""
        response = client.post("/video-captions", json={})
        assert response.status_code == 422

    def test_video_timestamps_missing_url(self, client):
        """Test video-timestamps endpoint with missing URL."""
        response = client.post("/video-timestamps", json={})
        assert response.status_code == 422

    def test_video_languages_missing_url(self, client):
        """Test video-transcript-languages endpoint with missing URL."""
        response = client.post("/video-transcript-languages", json={})
        assert response.status_code == 422

    @pytest.mark.skip(reason="Requires network access to YouTube")
    def test_video_data_valid_url(self, client, sample_video_url):
        """Test video-data endpoint with valid URL."""
        response = client.post("/video-data", json={"url": sample_video_url})
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "author_name" in data


class TestAIEndpoints:
    """Test AI-powered endpoints."""

    def test_video_notes_missing_url(self, client):
        """Test video-notes endpoint with missing URL."""
        response = client.post("/video-notes", json={})
        assert response.status_code == 422

    def test_video_translate_missing_fields(self, client):
        """Test video-translate endpoint with missing fields."""
        response = client.post("/video-translate", json={"url": "test"})
        assert response.status_code == 422  # Missing target_language

    def test_video_notes_request_validation(self, client):
        """Test video-notes request validation."""
        response = client.post(
            "/video-notes",
            json={
                "url": "test_url",
                "format": "invalid_format",  # Should only allow: structured, summary, detailed
            },
        )
        assert response.status_code == 422
