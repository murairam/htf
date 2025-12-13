#!/bin/bash

# Plant-Based Packaging Intelligence - Development Server Launcher
# This script starts FastAPI, Django backend, and Vite frontend dev servers

echo "🌱 Starting Plant-Based Packaging Intelligence Development Servers..."
echo ""

# Check if FastAPI service is running
echo "🔍 Checking FastAPI service..."
if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ FastAPI service is already running on port 8001"
else
    echo "⚠️  FastAPI service is not running!"
    echo "   Please start it in a separate terminal with:"
    echo ""
    echo "   ./run_fastapi.sh"
    echo ""
    echo "   Or continue without it (analysis will fail)"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Check if Redis is running (optional for dev)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✓ Redis is running (WebSocket backend)"
    else
        echo "⚠ Redis not running - using in-memory channel layer"
    fi
else
    echo "⚠ Redis not installed - using in-memory channel layer"
fi

echo ""
echo "Starting servers..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $DJANGO_PID $VITE_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Start Django backend
echo "🐍 Starting Django backend on http://localhost:8000..."
python manage.py runserver &
DJANGO_PID=$!

# Wait a moment for Django to start
sleep 2

# Start Vite frontend
echo "⚛️  Starting Vite dev server on http://localhost:5173..."
cd frontend
npm run dev &
VITE_PID=$!
cd ..

echo ""
echo "✅ Development servers are running!"
echo ""
echo "📱 Frontend:  http://localhost:5173"
echo "🔧 Django:    http://localhost:8000"
echo "🤖 FastAPI:   http://localhost:8001"
echo "🔌 WebSocket: ws://localhost:8000/ws/analysis/<id>/"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $DJANGO_PID $VITE_PID
