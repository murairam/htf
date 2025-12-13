#!/bin/bash

# Plant-Based Packaging Intelligence - Production Server Launcher
# This script builds the frontend and runs Django with Daphne (ASGI server)

echo "🌱 Starting Plant-Based Packaging Intelligence in Production Mode..."
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

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run with Daphne
echo ""
echo "🚀 Starting Daphne ASGI server..."
echo ""
echo "✅ Server running at http://localhost:8000"
echo "🔌 WebSocket endpoint: ws://localhost:8000/ws/analysis/<id>/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m daphne -b 0.0.0.0 -p 8000 config.asgi:application
