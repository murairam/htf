#!/bin/bash
# Test runner script for essenceAI

echo "🧪 Running essenceAI Test Suite"
echo "================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing test dependencies..."
    pip install -r requirements.txt
fi

# Run tests with different options based on argument
case "$1" in
    "quick")
        echo "⚡ Running quick tests (unit tests only)..."
        pytest tests/ -m unit -v
        ;;
    "coverage")
        echo "📊 Running tests with coverage report..."
        pytest tests/ --cov=src --cov-report=html --cov-report=term
        echo ""
        echo "📄 Coverage report generated in htmlcov/index.html"
        ;;
    "integration")
        echo "🔗 Running integration tests..."
        pytest tests/ -m integration -v
        ;;
    "all")
        echo "🎯 Running all tests..."
        pytest tests/ -v
        ;;
    *)
        echo "📝 Running standard test suite..."
        pytest tests/ -v --tb=short
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Some tests failed. Check output above."
    exit 1
fi
