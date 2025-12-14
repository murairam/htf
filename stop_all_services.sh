#!/bin/bash

# Script to stop all services started by run_all_services.sh

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Attempting to stop all services...${NC}"

# List of PID files
PID_FILES=(
    "logs/api_final_agent.pid"
)

for pid_file in "${PID_FILES[@]}"; do
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null; then
            echo -e "${YELLOW}Killing process $PID from $pid_file...${NC}"
            kill $PID
            sleep 1 # Give it a moment to terminate
            if ps -p $PID > /dev/null; then
                echo -e "${RED}Process $PID still running, forcing kill...${NC}"
                kill -9 $PID
            fi
        else
            echo -e "${YELLOW}Process $PID from $pid_file not found, likely already stopped.${NC}"
        fi
        rm -f "$pid_file" # Clean up PID file
    else
        echo -e "${YELLOW}PID file $pid_file not found. Service might not be running or was stopped manually.${NC}"
    fi
done

# For Django, we assume it's running in the foreground of the terminal that called run_all_services.sh
# So, it should be stopped by Ctrl+C in that terminal.
# If this script is called independently, it won't stop Django.

echo -e "${GREEN}✅ Attempted to stop all background services.${NC}"
echo -e "${YELLOW}If Django was running in the foreground, you need to stop its terminal manually (Ctrl+C).${NC}"
