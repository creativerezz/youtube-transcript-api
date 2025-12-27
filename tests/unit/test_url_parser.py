"""Tests for YouTube URL parsing."""

import pytest

from src.youtube_api.utils.url_parser import get_youtube_video_id


class TestGetYoutubeVideoId:
    """Test cases for get_youtube_video_id function."""

    # Direct video ID
    def test_direct_video_id(self):
        """Test parsing direct video ID."""
        assert get_youtube_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Standard watch URLs
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ],
    )
    def test_standard_watch_urls(self, url, expected):
        """Test standard YouTube watch URLs."""
        assert get_youtube_video_id(url) == expected

    # Short URLs (youtu.be)
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ],
    )
    def test_short_urls(self, url, expected):
        """Test youtu.be short URLs."""
        assert get_youtube_video_id(url) == expected

    # URLs with query parameters
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://youtu.be/dQw4w9WgXcQ?t=123", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ"),
        ],
    )
    def test_urls_with_params(self, url, expected):
        """Test URLs with additional query parameters."""
        assert get_youtube_video_id(url) == expected

    # Embed URLs
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1", "dQw4w9WgXcQ"),
        ],
    )
    def test_embed_urls(self, url, expected):
        """Test embed URLs."""
        assert get_youtube_video_id(url) == expected

    # Old /v/ format
    def test_old_v_format(self):
        """Test old /v/ format URL."""
        assert get_youtube_video_id("https://www.youtube.com/v/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Shorts URLs
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ],
    )
    def test_shorts_urls(self, url, expected):
        """Test YouTube Shorts URLs."""
        assert get_youtube_video_id(url) == expected

    # Live URLs
    def test_live_url(self):
        """Test YouTube Live URL."""
        assert get_youtube_video_id("https://www.youtube.com/live/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Mobile URLs
    def test_mobile_url(self):
        """Test mobile YouTube URL."""
        assert get_youtube_video_id("https://m.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # YouTube Music
    def test_music_url(self):
        """Test YouTube Music URL."""
        assert get_youtube_video_id("https://music.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # URLs without protocol
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ],
    )
    def test_urls_without_protocol(self, url, expected):
        """Test URLs without protocol prefix."""
        assert get_youtube_video_id(url) == expected

    # Invalid inputs
    @pytest.mark.parametrize(
        "url",
        [
            "",
            "invalid",
            "https://example.com/watch?v=test",
            "not_a_video_id_too_long",
        ],
    )
    def test_invalid_inputs(self, url):
        """Test invalid URL inputs return None."""
        assert get_youtube_video_id(url) is None
