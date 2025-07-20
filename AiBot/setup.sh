#!/bin/bash

# AI Bot Setup Script for Raspberry Pi 5
# This script sets up the complete environment for the AI Bot controller

set -e

echo "====================================="
echo "AI Bot Controller Setup Script"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This script is designed for Raspberry Pi. Continuing anyway..."
fi

# Update system packages
print_status "Updating system packages..."
sudo apt-get update

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    python3-pyqt5 \
    python3-h5py \
    libjasper-dev \
    libqt5gui5 \
    libqt5webkit5 \
    libqt5test5 \
    python3-pyqt5 \
    git \
    i2c-tools

# Enable I2C interface
print_status "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Enable camera interface
print_status "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Create virtual environment
print_status "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional dependencies for Raspberry Pi
print_status "Installing Raspberry Pi specific dependencies..."
pip install picamera2[gui]

# Check for Hailo installation
print_status "Checking for Hailo NPU support..."
if python3 -c "from picamera2.devices import Hailo; print('Hailo available')" 2>/dev/null; then
    print_status "Hailo NPU support detected"
else
    print_warning "Hailo NPU support not detected. Please install Hailo drivers separately."
    print_warning "Visit: https://hailo.ai/developer-zone/ for installation instructions."
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p static
mkdir -p templates

# Set permissions for GPIO access
print_status "Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER

# Create systemd service file
print_status "Creating systemd service file..."
sudo tee /etc/systemd/system/aibot.service > /dev/null <<EOF
[Unit]
Description=AI Bot Controller
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/spark/RR2025/AiBot
Environment=PATH=/home/spark/RR2025/AiBot/venv/bin
ExecStart=/home/spark/RR2025/AiBot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_status "Enabling AI Bot service..."
sudo systemctl daemon-reload
sudo systemctl enable aibot.service

# Create startup script
print_status "Creating startup script..."
cat > start_aibot.sh <<EOF
#!/bin/bash
cd /home/spark/RR2025/AiBot
source venv/bin/activate
python main.py
EOF
chmod +x start_aibot.sh

# Create stop script
print_status "Creating stop script..."
cat > stop_aibot.sh <<EOF
#!/bin/bash
sudo systemctl stop aibot.service
EOF
chmod +x stop_aibot.sh

# Test I2C devices
print_status "Testing I2C devices..."
echo "Scanning for I2C devices..."
i2cdetect -y 1

print_status "Setup completed successfully!"
echo ""
echo "====================================="
echo "Setup Summary:"
echo "====================================="
echo "✓ System packages installed"
echo "✓ Python virtual environment created"
echo "✓ Dependencies installed"
echo "✓ I2C and camera interfaces enabled"
echo "✓ Systemd service created"
echo "✓ Startup scripts created"
echo ""
echo "Next steps:"
echo "1. Reboot the system: sudo reboot"
echo "2. Test the setup: ./start_aibot.sh"
echo "3. Access web interface: http://$(hostname -I | cut -d' ' -f1):5000"
echo ""
echo "Service commands:"
echo "- Start service: sudo systemctl start aibot.service"
echo "- Stop service: sudo systemctl stop aibot.service"
echo "- Check status: sudo systemctl status aibot.service"
echo "- View logs: sudo journalctl -u aibot.service -f"
echo ""
print_warning "Please reboot the system for all changes to take effect!"
