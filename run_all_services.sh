#!/bin/bash

# Script to run unified services
# - API_Final_Agent (unified LLM service) on port 8001
# - Django (main website) on port 8000

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load .env file if it exists
if [ -f .env ]; then
    echo -e "${GREEN}📄 Loading environment variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
    echo ""
fi


# Create logs directory
mkdir -p logs

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}⏳ Waiting for $name to be ready at $url...${NC}"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    echo -e "${RED}❌ $name failed to start after ${max_attempts} seconds${NC}"
    return 1
}

# Default ports
API_FINAL_AGENT_PORT=${API_FINAL_AGENT_PORT:-8001}
DJANGO_PORT=${DJANGO_PORT:-8000}

# Check ports
echo -e "${YELLOW}🔍 Checking ports...${NC}"
if check_port $API_FINAL_AGENT_PORT; then
    echo -e "${RED}❌ Port $API_FINAL_AGENT_PORT is already in use. Please free it or change API_FINAL_AGENT_PORT.${NC}"
    exit 1
fi
if check_port $DJANGO_PORT; then
    echo -e "${RED}❌ Port $DJANGO_PORT is already in use. Please free it or change DJANGO_PORT.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All required ports are free${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
    kill $API_FINAL_PID 2>/dev/null || true
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Start API_Final_Agent in background
echo -e "${GREEN}🚀 Starting API_Final_Agent on port ${API_FINAL_AGENT_PORT}...${NC}"
cd API_Final_Agent

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ python3 not found. Please install Python 3.${NC}"
    exit 1
fi

# Create venv if it doesn't exist or if pip is missing
if [ ! -d "venv" ] || [ ! -f "venv/bin/pip" ]; then
    if [ -d "venv" ]; then
        echo -e "${YELLOW}📦 Recreating virtual environment (pip missing)...${NC}"
        rm -rf venv
    else
        echo -e "${YELLOW}📦 Creating virtual environment for API_Final_Agent...${NC}"
    fi
    python3 -m venv venv
    
    # Ensure pip is available
    if [ ! -f "venv/bin/pip" ]; then
        echo -e "${YELLOW}📦 Installing pip in virtual environment...${NC}"
        ./venv/bin/python -m ensurepip --upgrade --default-pip 2>/dev/null || \
        ./venv/bin/python -m pip install --upgrade pip 2>/dev/null || {
            echo -e "${RED}❌ Failed to install pip in virtual environment${NC}"
            exit 1
        }
    fi
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
./venv/bin/pip install -q -r requirements.txt > /dev/null 2>&1 || {
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
}

# Start the service with environment variables from .env
# The environment variables are already loaded at the top of the script
echo -e "${YELLOW}🔑 Environment variables loaded (OPENAI_API_KEY, BLACKBOX_API_KEY, etc.)${NC}"
./venv/bin/python main.py > ../logs/api_final_agent.log 2>&1 &
API_FINAL_PID=$!
cd ..
echo "   PID: $API_FINAL_PID"

if ! wait_for_service "http://localhost:${API_FINAL_AGENT_PORT}/" "API_Final_Agent"; then
    echo -e "${RED}❌ API_Final_Agent failed to start. Check logs/api_final_agent.log${NC}"
    exit 1
fi
echo ""

# Build frontend
echo -e "${GREEN}📦 Building React frontend...${NC}"
cd frontend
if ! npm run build:deploy > ../logs/frontend_build.log 2>&1; then
    echo -e "${RED}❌ Frontend build failed!${NC}"
    echo "   Check logs/frontend_build.log for details"
    cd ..
    exit 1
fi
cd ..
echo -e "${GREEN}✅ Frontend built successfully${NC}"
echo ""

# Update Django template
echo -e "${GREEN}🔧 Updating Django template...${NC}"
if ! python update_template.py; then
    echo -e "${YELLOW}⚠️  WARNING: Template update failed, but continuing...${NC}"
fi
echo -e "${GREEN}✅ Template updated${NC}"
echo ""

# Collect static files
echo -e "${GREEN}📁 Collecting static files...${NC}"
if ! python manage.py collectstatic --noinput > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: Static files collection may have failed, but continuing...${NC}"
fi
echo -e "${GREEN}✅ Static files collected${NC}"
echo ""

# Check if Redis is running (for WebSockets in production)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: Redis is not running!${NC}"
        echo "   WebSocket connections will fail in production mode."
        echo "   Start Redis with: redis-server"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: Redis is not installed!${NC}"
    echo "   Install Redis for production WebSocket support."
    echo ""
fi
echo ""

# Run migrations
echo -e "${GREEN}🔄 Running migrations...${NC}"
if ! python manage.py migrate > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: Migrations may have failed, but continuing...${NC}"
fi
echo -e "${GREEN}✅ Migrations complete${NC}"
echo ""

# Save PID to file for later cleanup
echo "$API_FINAL_PID" > logs/api_final_agent.pid

# Run Django (foreground, so script stays alive)
echo -e "${GREEN}🚀 Starting Django server...${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All services are running!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📍 Service URLs:${NC}"
echo "   Django:        http://localhost:${DJANGO_PORT}"
echo "   API_Final:     http://localhost:${API_FINAL_AGENT_PORT}"
echo ""
echo -e "${YELLOW}📋 Process IDs:${NC}"
echo "   API_Final:    $API_FINAL_PID"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo "   API_Final:     logs/api_final_agent.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Run Django (foreground, so script stays alive)
python3 -m daphne -b 0.0.0.0 -p ${DJANGO_PORT} config.asgi:application
