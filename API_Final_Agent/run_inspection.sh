#!/bin/bash
# Script to run Phase 1 inspection

echo "=========================================="
echo "Phase 1: API Output Inspection"
echo "=========================================="
echo ""

# Check if ACE API is running
echo "Checking ACE_Framework API..."
if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ ACE_Framework API is running"
else
    echo "❌ ACE_Framework API is not running on http://localhost:8001"
    echo "   Please start it first: cd ACE_Framwork && python -m uvicorn api:app --port 8001"
    exit 1
fi

# Check if EssenceAI wrapper is running
echo "Checking EssenceAI API wrapper..."
if curl -s http://localhost:8002/ > /dev/null 2>&1; then
    echo "✅ EssenceAI API wrapper is running"
else
    echo "⚠️  EssenceAI API wrapper is not running on http://localhost:8002"
    echo "   Starting it in background..."
    python essence_wrapper.py &
    ESSENCE_PID=$!
    echo "   Started with PID: $ESSENCE_PID"
    sleep 3
    if curl -s http://localhost:8002/ > /dev/null 2>&1; then
        echo "✅ EssenceAI API wrapper is now running"
    else
        echo "❌ Failed to start EssenceAI API wrapper"
        kill $ESSENCE_PID 2>/dev/null
        exit 1
    fi
fi

echo ""
echo "Running inspection tool..."
echo ""

python tools/inspect_outputs.py

echo ""
echo "=========================================="
echo "Inspection complete! Check artifacts/ directory"
echo "=========================================="

