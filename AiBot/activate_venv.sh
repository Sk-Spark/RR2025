#!/bin/bash
# Activation script for AiBot virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    echo "Activating AiBot virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "Virtual environment activated. Use 'deactivate' to exit."
else
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi
