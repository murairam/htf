#!/bin/bash

# Script to run the FastAPI LLM Analysis Service
# This service must be running before starting Django

echo "🚀 Starting FastAPI LLM Analysis Service..."
echo "📍 Service will run on http://localhost:8001"
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
    echo "✅ .env file loaded"
    echo ""
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable is not set!"
    echo ""
    echo "   The FastAPI service requires an OpenAI API key to function."
    echo ""
    echo "   Option 1: Create a .env file in the project root:"
    echo "   ----------------------------------------"
    echo "   echo 'OPENAI_API_KEY=sk-your-key-here' > .env"
    echo "   ----------------------------------------"
    echo ""
    echo "   Option 2: Export it in your terminal:"
    echo "   ----------------------------------------"
    echo "   export OPENAI_API_KEY='sk-your-key-here'"
    echo "   ----------------------------------------"
    echo ""
    echo "   To get your API key, visit: https://platform.openai.com/api-keys"
    echo ""
    exit 1
fi

echo "✅ OPENAI_API_KEY is set"
echo ""

# Navigate to ACE_Framework directory
cd ACE_Framwork

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Run FastAPI service
echo "✅ Starting FastAPI service on port 8001..."
echo ""
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
