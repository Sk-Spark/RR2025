#!/bin/bash

# AI Bot Starter Script
# This script activates the virtual environment and starts the AI Bot controller

set -e

cd /home/spark/RR2025/AiBot

echo "🤖 Starting AI Bot Controller..."
echo "================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./setup.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated"
echo "🚀 Starting AI Bot..."
echo ""
echo "Web interface will be available at:"
echo "  http://$(hostname -I | cut -d' ' -f1):5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the AI Bot
python main.py
