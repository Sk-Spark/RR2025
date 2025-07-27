#!/bin/bash
# Setup script for Ping Pong Ball Tracking System
# Run this script to install dependencies and configure the system

set -e

echo "========================================"
echo "Ping Pong Ball Tracking System Setup"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This system is optimized for Raspberry Pi 5"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
VENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install system dependencies
echo "Installing system dependencies..."

# Check if apt is available (Debian/Ubuntu based systems)
if command -v apt-get &> /dev/null; then
    echo "Installing system packages via apt..."
    sudo apt-get update
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        libopencv-dev \
        python3-opencv \
        i2c-tools \
        python3-smbus \
        libatlas-base-dev \
        libhdf5-dev \
        libhdf5-serial-dev \
        libatlas-base-dev \
        libjasper-dev \
        libqtgui4 \
        libqt4-test \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Enable I2C if on Raspberry Pi
if command -v raspi-config &> /dev/null; then
    echo "Enabling I2C interface..."
    sudo raspi-config nonint do_i2c 0
fi

# Copy servo controller modules if needed
MOTORS_SERVO_DIR="$PROJECT_ROOT/Motors_Servo_POC"
if [ -d "$MOTORS_SERVO_DIR" ]; then
    echo "Servo controller modules found at: $MOTORS_SERVO_DIR"
else
    echo "Warning: Servo controller modules not found at $MOTORS_SERVO_DIR"
    echo "Make sure the Motors_Servo_POC directory exists and contains the required modules"
fi

# Copy Hailo modules if needed
HAILO_DIR="$PROJECT_ROOT/HailoNPU_POC"
if [ -d "$HAILO_DIR" ]; then
    echo "Hailo NPU modules found at: $HAILO_DIR"
    
    # Check if Hailo is properly installed
    if [ -f "$HAILO_DIR/venv/bin/activate" ]; then
        echo "Hailo virtual environment found"
        echo "You may need to install Hailo dependencies separately"
        echo "Run: cd $HAILO_DIR && source venv/bin/activate && pip install -r requirements.txt"
    fi
else
    echo "Warning: Hailo NPU modules not found at $HAILO_DIR"
    echo "Color-based detection will be used as fallback"
fi

# Create log directory
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Create startup script
STARTUP_SCRIPT="$SCRIPT_DIR/start_tracking.sh"
cat > "$STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
# Startup script for Ping Pong Ball Tracking System

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Start the tracking system
python3 main.py "$@"
EOF

chmod +x "$STARTUP_SCRIPT"

# Create systemd service file (optional)
SERVICE_FILE="$SCRIPT_DIR/ball-tracker.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Ping Pong Ball Tracking System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$SCRIPT_DIR
ExecStart=$STARTUP_SCRIPT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Setup complete!"
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Hardware Setup:"
echo "   - Connect PCA9685 to I2C (SDA: GPIO 2, SCL: GPIO 3)"
echo "   - Connect SG90 servos to PCA9685 channels 0 (pan) and 1 (tilt)"
echo "   - Mount camera on servo bracket"
echo "   - Connect RPi camera to CSI port"
echo ""
echo "2. Test the system:"
echo "   cd $SCRIPT_DIR"
echo "   ./start_tracking.sh"
echo ""
echo "3. Access web interface:"
echo "   http://localhost:5000 (or your Pi's IP address)"
echo ""
echo "4. Optional - Install as system service:"
echo "   sudo cp ball-tracker.service /etc/systemd/system/"
echo "   sudo systemctl enable ball-tracker"
echo "   sudo systemctl start ball-tracker"
echo ""
echo "Configuration can be modified in config.py"
echo "========================================"
