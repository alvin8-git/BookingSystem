#!/bin/bash

# Booking System - Production Deployment Script
# This script starts the application with Gunicorn in production mode

set -e

# Configuration
APP_NAME="booking_system"
APP_DIR="/data/alvin/BookingSystem"
LOG_DIR="$APP_DIR/logs"
PID_FILE="/tmp/$APP_NAME.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VERSION=$(cat VERSION 2>/dev/null || echo "1.1.0")
echo -e "${GREEN}Starting Booking System v${VERSION} in Production Mode${NC}"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to check if process is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to stop the application
stop_app() {
    if is_running; then
        echo -e "${YELLOW}Stopping existing application...${NC}"
        PID=$(cat "$PID_FILE")
        kill -TERM "$PID"
        
        # Wait for process to stop
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                echo -e "${GREEN}Application stopped successfully${NC}"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${RED}Force killing process...${NC}"
            kill -KILL "$PID"
        fi
        
        rm -f "$PID_FILE"
    else
        echo -e "${YELLOW}Application is not running${NC}"
    fi
}

# Function to start the application
start_app() {
    if is_running; then
        echo -e "${YELLOW}Application is already running (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Starting application with Gunicorn...${NC}"
    
    # Change to application directory
    cd "$APP_DIR"
    
    # Initialize database first
    python3 -c "from app import init_db; init_db()"
    
    # Start Gunicorn
    gunicorn \
        --config gunicorn.conf.py \
        --daemon \
        --pid "$PID_FILE" \
        wsgi:app
    
    # Check if started successfully
    sleep 2
    if is_running; then
        echo -e "${GREEN}Application started successfully (PID: $(cat $PID_FILE))${NC}"
        echo -e "${GREEN}Application is accessible at: http://192.168.1.168:8001${NC}"
    else
        echo -e "${RED}Failed to start application${NC}"
        exit 1
    fi
}

# Function to restart the application
restart_app() {
    echo -e "${YELLOW}Restarting application...${NC}"
    stop_app
    sleep 2
    start_app
}

# Function to show status
show_status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}Application is running (PID: $PID)${NC}"
        echo -e "${GREEN}Accessible at: http://192.168.1.168:8001${NC}"
    else
        echo -e "${RED}Application is not running${NC}"
    fi
}

# Function to show logs
show_logs() {
    echo -e "${GREEN}Showing recent logs...${NC}"
    tail -n 50 "$LOG_DIR/error.log" 2>/dev/null || echo "No error logs found"
    echo -e "${GREEN}---${NC}"
    tail -n 50 "$LOG_DIR/access.log" 2>/dev/null || echo "No access logs found"
}

# Main script logic
case "${1:-start}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo "  start   - Start the application"
        echo "  stop    - Stop the application"
        echo "  restart - Restart the application"
        echo "  status  - Show application status"
        echo "  logs    - Show recent logs"
        exit 1
        ;;
esac