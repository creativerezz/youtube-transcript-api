"""
Performance tests for Health & Cache endpoints.
"""
from config import BASE_URL, PERFORMANCE_ITERATIONS
from utils import make_request, measure_performance, print_test_header


def test_root():
    """Test GET / endpoint."""
    def _test():
        return make_request("GET", f"{BASE_URL}/")

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_health():
    """Test GET /health endpoint."""
    def _test():
        return make_request("GET", f"{BASE_URL}/health")

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_cache_stats():
    """Test GET /cache/stats endpoint."""
    def _test():
        return make_request("GET", f"{BASE_URL}/cache/stats")

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_cache_clear():
    """Test POST /cache/clear endpoint."""
    def _test():
        return make_request("POST", f"{BASE_URL}/cache/clear")

    # Only run once to avoid clearing cache multiple times
    return measure_performance(_test, 1)


def run_all_tests():
    """Run all health endpoint tests."""
    print_test_header("HEALTH & CACHE ENDPOINTS")

    results = []

    # Test endpoints
    metrics = test_root()
    metrics.endpoint_name = "root"
    passed = metrics.print_report()
    results.append(("GET /", passed))

    metrics = test_health()
    metrics.endpoint_name = "health"
    passed = metrics.print_report()
    results.append(("GET /health", passed))

    metrics = test_cache_stats()
    metrics.endpoint_name = "cache_stats"
    passed = metrics.print_report()
    results.append(("GET /cache/stats", passed))

    metrics = test_cache_clear()
    metrics.endpoint_name = "cache_clear"
    passed = metrics.print_report()
    results.append(("POST /cache/clear", passed))

    return results


if __name__ == "__main__":
    from utils import print_summary

    results = run_all_tests()
    print_summary(results)
