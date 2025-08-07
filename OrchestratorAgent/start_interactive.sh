#!/bin/bash
#
# Quick start script for the Orchestrator Agent in Interactive Mode
#

# Navigate to the orchestrator directory
cd "$(dirname "$0")"

echo "🤖 Starting Orchestrator Agent in Interactive Mode..."
echo "🎯 Ready to manage AI bot scenarios and task assignment"
echo "==============================================="

# Use the virtual environment Python
PYTHON_CMD="/home/spark/.venv/bin/python"

if [ -f "$PYTHON_CMD" ]; then
    echo "✅ Using virtual environment Python"
else
    echo "❌ Virtual environment not found, using system Python"
    PYTHON_CMD="python"
fi

# Start the orchestrator in interactive mode
$PYTHON_CMD main.py

echo "👋 Orchestrator stopped. Goodbye!"
