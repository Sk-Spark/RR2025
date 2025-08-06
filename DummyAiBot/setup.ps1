# PowerShell setup script for DummyAiBot - Testing Environment

Write-Host "Setting up DummyAiBot testing environment..." -ForegroundColor Green

# Create logs directory if it doesn't exist
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
    Write-Host "Created logs directory" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
pip install --upgrade pip

# Install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the environment in the future, run:" -ForegroundColor Cyan
Write-Host "venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To start the bot, run:" -ForegroundColor Cyan
Write-Host "python main.py" -ForegroundColor White
