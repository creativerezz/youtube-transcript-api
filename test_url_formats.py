#!/usr/bin/env python3
"""
Test script to verify all YouTube URL formats are properly parsed
"""
from main import YouTubeTools

# Test cases for different YouTube URL formats
test_cases = [
    # Direct video ID
    ("dQw4w9WgXcQ", "dQw4w9WgXcQ", "Direct video ID"),

    # Standard watch URLs
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "Standard watch URL"),
    ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "Watch URL without www"),
    ("http://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "HTTP watch URL"),

    # Short URLs (youtu.be)
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ", "youtu.be short URL"),
    ("http://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ", "HTTP youtu.be"),
    ("youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ", "youtu.be without protocol"),

    # With query parameters
    ("https://youtu.be/dQw4w9WgXcQ?t=123", "dQw4w9WgXcQ", "Short URL with timestamp"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest", "dQw4w9WgXcQ", "Watch URL with playlist"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ", "Watch URL with timestamp"),

    # Embed URLs
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Embed URL"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1", "dQw4w9WgXcQ", "Embed URL with params"),

    # Old /v/ format
    ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Old /v/ format"),

    # Shorts
    ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "YouTube Shorts"),
    ("https://youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ", "Shorts without www"),

    # Live
    ("https://www.youtube.com/live/dQw4w9WgXcQ", "dQw4w9WgXcQ", "YouTube Live"),

    # Mobile
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "Mobile YouTube"),

    # Music
    ("https://music.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "YouTube Music"),

    # Without protocol
    ("www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "URL without protocol"),
    ("youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ", "URL without www or protocol"),
]

def test_url_parsing():
    """Test all URL format variations"""
    print("Testing YouTube URL Parser")
    print("=" * 80)

    passed = 0
    failed = 0

    for input_url, expected_id, description in test_cases:
        result = YouTubeTools.get_youtube_video_id(input_url)

        if result == expected_id:
            print(f"✓ PASS: {description}")
            print(f"  Input:    {input_url}")
            print(f"  Expected: {expected_id}")
            print(f"  Got:      {result}")
            passed += 1
        else:
            print(f"✗ FAIL: {description}")
            print(f"  Input:    {input_url}")
            print(f"  Expected: {expected_id}")
            print(f"  Got:      {result}")
            failed += 1
        print()

    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failed == 0:
        print("✓ All tests passed! 🎉")
        return True
    else:
        print(f"✗ {failed} test(s) failed")
        return False

if __name__ == "__main__":
    import sys
    success = test_url_parsing()
    sys.exit(0 if success else 1)
