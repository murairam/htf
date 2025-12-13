#!/bin/bash

# Plant-Based Packaging Intelligence - Development Server Launcher
# This script starts both Django backend and Vite frontend dev servers

echo "🌱 Starting Plant-Based Packaging Intelligence Development Servers..."
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
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "🔌 WebSocket: ws://localhost:8000/ws/analysis/<id>/"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $DJANGO_PID $VITE_PID
