"""
Performance tests for AI-powered endpoints.
"""
import os
from config import BASE_URL, PERFORMANCE_ITERATIONS, TEST_VIDEOS, TEST_LANGUAGES, REQUEST_TIMEOUT
from utils import make_request, measure_performance, print_test_header, Colors


def check_ai_available():
    """Check if AI features are available."""
    response, error = make_request("GET", f"{BASE_URL}/")
    if response and not error:
        data = response.json()
        return data.get("ai_features_available", False)
    return False


def test_video_notes_structured():
    """Test POST /video-notes with structured format."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-notes",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"],
                "format": "structured"
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 2)  # Fewer iterations for AI endpoints


def test_video_notes_summary():
    """Test POST /video-notes with summary format."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-notes",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"],
                "format": "summary"
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 2)


def test_video_notes_detailed():
    """Test POST /video-notes with detailed format."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-notes",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"],
                "format": "detailed"
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 2)


def test_video_translate():
    """Test POST /video-translate endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-translate",
            json={
                "url": TEST_VIDEOS["short"],
                "source_languages": TEST_LANGUAGES["primary"],
                "target_language": "Spanish"
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 2)


def test_openrouter_proxy():
    """Test POST /openrouter-proxy endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/openrouter-proxy",
            json={
                "prompt": "What is 2+2?",
                "model": "xiaomi/mimo-v2-flash:free",
                "max_tokens": 100
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 2)


def run_all_tests():
    """Run all AI endpoint tests."""
    print_test_header("AI-POWERED ENDPOINTS")

    # Check if AI is available
    ai_available = check_ai_available()

    if not ai_available:
        print(f"{Colors.WARNING}⚠ AI features not available (OPENROUTER_API_KEY not configured){Colors.ENDC}")
        print(f"{Colors.WARNING}  Skipping AI endpoint tests...{Colors.ENDC}\n")
        return []

    print(f"{Colors.OKGREEN}✓ AI features available{Colors.ENDC}\n")

    results = []

    # Test video notes - structured
    metrics = test_video_notes_structured()
    metrics.endpoint_name = "video_notes"
    passed = metrics.print_report()
    results.append(("POST /video-notes (structured)", passed))

    # Test video notes - summary
    metrics = test_video_notes_summary()
    metrics.endpoint_name = "video_notes"
    passed = metrics.print_report()
    results.append(("POST /video-notes (summary)", passed))

    # Test video notes - detailed
    metrics = test_video_notes_detailed()
    metrics.endpoint_name = "video_notes"
    passed = metrics.print_report()
    results.append(("POST /video-notes (detailed)", passed))

    # Test translation
    metrics = test_video_translate()
    metrics.endpoint_name = "video_translate"
    passed = metrics.print_report()
    results.append(("POST /video-translate", passed))

    # Test OpenRouter proxy
    metrics = test_openrouter_proxy()
    metrics.endpoint_name = "openrouter_proxy"
    passed = metrics.print_report()
    results.append(("POST /openrouter-proxy", passed))

    return results


if __name__ == "__main__":
    from utils import print_summary

    results = run_all_tests()
    if results:
        print_summary(results)
