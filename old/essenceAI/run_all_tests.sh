#!/bin/bash
# Run all agent system tests

echo "================================================================================"
echo "  essenceAI Agent System - Complete Test Suite"
echo "================================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Running: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Change to essenceAI directory
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo ""

# 1. Setup Verification
run_test "Setup Verification" "python3 test_agent_setup.py"

# 2. Marketing Agent Tests
run_test "Marketing Agent - All Segments" "python3 test_marketing.py"
run_test "Marketing Agent - Segment Comparison" "python3 test_segment_comparison.py"

# 3. Unit Tests (without API keys)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Running Unit Tests (tests that don't require API keys)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run specific test classes that don't need API keys
pytest tests/test_agents.py::TestBaseAgent -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}: Base Agent Tests"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAILED${NC}: Base Agent Tests"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

pytest tests/test_agents.py::TestMarketingAgent -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}: Marketing Agent Tests"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAILED${NC}: Marketing Agent Tests"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

pytest tests/test_agents.py::TestAgentConfig -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}: Agent Config Tests"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAILED${NC}: Agent Config Tests"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

pytest tests/test_agents.py::TestIntegration -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}: Integration Tests"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAILED${NC}: Integration Tests"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Summary
echo ""
echo "================================================================================"
echo "  Test Summary"
echo "================================================================================"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"
echo -e "${RED}Failed:       $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "Your agent system is working perfectly!"
    echo ""
    echo "Next steps:"
    echo "  1. Add API keys to .env file for full functionality"
    echo "  2. Run: python3 examples/agent_usage_examples.py"
    echo "  3. Check AGENTS_README.md for documentation"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo ""
    echo "This is expected if you haven't set up API keys yet."
    echo "Tests that require API keys will fail without them."
    echo ""
    echo "To fix:"
    echo "  1. Create .env file with: OPENAI_API_KEY=sk-your-key-here"
    echo "  2. Run tests again"
    echo ""
    exit 1
fi
