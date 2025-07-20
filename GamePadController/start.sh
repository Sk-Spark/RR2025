#!/bin/bash
# Start script for Xbox Controller Demo Mode

echo "🎮 Starting Xbox Controller Demo..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first"
    exit 1
fi

# Check if controller is connected
if [ ! -e "/dev/input/js0" ]; then
    echo "❌ No controller detected at /dev/input/js0"
    echo "Available input devices:"
    ls -la /dev/input/js* 2>/dev/null || echo "No joystick devices found"
    echo ""
    echo "Please make sure:"
    echo "1. Your Xbox controller is connected via USB"
    echo "2. The controller is recognized by the system"
    echo "3. You may need to run: sudo chmod 666 /dev/input/js0"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the demo controller reader
echo "🚀 Launching controller demo..."
python3 xbox_demo.py
