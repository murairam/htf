#!/bin/bash

# Plant-Based Packaging Intelligence - Production Server Launcher
# This script builds the frontend and runs Django with Daphne (ASGI server)

echo "🌱 Starting Plant-Based Packaging Intelligence in Production Mode..."
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
    echo ""
fi

# Check if FastAPI service is running
echo "🔍 Checking FastAPI service..."
if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ FastAPI service is running on port 8001"
else
    echo "❌ ERROR: FastAPI service is not running!"
    echo ""
    echo "   The FastAPI LLM service must be running before starting Django."
    echo "   Please start it in a separate terminal with:"
    echo ""
    echo "   ./run_fastapi.sh"
    echo ""
    echo "   Or manually:"
    echo "   cd ACE_Framwork && uvicorn api:app --host 0.0.0.0 --port 8001"
    echo ""
    exit 1
fi

echo ""

# Build frontend
echo "📦 Building React frontend..."
cd frontend
npm run build:deploy
cd ..

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend built successfully"
echo ""

# Copy frontend build to backend static
echo "📋 Copying frontend build to backend/static/react/..."
mkdir -p backend/static/react
cp -r frontend/dist/* backend/static/react/

# Update Django template with correct asset filenames
echo "🔧 Updating Django template with asset filenames..."
python update_template.py

if [ $? -ne 0 ]; then
    echo "⚠️  WARNING: Template update failed, but continuing..."
fi

echo ""

# Check if Redis is running
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✓ Redis is running"
    else
        echo "⚠️  WARNING: Redis is not running!"
        echo "   WebSocket connections will fail in production mode."
        echo "   Start Redis with: redis-server"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  WARNING: Redis is not installed!"
    echo "   Install Redis for production WebSocket support."
    echo ""
fi

# Set PYTHONPATH to current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run with Daphne
echo ""
echo "🚀 Starting Daphne ASGI server..."
echo ""
echo "✅ Django server running at http://localhost:8000"
echo "✅ FastAPI service running at http://localhost:8001"
echo "🔌 WebSocket endpoint: ws://localhost:8000/ws/analysis/<id>/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m daphne -b 0.0.0.0 -p 8000 config.asgi:application
