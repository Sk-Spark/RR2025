#!/bin/bash
# Activate virtual environment and run robot controller

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if packages are installed
echo "Checking Python packages..."
if ! python -c "import adafruit_pca9685" 2>/dev/null; then
    echo "Installing required packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Run the main program with provided arguments
echo "Starting robot controller..."
python main.py "$@"

# Deactivate virtual environment
deactivate
