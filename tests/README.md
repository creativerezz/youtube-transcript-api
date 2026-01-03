# API Performance Tests

Comprehensive performance testing suite for the YouTube Summaries API with detailed metrics and reporting.

## Overview

This test suite provides:
- **Performance metrics**: Response times, throughput, success rates
- **Load testing**: Multiple iterations to identify performance issues
- **Error handling**: Validation of error responses
- **Workflow testing**: End-to-end scenario validation
- **Detailed reporting**: Color-coded terminal output with statistics

## Test Structure

```
tests/
├── config.py              # Test configuration and settings
├── utils.py               # Performance testing utilities
├── test_health.py         # Health & cache endpoint tests
├── test_video.py          # Video data & transcript tests
├── test_ai.py             # AI-powered feature tests
├── test_storage.py        # Transcript storage tests
├── test_prompts.py        # Prompt management tests
├── run_all_tests.py       # Master test runner
└── README.md              # This file
```

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install requests
   ```

2. **Start the API server:**
   ```bash
   # From project root
   uv run uvicorn main:app --reload
   ```

3. **Configure environment (optional):**
   ```bash
   # For AI features
   export OPENROUTER_API_KEY=your_key_here

   # For storage features
   export REDIS_URL=redis://localhost:6379/0

   # Custom API URL
   export API_BASE_URL=http://localhost:8000
   ```

## Running Tests

### Run All Tests

```bash
cd tests
python run_all_tests.py
```

### Run Specific Test Suite

```bash
# Health endpoints only
python run_all_tests.py --only health

# Video endpoints only
python run_all_tests.py --only video

# AI endpoints only
python run_all_tests.py --only ai

# Storage endpoints only
python run_all_tests.py --only storage

# Prompts endpoints only
python run_all_tests.py --only prompts
```

### Skip Specific Suites

```bash
# Skip AI tests (if no API key)
python run_all_tests.py --skip-ai

# Skip storage tests (if no Redis)
python run_all_tests.py --skip-storage

# Skip multiple suites
python run_all_tests.py --skip-ai --skip-storage
```

### Run Individual Test Files

```bash
# Health tests
python test_health.py

# Video tests
python test_video.py

# AI tests
python test_ai.py

# Storage tests
python test_storage.py

# Prompts tests
python test_prompts.py
```

## Configuration

Edit `config.py` to customize:

### API Base URL
```python
BASE_URL = "http://localhost:8000"
```

### Test Videos
```python
TEST_VIDEOS = {
    "short": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "medium": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "long": "https://www.youtube.com/watch?v=9bZkp7q19f0",
}
```

### Performance Thresholds
```python
PERFORMANCE_THRESHOLDS = {
    "health": 0.1,           # 100ms
    "video_data": 2.0,       # 2 seconds
    "video_captions": 5.0,   # 5 seconds
    "video_notes": 30.0,     # 30 seconds
    # ...
}
```

### Iterations
```python
PERFORMANCE_ITERATIONS = 5  # Number of test iterations
```

## Test Output

### Performance Metrics

Each test displays:
- **Response Times**: Min, Max, Mean, Median, StdDev
- **Throughput**: Requests per second
- **Reliability**: Success/failure counts and rates
- **Status Codes**: HTTP response code distribution
- **Errors**: Error messages (if any)
- **Pass/Fail**: Against performance thresholds

### Example Output

```
======================================================================
Performance Report: video_data
======================================================================

Response Times (seconds):
  Min:     0.245s
  Max:     0.312s
  Mean:    0.278s
  Median:  0.281s
  StdDev:  0.025s

Throughput:
  Requests/sec: 3.60

Reliability:
  Total Requests:  5
  Successful:      5
  Failed:          0
  Success Rate:    100.0%

Status Codes:
  200: 5

Performance Threshold:
  Expected:  ≤ 2.000s
  Actual:    0.278s
  ✓ PASSED
======================================================================
```

### Final Report

```
======================================================================
  FINAL TEST REPORT
======================================================================

Summary:
  Total Time:   45.23s
  Total Tests:  22
  Passed:       20
  Failed:       2
  Success Rate: 90.9%

Detailed Results:
  Health & Cache:
    GET /                         ✓ PASS
    GET /health                   ✓ PASS
    GET /cache/stats              ✓ PASS
    POST /cache/clear             ✓ PASS

  Video Data:
    POST /video-data              ✓ PASS
    POST /video-captions          ✓ PASS
    ...

Overall Status:
  ✗ SOME TESTS FAILED
```

## Test Coverage

### Health & Cache (4 tests)
- ✓ GET / (API info)
- ✓ GET /health (Health check)
- ✓ GET /cache/stats (Cache statistics)
- ✓ POST /cache/clear (Clear cache)

### Video Data (6 tests)
- ✓ POST /video-data (Video metadata)
- ✓ POST /video-captions (Plain text transcript)
- ✓ POST /video-captions (Language fallback)
- ✓ POST /video-timestamps (Timestamped transcript)
- ✓ POST /video-transcript-languages (Available languages)
- ✓ Error handling (Invalid URL)
- ✓ Cache effectiveness test

### AI Features (5 tests)
- ✓ POST /video-notes (Structured format)
- ✓ POST /video-notes (Summary format)
- ✓ POST /video-notes (Detailed format)
- ✓ POST /video-translate (Translation)
- ✓ POST /openrouter-proxy (Direct API access)

### Storage (6 tests)
- ✓ POST /transcripts/save (Save transcript)
- ✓ POST /transcripts/get (Retrieve transcript)
- ✓ GET /transcripts/list (List all)
- ✓ GET /transcripts/stats (Statistics)
- ✓ POST /transcripts/delete (Delete transcript)
- ✓ Storage workflow (Complete flow)

### Prompts (8 tests)
- ✓ GET /prompts/ (List all prompts)
- ✓ GET /prompts/categories (List categories)
- ✓ GET /prompts/category/{category} (By category)
- ✓ GET /prompts/{name} (Get specific prompt)
- ✓ POST /prompts/refresh (Refresh cache)
- ✓ 404 handling (Prompt not found)
- ✓ 404 handling (Category not found)
- ✓ Content availability check

**Total: ~30 tests**

## Performance Benchmarks

### Expected Response Times

| Endpoint | Target | Typical |
|----------|--------|---------|
| Health | < 100ms | 50ms |
| Cache Stats | < 200ms | 100ms |
| Video Data | < 2s | 500ms |
| Captions | < 5s | 2s |
| Timestamps | < 5s | 2s |
| Languages | < 3s | 1s |
| AI Notes | < 30s | 15s |
| Translation | < 45s | 25s |
| Storage Save | < 3s | 1s |
| Storage Get | < 500ms | 200ms |

## Troubleshooting

### API Not Responding
```bash
# Check if server is running
curl http://localhost:8000/health

# Start the server
uv run uvicorn main:app --reload
```

### AI Tests Failing
```bash
# Check if API key is configured
curl http://localhost:8000/ | jq '.ai_features_available'

# Set API key
export OPENROUTER_API_KEY=your_key_here
```

### Storage Tests Failing
```bash
# Check Redis connection
redis-cli ping

# Check health endpoint
curl http://localhost:8000/health | jq '.cache_status'
```

### Rate Limiting Errors
- Tests include delays between requests
- Reduce `PERFORMANCE_ITERATIONS` in `config.py`
- Wait 1 minute between test runs

### Timeout Errors
- Increase `REQUEST_TIMEOUT` in `config.py`
- Check network connection
- Try shorter test videos

## CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install requests

      - name: Start API
        run: |
          uvicorn main:app &
          sleep 5
        env:
          REDIS_URL: redis://localhost:6379/0

      - name: Run tests
        run: |
          cd tests
          python run_all_tests.py --skip-ai
```

## Best Practices

1. **Always run health check first**
   - Ensures API is responsive
   - Validates configuration

2. **Use appropriate iterations**
   - More iterations = better statistics
   - But slower tests and potential rate limiting

3. **Monitor performance trends**
   - Save test results over time
   - Identify performance degradation

4. **Skip unavailable features**
   - Use `--skip-ai` if no API key
   - Use `--skip-storage` if no Redis

5. **Check thresholds regularly**
   - Update `PERFORMANCE_THRESHOLDS` as API evolves
   - Account for network latency

## Contributing

When adding new endpoints:

1. Add endpoint to appropriate test file
2. Update `PERFORMANCE_THRESHOLDS` in `config.py`
3. Add test to `run_all_tests.py`
4. Update this README
5. Run full test suite before committing

## License

Same as main project.
