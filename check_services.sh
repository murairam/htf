#!/bin/bash

# Script to check the status of all services

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 Checking status of all services...${NC}"
echo ""

# Default ports
API_FINAL_AGENT_PORT=${API_FINAL_AGENT_PORT:-8001}
DJANGO_PORT=${DJANGO_PORT:-8000}

check_service() {
    local name=$1
    local url=$2
    local port=$3
    echo -n "  ${YELLOW}$name (Port $port): ${NC}"
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not Running${NC}"
    fi
}

check_service "API_Final_Agent" "http://localhost:${API_FINAL_AGENT_PORT}/" "${API_FINAL_AGENT_PORT}"
check_service "Django" "http://localhost:${DJANGO_PORT}/" "${DJANGO_PORT}"

echo ""
echo -e "${GREEN}✅ Service check complete.${NC}"
