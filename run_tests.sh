#!/bin/bash
#
# YouTube Summaries API - Test Runner Script
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh health       # Run only health tests
#   ./run_tests.sh --skip-ai    # Skip AI tests
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_BASE_URL:-http://localhost:8000}"
TEST_DIR="tests"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}YouTube Summaries API - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if API is running
echo -e "${YELLOW}Checking if API is running...${NC}"
if curl -s -f "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is running at ${API_URL}${NC}"
else
    echo -e "${RED}✗ API is not running at ${API_URL}${NC}"
    echo ""
    echo "Please start the API server first:"
    echo "  uv run uvicorn main:app --reload"
    echo ""
    exit 1
fi

echo ""

# Check Python dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${RED}✗ 'requests' library not found${NC}"
    echo ""
    echo "Installing required dependencies..."
    pip install requests
    echo ""
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Change to test directory
cd "$TEST_DIR"

# Check if specific test file or arguments provided
if [ $# -eq 0 ]; then
    echo -e "${BLUE}Running all tests...${NC}"
    echo ""
    python3 run_all_tests.py
else
    # Check if it's a test suite name
    case "$1" in
        health|video|ai|storage|prompts)
            echo -e "${BLUE}Running $1 tests only...${NC}"
            echo ""
            python3 run_all_tests.py --only "$1"
            ;;
        *)
            # Pass all arguments to test runner
            echo -e "${BLUE}Running tests with custom options...${NC}"
            echo ""
            python3 run_all_tests.py "$@"
            ;;
    esac
fi

# Return to original directory
cd ..

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test run completed${NC}"
echo -e "${BLUE}========================================${NC}"
