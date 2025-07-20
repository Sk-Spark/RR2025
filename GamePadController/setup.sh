#!/bin/bash
# Setup script for Xbox Controller project

echo "🎮 Setting up Xbox Controller Project for Raspberry Pi 5"
echo "======================================================"

# Check if we're on RPi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Available scripts:"
echo "  ./start_demo.sh     - Test gamepad inputs (demo mode)"
echo "  ./start.sh          - Run gamepad demo"
echo ""
echo "To check if your controller is detected:"
echo "   ls -la /dev/input/js*"
