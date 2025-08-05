#!/bin/bash
#
# Startup script for Interactive Test Orchestrator
# Uses absolute paths for virtual environment activation
#

# Define absolute paths
SCRIPT_DIR="/home/spark/RR2025/SemanticKernal"
VENV_PATH="/home/spark/RR2025/SemanticKernal/env"
PYTHON_SCRIPT="test_orchestrator.py"

# Change to script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at: $VENV_PATH"
    echo "Please create the virtual environment first"
    exit 1
fi

# Activate virtual environment using absolute path
echo "🔄 Activating virtual environment at: $VENV_PATH"
source "$VENV_PATH/bin/activate"

# Verify activation
if [ "$VIRTUAL_ENV" != "$VENV_PATH" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated successfully"
echo "🐍 Python version: $(python --version)"
echo "📍 Virtual env: $VIRTUAL_ENV"

# Check if websockets module is available
echo "🔍 Checking websockets module..."
python -c "import websockets; print('✅ websockets module available')" || {
    echo "❌ websockets module not found. Installing..."
    pip install websockets
}

# Run the orchestrator
echo "🚀 Starting Interactive Test Orchestrator..."
echo "📂 Working directory: $(pwd)"
echo "🎯 Script: $PYTHON_SCRIPT"
echo ""

# Execute the Python script
python "$PYTHON_SCRIPT"
