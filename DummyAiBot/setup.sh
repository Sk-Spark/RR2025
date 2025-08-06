#!/bin/bash
# Setup script for DummyAiBot - Testing Environment

echo "Setting up DummyAiBot testing environment..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup completed!"
echo ""
echo "To activate the environment in the future, run:"
echo "source venv/bin/activate"
echo ""
echo "To start the bot, run:"
echo "python main.py"
