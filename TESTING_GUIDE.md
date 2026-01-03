# Testing Guide - Quick Start

## Quick Start

### 1. Start the API Server
```bash
uv run uvicorn main:app --reload
```

### 2. Run All Tests
```bash
./run_tests.sh
```

### 3. Run Specific Tests
```bash
# Health endpoints only
./run_tests.sh health

# Video endpoints only
./run_tests.sh video

# AI endpoints (requires OPENROUTER_API_KEY)
./run_tests.sh ai

# Storage endpoints (requires Redis)
./run_tests.sh storage

# Prompt endpoints
./run_tests.sh prompts
```

### 4. Skip Optional Tests
```bash
# Skip AI tests if no API key
./run_tests.sh --skip-ai

# Skip storage tests if no Redis
./run_tests.sh --skip-storage

# Skip multiple suites
./run_tests.sh --skip-ai --skip-storage
```

## What Gets Tested

### Performance Metrics
- ✓ Response times (min, max, mean, median, stddev)
- ✓ Throughput (requests/second)
- ✓ Success rates
- ✓ Error handling

### Endpoint Coverage
- ✓ **Health & Cache** (4 endpoints)
- ✓ **Video Data** (4 endpoints + error handling)
- ✓ **AI Features** (3 endpoints - optional)
- ✓ **Storage** (5 endpoints + workflow - optional)
- ✓ **Prompts** (5 endpoints + error handling)

### Total: ~30 tests

## Configuration

Set environment variables before testing:

```bash
# Optional: AI features
export OPENROUTER_API_KEY=your_key_here

# Optional: Storage features
export REDIS_URL=redis://localhost:6379/0

# Optional: Custom API URL
export API_BASE_URL=http://localhost:8000
```

## Reading Results

### ✓ GREEN = Passed
- Response time within threshold
- All requests successful
- Expected behavior confirmed

### ✗ RED = Failed
- Response time exceeded threshold
- Requests failed
- Unexpected errors

### Example Output
```
======================================================================
Performance Report: video_data
======================================================================

Response Times (seconds):
  Min:     0.245s
  Max:     0.312s
  Mean:    0.278s    ← Average response time
  Median:  0.281s
  StdDev:  0.025s

Throughput:
  Requests/sec: 3.60  ← How fast it processes

Reliability:
  Success Rate: 100.0%  ← All requests succeeded

Performance Threshold:
  Expected:  ≤ 2.000s
  Actual:    0.278s
  ✓ PASSED             ← Test passed!
======================================================================
```

## Troubleshooting

### "API is not responding"
```bash
# Check if server is running
curl http://localhost:8000/health

# Start the server
uv run uvicorn main:app --reload
```

### "AI features not available"
```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY=your_key_here

# Or skip AI tests
./run_tests.sh --skip-ai
```

### "Storage not enabled"
```bash
# Start Redis (Docker)
docker run -p 6379:6379 redis:alpine

# Or start Redis (Mac)
brew services start redis

# Or skip storage tests
./run_tests.sh --skip-storage
```

### Rate limiting errors
- Wait 1 minute between test runs
- Reduce iterations in `tests/config.py`:
  ```python
  PERFORMANCE_ITERATIONS = 3  # Default: 5
  ```

## Advanced Usage

### Run individual test files
```bash
cd tests

# Health tests only
python test_health.py

# Video tests only
python test_video.py
```

### Customize performance thresholds
Edit `tests/config.py`:
```python
PERFORMANCE_THRESHOLDS = {
    "video_data": 2.0,      # 2 seconds max
    "video_captions": 5.0,  # 5 seconds max
    # Adjust as needed
}
```

### Change test videos
Edit `tests/config.py`:
```python
TEST_VIDEOS = {
    "short": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    # ...
}
```

## Documentation

- **API Documentation**: See `API_DOCUMENTATION.md`
- **Test Details**: See `tests/README.md`
- **Main README**: See `README.md`

## Need Help?

1. Check `tests/README.md` for detailed documentation
2. Check `API_DOCUMENTATION.md` for API reference
3. Run `./run_tests.sh --help` for options
4. Review test output for specific errors

## CI/CD Integration

Add to your GitHub Actions workflow:
```yaml
- name: Run API Tests
  run: |
    uvicorn main:app &
    sleep 5
    ./run_tests.sh --skip-ai --skip-storage
```
