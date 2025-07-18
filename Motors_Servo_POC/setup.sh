#!/bin/bash
# Setup script for Robot Controller

echo "=== Robot Controller Setup ==="
echo "Setting up environment for RPi 5 Robot Controller..."

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This setup is designed for Raspberry Pi"
fi

# Update system
echo "1. Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "2. Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    i2c-tools \
    git

# Enable I2C
echo "3. Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Create virtual environment
echo "4. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "5. Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up permissions
echo "6. Setting up I2C permissions..."
sudo usermod -a -G i2c $USER

# Test I2C connection
echo "7. Testing I2C connection..."
if command -v i2cdetect >/dev/null 2>&1; then
    echo "I2C devices detected:"
    i2cdetect -y 1
else
    echo "i2cdetect not available, skipping I2C test"
fi

# Create systemd service (optional)
echo "8. Creating systemd service (optional)..."
cat > robot-controller.service << EOF
[Unit]
Description=Robot Controller Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py --mode patrol
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created: robot-controller.service"
echo "To install as system service:"
echo "  sudo cp robot-controller.service /etc/systemd/system/"
echo "  sudo systemctl enable robot-controller"
echo "  sudo systemctl start robot-controller"

echo ""
echo "=== Setup Complete ==="
echo "Next steps:"
echo "1. Reboot to ensure I2C is enabled: sudo reboot"
echo "2. Connect your PCA9685, motors, and servos"
echo "3. Test the setup: python3 main.py --mode test"
echo "4. Run demo: python3 main.py --mode demo"
echo ""
echo "Don't forget to activate the virtual environment:"
echo "  source venv/bin/activate"
