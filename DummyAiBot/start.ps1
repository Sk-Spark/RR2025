# PowerShell start script for DummyAiBot

Write-Host "Starting DummyAiBot..." -ForegroundColor Green

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Start the bot
python main.py
