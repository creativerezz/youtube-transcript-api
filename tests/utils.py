"""
Utility functions for performance testing.
"""
import time
import statistics
from typing import Dict, List, Callable, Any
import requests
from config import Colors, PERFORMANCE_THRESHOLDS


class PerformanceMetrics:
    """Track and display performance metrics for API tests."""

    def __init__(self, endpoint_name: str):
        self.endpoint_name = endpoint_name
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.success_count = 0
        self.failure_count = 0

    def add_result(self, response_time: float, status_code: int, error: str = None):
        """Add a test result."""
        self.response_times.append(response_time)
        self.status_codes.append(status_code)

        if error:
            self.errors.append(error)
            self.failure_count += 1
        else:
            self.success_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Calculate statistics from collected metrics."""
        if not self.response_times:
            return {}

        return {
            "min": min(self.response_times),
            "max": max(self.response_times),
            "mean": statistics.mean(self.response_times),
            "median": statistics.median(self.response_times),
            "stdev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
            "total_requests": len(self.response_times),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (self.success_count / len(self.response_times)) * 100,
        }

    def print_report(self):
        """Print a formatted performance report."""
        stats = self.get_stats()

        if not stats:
            print(f"{Colors.WARNING}No data collected for {self.endpoint_name}{Colors.ENDC}")
            return

        threshold = PERFORMANCE_THRESHOLDS.get(self.endpoint_name, 1.0)
        passed = stats["mean"] <= threshold

        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}Performance Report: {self.endpoint_name}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")

        # Response times
        print(f"\n{Colors.OKCYAN}Response Times (seconds):{Colors.ENDC}")
        print(f"  Min:     {stats['min']:.3f}s")
        print(f"  Max:     {stats['max']:.3f}s")
        print(f"  Mean:    {stats['mean']:.3f}s")
        print(f"  Median:  {stats['median']:.3f}s")
        print(f"  StdDev:  {stats['stdev']:.3f}s")

        # Throughput
        print(f"\n{Colors.OKCYAN}Throughput:{Colors.ENDC}")
        print(f"  Requests/sec: {1/stats['mean']:.2f}")

        # Success rate
        print(f"\n{Colors.OKCYAN}Reliability:{Colors.ENDC}")
        print(f"  Total Requests:  {stats['total_requests']}")
        print(f"  Successful:      {stats['success_count']}")
        print(f"  Failed:          {stats['failure_count']}")
        print(f"  Success Rate:    {stats['success_rate']:.1f}%")

        # Status codes
        status_counts = {}
        for code in self.status_codes:
            status_counts[code] = status_counts.get(code, 0) + 1

        print(f"\n{Colors.OKCYAN}Status Codes:{Colors.ENDC}")
        for code, count in sorted(status_counts.items()):
            print(f"  {code}: {count}")

        # Errors
        if self.errors:
            print(f"\n{Colors.WARNING}Errors:{Colors.ENDC}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")

        # Performance threshold check
        print(f"\n{Colors.OKCYAN}Performance Threshold:{Colors.ENDC}")
        print(f"  Expected:  ≤ {threshold:.3f}s")
        print(f"  Actual:    {stats['mean']:.3f}s")

        if passed:
            print(f"  {Colors.OKGREEN}✓ PASSED{Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}✗ FAILED{Colors.ENDC}")

        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

        return passed


def measure_performance(func: Callable, iterations: int = 5) -> PerformanceMetrics:
    """
    Measure performance of a function over multiple iterations.

    Args:
        func: Function to test (should return (response, error))
        iterations: Number of times to run the test

    Returns:
        PerformanceMetrics object with collected data
    """
    metrics = PerformanceMetrics(func.__name__)

    print(f"\n{Colors.OKBLUE}Testing {func.__name__}...{Colors.ENDC}")

    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)

        start_time = time.time()
        try:
            response, error = func()
            response_time = time.time() - start_time

            if response:
                status_code = response.status_code
            else:
                status_code = 0

            metrics.add_result(response_time, status_code, error)

            if error:
                print(f"{Colors.WARNING}ERROR{Colors.ENDC} ({response_time:.3f}s)")
            else:
                print(f"{Colors.OKGREEN}OK{Colors.ENDC} ({response_time:.3f}s)")

        except Exception as e:
            response_time = time.time() - start_time
            metrics.add_result(response_time, 0, str(e))
            print(f"{Colors.FAIL}EXCEPTION{Colors.ENDC} ({response_time:.3f}s): {e}")

        # Small delay between requests to avoid rate limiting
        if i < iterations - 1:
            time.sleep(0.5)

    return metrics


def make_request(method: str, url: str, **kwargs) -> tuple:
    """
    Make an HTTP request and return response and error.

    Returns:
        tuple: (response, error_message)
    """
    try:
        response = requests.request(method, url, **kwargs)

        # Check for HTTP errors
        if response.status_code >= 400:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json().get("detail", "")
                if error_detail:
                    error_msg += f": {error_detail}"
            except:
                pass
            return response, error_msg

        return response, None

    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {str(e)}"


def print_test_header(title: str):
    """Print a formatted test section header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print(f"{Colors.ENDC}")


def print_summary(results: List[tuple]):
    """
    Print overall test summary.

    Args:
        results: List of (endpoint_name, passed) tuples
    """
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed

    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 70)
    print("  OVERALL TEST SUMMARY")
    print("=" * 70)
    print(f"{Colors.ENDC}")

    print(f"\nTotal Tests:  {total}")
    print(f"{Colors.OKGREEN}Passed:       {passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}Failed:       {failed}{Colors.ENDC}")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")

    # Print individual results
    print(f"{Colors.BOLD}Individual Results:{Colors.ENDC}")
    for name, result in results:
        status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if result else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
        print(f"  {name:40s} {status}")

    print()
