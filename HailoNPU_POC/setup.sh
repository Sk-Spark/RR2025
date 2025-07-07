#!/bin/bash

# Setup script for RPi AI Hat+ Object Detection System
# This script installs dependencies and configures the system

set -e

echo "🚀 Setting up RPi AI Hat+ Object Detection System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    print_warning "This script is designed for Raspberry Pi. Some features may not work on other systems."
fi

# Check for Raspberry Pi 5
if grep -q "BCM2712" /proc/cpuinfo; then
    print_status "Raspberry Pi 5 detected ✓"
else
    print_warning "Raspberry Pi 5 not detected. Some features may not work optimally."
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    cmake \
    build-essential \
    libopencv-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    gfortran \
    openexr \
    libatlas-base-dev \
    python3-numpy \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz-dev

# Install camera support
print_status "Installing camera support..."
sudo apt install -y \
    python3-picamera2 \
    libcamera-apps \
    libcamera-dev

# Enable camera interface
print_status "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install heloRT (Hailo Runtime Library)
print_status "Installing heloRT library..."
if [ ! -f "heloRT-*.whl" ]; then
    print_warning "heloRT wheel file not found. Please download it from Hailo's official repository."
    print_warning "Visit: https://github.com/hailo-ai/hailort"
    print_warning "You can install it manually with: pip install heloRT-*.whl"
else
    pip install heloRT-*.whl
    print_status "heloRT installed successfully ✓"
fi

# Download YOLOv8 model (if not present)
print_status "Checking for YOLOv8 model..."
if [ ! -f "yolov8n.hef" ]; then
    print_warning "YOLOv8 Hailo model (yolov8n.hef) not found."
    print_warning "Please obtain the model from Hailo's model zoo or convert your own model."
    print_warning "Visit: https://github.com/hailo-ai/hailo_model_zoo"
fi

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/rpi-object-detection.service > /dev/null <<EOF
[Unit]
Description=RPi AI Hat+ Object Detection Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
print_status "Enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable rpi-object-detection.service

# Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/rpi-object-detection > /dev/null <<EOF
$(pwd)/object_detection.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

# Create desktop shortcut
print_status "Creating desktop shortcut..."
cat > ~/Desktop/RPi-Object-Detection.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=RPi Object Detection
Comment=Launch RPi AI Hat+ Object Detection System
Exec=x-www-browser http://localhost:5000
Icon=applications-multimedia
Terminal=false
Categories=Development;
EOF

chmod +x ~/Desktop/RPi-Object-Detection.desktop

# Final setup
print_status "Setting up permissions..."
sudo usermod -a -G video,gpio,i2c,spi $USER

# Create startup script
print_status "Creating startup script..."
cat > start.sh <<EOF
#!/bin/bash
cd $(pwd)
source venv/bin/activate
python main.py
EOF

chmod +x start.sh

print_status "✅ Setup complete!"
echo
echo "📋 Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. After reboot, start the service: sudo systemctl start rpi-object-detection"
echo "3. Check service status: sudo systemctl status rpi-object-detection"
echo "4. Access the web interface: http://localhost:5000"
echo "5. For remote access, use: http://[RPi-IP]:5000"
echo
echo "🔧 Manual start: ./start.sh"
echo "📊 View logs: journalctl -u rpi-object-detection -f"
echo "🌐 Web interface: http://$(hostname -I | awk '{print $1}'):5000"
echo
print_warning "Don't forget to install the heloRT library and YOLOv8 model!"
