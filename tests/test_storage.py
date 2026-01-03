"""
Performance tests for Transcript Storage endpoints.
"""
from config import BASE_URL, PERFORMANCE_ITERATIONS, TEST_VIDEOS, TEST_LANGUAGES, REQUEST_TIMEOUT
from utils import make_request, measure_performance, print_test_header, Colors


def check_storage_available():
    """Check if storage features are available."""
    response, error = make_request("GET", f"{BASE_URL}/health")
    if response and not error:
        data = response.json()
        cache_status = data.get("cache_status", "")
        return "enabled" in cache_status
    return False


def test_transcript_save():
    """Test POST /transcripts/save endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/transcripts/save",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"]
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 2)  # Save fewer times


def test_transcript_get():
    """Test POST /transcripts/get endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/transcripts/get",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"]
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_transcript_list():
    """Test GET /transcripts/list endpoint."""
    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/transcripts/list",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_transcript_stats():
    """Test GET /transcripts/stats endpoint."""
    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/transcripts/stats",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_transcript_delete():
    """Test POST /transcripts/delete endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/transcripts/delete",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"]
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 1)  # Delete only once


def test_storage_workflow():
    """Test complete storage workflow: save -> get -> list -> delete."""
    print(f"\n{Colors.OKBLUE}Testing complete storage workflow...{Colors.ENDC}")

    workflow_steps = [
        ("Save", "POST", "/transcripts/save", {
            "url": TEST_VIDEOS["medium"],
            "languages": TEST_LANGUAGES["primary"]
        }),
        ("Get", "POST", "/transcripts/get", {
            "url": TEST_VIDEOS["medium"],
            "languages": TEST_LANGUAGES["primary"]
        }),
        ("List", "GET", "/transcripts/list", None),
        ("Stats", "GET", "/transcripts/stats", None),
        ("Delete", "POST", "/transcripts/delete", {
            "url": TEST_VIDEOS["medium"],
            "languages": TEST_LANGUAGES["primary"]
        }),
    ]

    all_passed = True

    for step_name, method, endpoint, data in workflow_steps:
        print(f"  {step_name}...", end=" ", flush=True)

        kwargs = {
            "timeout": REQUEST_TIMEOUT,
            "headers": {"Content-Type": "application/json"}
        }

        if data:
            kwargs["json"] = data

        response, error = make_request(method, f"{BASE_URL}{endpoint}", **kwargs)

        if error:
            print(f"{Colors.FAIL}✗ FAILED{Colors.ENDC}: {error}")
            all_passed = False
        elif response and response.status_code < 400:
            print(f"{Colors.OKGREEN}✓ OK{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ FAILED{Colors.ENDC}: HTTP {response.status_code if response else 'N/A'}")
            all_passed = False

    if all_passed:
        print(f"\n  {Colors.OKGREEN}✓ Workflow completed successfully{Colors.ENDC}")
    else:
        print(f"\n  {Colors.FAIL}✗ Workflow had failures{Colors.ENDC}")

    return all_passed


def run_all_tests():
    """Run all storage endpoint tests."""
    print_test_header("TRANSCRIPT STORAGE ENDPOINTS")

    # Check if storage is available
    storage_available = check_storage_available()

    if not storage_available:
        print(f"{Colors.WARNING}⚠ Storage not available (Redis not configured){Colors.ENDC}")
        print(f"{Colors.WARNING}  Skipping storage endpoint tests...{Colors.ENDC}\n")
        return []

    print(f"{Colors.OKGREEN}✓ Storage available{Colors.ENDC}\n")

    results = []

    # Test save
    metrics = test_transcript_save()
    metrics.endpoint_name = "storage_save"
    passed = metrics.print_report()
    results.append(("POST /transcripts/save", passed))

    # Test get
    metrics = test_transcript_get()
    metrics.endpoint_name = "storage_get"
    passed = metrics.print_report()
    results.append(("POST /transcripts/get", passed))

    # Test list
    metrics = test_transcript_list()
    metrics.endpoint_name = "storage_list"
    passed = metrics.print_report()
    results.append(("GET /transcripts/list", passed))

    # Test stats
    metrics = test_transcript_stats()
    metrics.endpoint_name = "storage_stats"
    passed = metrics.print_report()
    results.append(("GET /transcripts/stats", passed))

    # Test delete
    metrics = test_transcript_delete()
    metrics.endpoint_name = "storage_delete"
    passed = metrics.print_report()
    results.append(("POST /transcripts/delete", passed))

    # Test complete workflow
    print_test_header("STORAGE WORKFLOW TEST")
    workflow_passed = test_storage_workflow()
    results.append(("Storage Workflow", workflow_passed))

    return results


if __name__ == "__main__":
    from utils import print_summary

    results = run_all_tests()
    if results:
        print_summary(results)
