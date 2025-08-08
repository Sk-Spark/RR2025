#!/bin/bash
"""
Startup script for Semantic Kernel LED Control
This script activates the virtual environment and runs the main application.
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/home/spark/RR2025/SemanticKernal"

echo -e "${BLUE}🚀 Starting Semantic Kernel LED Control${NC}"
echo -e "${BLUE}======================================${NC}"

# Change to project directory
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Failed to change to project directory: $PROJECT_DIR${NC}"
    exit 1
}

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup first.${NC}"
    echo -e "${YELLOW}Run: python3 -m venv env && source /home/spark/.venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source /home/spark/.venv/bin/activate || {
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
}

# Check if Ollama is running
echo -e "${YELLOW}🔍 Checking if Ollama is running...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}❌ Ollama is not running or not accessible${NC}"
    echo -e "${YELLOW}Please start Ollama with: ollama serve${NC}"
    exit 1
fi

# Check if required model is available
echo -e "${YELLOW}🔍 Checking if llama3.2:1b model is available...${NC}"
if ! ollama list | grep -q "llama3.2:1b"; then
    echo -e "${YELLOW}⚠️  llama3.2:1b model not found. Attempting to pull...${NC}"
    ollama pull llama3.2:1b || {
        echo -e "${RED}❌ Failed to pull llama3.2:1b model${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ All checks passed!${NC}"
echo -e "${BLUE}🎯 Starting LED Control Agent...${NC}"
echo ""

# Run the main application
python main.py
