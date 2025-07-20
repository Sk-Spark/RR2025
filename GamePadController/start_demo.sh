#!/bin/bash
# Start script for Demo Mode

echo "🎮 Starting Xbox Controller Demo Mode..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the demo
echo "🚀 Launching demo mode..."
python3 xbox_demo.py
