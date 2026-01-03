#!/usr/bin/env python3
"""
Master test runner for all API performance tests.
"""
import sys
import time
import argparse
from datetime import datetime
from config import BASE_URL, Colors
from utils import print_test_header, print_summary, make_request

# Import test modules
import test_health
import test_video
import test_ai
import test_storage
import test_prompts


def check_api_health():
    """Check if API is running and healthy."""
    print(f"{Colors.OKBLUE}Checking API health...{Colors.ENDC}")
    print(f"  API URL: {BASE_URL}")

    response, error = make_request("GET", f"{BASE_URL}/health", timeout=5)

    if error:
        print(f"  {Colors.FAIL}✗ API is not responding{Colors.ENDC}")
        print(f"  Error: {error}")
        return False

    if response and response.status_code == 200:
        data = response.json()
        print(f"  {Colors.OKGREEN}✓ API is healthy{Colors.ENDC}")
        print(f"  Status: {data.get('status')}")
        print(f"  Cache: {data.get('cache_status')}")
        print(f"  Proxy: {data.get('proxy_status')}")
        return True

    print(f"  {Colors.FAIL}✗ API returned status {response.status_code}{Colors.ENDC}")
    return False


def run_test_suite(suite_name, test_module, skip=False):
    """
    Run a test suite and return results.

    Args:
        suite_name: Name of test suite
        test_module: Module containing tests
        skip: Whether to skip this suite

    Returns:
        List of (test_name, passed) tuples
    """
    if skip:
        print(f"\n{Colors.WARNING}Skipping {suite_name}...{Colors.ENDC}")
        return []

    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 70)
    print(f"  Running {suite_name}")
    print("=" * 70)
    print(f"{Colors.ENDC}")

    start_time = time.time()
    results = test_module.run_all_tests()
    elapsed = time.time() - start_time

    print(f"\n{Colors.OKCYAN}Suite completed in {elapsed:.2f}s{Colors.ENDC}")

    return results


def generate_report(all_results, total_time):
    """Generate and print final test report."""
    print(f"\n\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 70)
    print("  FINAL TEST REPORT")
    print("=" * 70)
    print(f"{Colors.ENDC}")

    # Calculate totals
    total_tests = len(all_results)
    passed_tests = sum(1 for _, result in all_results if result)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Summary statistics
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"  Total Time:   {total_time:.2f}s")
    print(f"  Total Tests:  {total_tests}")
    print(f"  {Colors.OKGREEN}Passed:       {passed_tests}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Failed:       {failed_tests}{Colors.ENDC}")
    print(f"  Success Rate: {success_rate:.1f}%")

    # Detailed results
    print(f"\n{Colors.BOLD}Detailed Results:{Colors.ENDC}")

    # Group by suite
    suites = {}
    for test_name, result in all_results:
        # Extract suite name from test name
        if "POST" in test_name or "GET" in test_name:
            suite = test_name.split()[1].split("/")[1] if "/" in test_name else "Other"
        else:
            suite = "Other"

        if suite not in suites:
            suites[suite] = []
        suites[suite].append((test_name, result))

    for suite_name, tests in sorted(suites.items()):
        print(f"\n  {Colors.BOLD}{suite_name}:{Colors.ENDC}")
        for test_name, result in tests:
            status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if result else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
            print(f"    {test_name:50s} {status}")

    # Final status
    print(f"\n{Colors.BOLD}Overall Status:{Colors.ENDC}")
    if failed_tests == 0:
        print(f"  {Colors.OKGREEN}✓ ALL TESTS PASSED{Colors.ENDC}\n")
        return 0
    else:
        print(f"  {Colors.FAIL}✗ SOME TESTS FAILED{Colors.ENDC}\n")
        return 1


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run API performance tests")
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Skip health endpoint tests"
    )
    parser.add_argument(
        "--skip-video",
        action="store_true",
        help="Skip video endpoint tests"
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip AI endpoint tests"
    )
    parser.add_argument(
        "--skip-storage",
        action="store_true",
        help="Skip storage endpoint tests"
    )
    parser.add_argument(
        "--skip-prompts",
        action="store_true",
        help="Skip prompt endpoint tests"
    )
    parser.add_argument(
        "--only",
        choices=["health", "video", "ai", "storage", "prompts"],
        help="Run only specified test suite"
    )

    args = parser.parse_args()

    # Print header
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 70)
    print("  YouTube Summaries API - Performance Test Suite")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    print(f"  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Base URL:   {BASE_URL}\n")

    # Check API health
    if not check_api_health():
        print(f"\n{Colors.FAIL}✗ API health check failed. Please start the API server first.{Colors.ENDC}")
        print(f"\n  To start the server, run:")
        print(f"    uv run uvicorn main:app --reload\n")
        return 1

    print()

    # Determine which suites to run
    skip_health = args.skip_health or (args.only and args.only != "health")
    skip_video = args.skip_video or (args.only and args.only != "video")
    skip_ai = args.skip_ai or (args.only and args.only != "ai")
    skip_storage = args.skip_storage or (args.only and args.only != "storage")
    skip_prompts = args.skip_prompts or (args.only and args.only != "prompts")

    # Run test suites
    start_time = time.time()
    all_results = []

    # Health tests
    results = run_test_suite("Health & Cache Tests", test_health, skip_health)
    all_results.extend(results)

    # Video tests
    results = run_test_suite("Video Data Tests", test_video, skip_video)
    all_results.extend(results)

    # AI tests
    results = run_test_suite("AI Features Tests", test_ai, skip_ai)
    all_results.extend(results)

    # Storage tests
    results = run_test_suite("Storage Tests", test_storage, skip_storage)
    all_results.extend(results)

    # Prompts tests
    results = run_test_suite("Prompts Tests", test_prompts, skip_prompts)
    all_results.extend(results)

    total_time = time.time() - start_time

    # Generate final report
    exit_code = generate_report(all_results, total_time)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
