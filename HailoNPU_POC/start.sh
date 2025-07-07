#!/bin/bash

# Simple start script for RPi AI Hat+ Object Detection System
# This script activates the virtual environment and starts the application

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting RPi AI Hat+ Object Detection System...${NC}"

# Change to script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py not found in current directory.${NC}"
    exit 1
fi

# Check dependencies
echo -e "${GREEN}🔍 Checking dependencies...${NC}"
python -c "import flask, cv2, numpy, picamera2" 2>/dev/null || {
    echo -e "${RED}❌ Missing dependencies. Please run: pip install -r requirements.txt${NC}"
    exit 1
}

# Check camera
echo -e "${GREEN}📷 Checking camera...${NC}"
if ! libcamera-hello --list-cameras &>/dev/null; then
    echo -e "${YELLOW}⚠️  Camera not detected or libcamera not available${NC}"
    echo -e "${YELLOW}   The system will still start but may not work properly${NC}"
fi

# Show system info
echo -e "${GREEN}📋 System Information:${NC}"
echo -e "  🖥️  Hostname: $(hostname)"
echo -e "  🌐 IP Address: $(hostname -I | awk '{print $1}')"
echo -e "  📁 Working Directory: $(pwd)"
echo -e "  🐍 Python Version: $(python --version)"
echo -e "  📡 Web Interface: http://$(hostname -I | awk '{print $1}'):5000"

# Start the application
echo -e "${GREEN}🎬 Starting application...${NC}"
echo -e "${YELLOW}   Press Ctrl+C to stop${NC}"
echo -e "${YELLOW}   Access the web interface at: http://localhost:5000${NC}"
echo

# Run the main application
python main.py
