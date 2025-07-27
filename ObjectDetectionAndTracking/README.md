# Ping Pong Ball Tracking System

A real-time ping pong ball tracking system for Raspberry Pi 5 with Hailo NPU acceleration, featuring servo-controlled pan-tilt camera movement and web-based monitoring interface.

## Features

- **Hailo NPU-Accelerated Detection**: Real-time sports ball detection using AI acceleration
- **Real-time Servo Control**: SG90 servos for smooth pan-tilt camera movement  
- **Web Interface**: Live video streaming with detection visualization
- **Modular Design**: Clean separation of components for easy maintenance
- **Performance Optimized**: Designed for real-time operation on RPi 5
- **Configurable**: Extensive configuration options for different scenarios

## Hardware Requirements

### Essential Components
- **Raspberry Pi 5** (4GB+ recommended)
- **Raspberry Pi Camera Module** (v2/v3 or HQ Camera)
- **2x SG90 Servo Motors** (micro servos)
- **PCA9685 16-Channel PWM Driver** (I2C)
- **Pan-tilt bracket** for camera mounting
- **Jumper wires** for connections
- **Power supply** (5V 3A for Pi + servos)

### Optional Components
- **Hailo AI Hat** (for NPU acceleration - enables AI detection)
- **Breadboard** for prototyping connections

### Hardware Connections
```
PCA9685 → Raspberry Pi 5:
- VCC → 5V (Pin 2 or 4)
- GND → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
- SDA → GPIO 2 (Pin 3)
- SCL → GPIO 3 (Pin 5)

Servos → PCA9685:
- Pan Servo → Channel 2 (config: PAN_SERVO_CHANNEL = 2)
- Tilt Servo → Channel 3 (config: TILT_SERVO_CHANNEL = 3)

Camera → Raspberry Pi CSI connector
```

## Project Structure

```
RR2025/ObjectDetectionAndTracking/
├── main.py                    # Main application entry point
├── config.py                  # System configuration settings
├── 
├── # Core Components
├── camera_manager.py          # Camera operations and frame management
├── hailo_detector.py          # Hailo NPU-based ball detection
├── servo_controller.py        # PCA9685 servo control and tracking
├── ball_tracker.py           # Main tracking coordination logic
├── web_interface.py          # Flask web server and API
├── system_status.py          # System monitoring and status
├── 
├── # Test Scripts
├── test_hailo_detection.py   # Standalone Hailo detection test
├── test_camera_colors.py    # Camera and color detection test
├── test_servo_movement.py   # Servo movement and calibration test
├── 
├── # Configuration & Setup
├── requirements.txt          # Python dependencies
├── setup.sh                 # System setup script
├── 
├── # Resources
├── resources/
│   └── models/
│       └── hailo8/
│           ├── yolov8m.hef   # YOLOv8 medium model
│           ├── yolov6n.hef   # YOLOv6 nano model  
│           └── yolov5m_seg.hef # YOLOv5 segmentation model
├── coco.txt                 # COCO class labels
├── 
├── # Web Interface
├── templates/
│   └── index.html           # Web interface template
├── 
├── # Logs and Runtime
├── ball_tracking.log        # Application logs
├── hailort.log             # Hailo runtime logs
└── __pycache__/            # Python cache files
```

## Software Installation

### Prerequisites

1. **Raspberry Pi OS Setup**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Enable I2C for PCA9685
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   
   # Enable camera
   sudo raspi-config
   # Navigate to: Interface Options → Camera → Enable
   
   # Reboot after changes
   sudo reboot
   ```

2. **Install System Dependencies**
   ```bash
   # Essential system packages
   sudo apt install -y \
       python3-dev \
       python3-pip \
       python3-picamera2 \
       python3-opencv \
       python3-numpy \
       python3-flask \
       python3-simplejpeg \
       i2c-tools \
       git
   
   # Verify I2C is working
   sudo i2cdetect -y 1
   # Should show your PCA9685 at address 0x40
   ```

3. **Install Python Libraries (System Packages)**
   
   **Important**: Use system packages to avoid numpy version conflicts:
   ```bash
   # Use system packages for core dependencies
   pip3 install --break-system-packages \
       adafruit-circuitpython-pca9685 \
       adafruit-circuitpython-motor \
       adafruit-circuitpython-servokit
   
   # Additional required packages
   pip3 install --break-system-packages \
       board \
       busio
   ```

### Hailo NPU Setup (Optional but Recommended)

1. **Install Hailo Runtime**
   ```bash
   # Download and install HailoRT
   wget https://hailo.ai/downloads/hailort/[version]/hailort-[version]-linux.deb
   sudo dpkg -i hailort-[version]-linux.deb
   
   # Install Python bindings
   pip3 install --break-system-packages hailort
   ```

2. **Download AI Models**
   ```bash
   # Create models directory
   mkdir -p resources/models/hailo8/
   
   # Download YOLOv8 medium model (recommended)
   wget -O resources/models/hailo8/yolov8m.hef \
       https://hailo-model-zoo.s3.amazonaws.com/[model-url]
   ```

### Project Installation

1. **Clone Repository**
   ```bash
   cd ~/RR2025
   git clone [repository-url] ObjectDetectionAndTracking
   cd ObjectDetectionAndTracking
   ```

2. **Install Project Dependencies**
   ```bash
   # Install from requirements.txt using system packages
   pip3 install --break-system-packages -r requirements.txt
   ```

3. **Run Setup Script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

## System Configuration

The system uses `config.py` for all configuration parameters:

```python
# Key Configuration Parameters
CAMERA_WIDTH = 1640          # Camera resolution width
CAMERA_HEIGHT = 1232         # Camera resolution height
CAMERA_FPS = 30             # Frames per second

# Servo Configuration
PAN_SERVO_CHANNEL = 2       # PCA9685 channel for pan servo
TILT_SERVO_CHANNEL = 3      # PCA9685 channel for tilt servo
PAN_MIN = 20                # Minimum pan angle
PAN_MAX = 160              # Maximum pan angle
TILT_MIN = 30              # Minimum tilt angle  
TILT_MAX = 150             # Maximum tilt angle

# Detection Parameters
MIN_BALL_AREA = 500        # Minimum area for ball detection
CONFIDENCE_THRESHOLD = 0.5  # AI detection confidence threshold
TRACKING_SENSITIVITY = 0.8  # Servo tracking sensitivity

# HSV Color Range (fallback detection)
BALL_COLOR_LOWER = (15, 100, 100)  # Lower HSV bound
BALL_COLOR_UPPER = (35, 255, 255)  # Upper HSV bound
```

## Required Python Libraries

### System Packages (Pre-installed)
- `python3-picamera2` - Camera interface
- `python3-opencv` - Computer vision (cv2)
- `python3-numpy` - Numerical computing 
- `python3-flask` - Web framework
- `python3-simplejpeg` - JPEG encoding

### Additional Libraries (pip install)
- `adafruit-circuitpython-pca9685` - PCA9685 PWM driver
- `adafruit-circuitpython-motor` - Motor control
- `adafruit-circuitpython-servokit` - Servo control utilities
- `board` - Hardware pin definitions
- `busio` - I2C/SPI communication
- `hailort` - Hailo NPU runtime (optional)

## Usage

### Quick Start
```bash
# Navigate to project directory
cd ~/RR2025/ObjectDetectionAndTracking

# Run the ball tracking test
python3 test_hailo_detection.py

# Access the web interface
# Open browser to: http://localhost:5000
# or: http://[raspberry-pi-ip]:5000
```

### Test Scripts

1. **Ball Detection Test**
   ```bash
   # Test Hailo NPU detection with web streaming
   python3 test_hailo_detection.py
   ```

2. **Camera and Color Detection Test**
   ```bash
   # Test camera and HSV color detection
   python3 test_camera_colors.py
   ```

3. **Servo Movement Test**
   ```bash
   # Test servo movement and calibration
   python3 test_servo_movement.py
   ```

### Main Application
```bash
# Start the full tracking system
python3 main.py
```

### Web Interface Features
- **Live Video Stream**: Real-time camera feed with detection overlays
- **Detection Visualization**: Bounding boxes around detected balls
- **System Status**: FPS counter, detection confidence, servo positions
- **Real-time Control**: Camera positioning and tracking controls

## System Operation

### Detection Process
1. **Primary Detection**: Hailo NPU detects "sports ball" class objects using YOLOv8
2. **Fallback Detection**: HSV color-based detection for orange ping pong balls
3. **Confidence Filtering**: Only detections above threshold are processed
4. **Area Filtering**: Minimum area requirement eliminates noise

### Tracking Algorithm
1. **Position Calculation**: Determine ball center relative to frame center
2. **Deadzone Application**: Ignore small movements to prevent jitter
3. **Proportional Control**: Calculate servo adjustments based on position error
4. **Movement Limiting**: Apply maximum step size to ensure smooth movement
5. **Servo Update**: Send PWM signals to pan/tilt servos via PCA9685

### Key Features
- **Real-time Performance**: 30 FPS processing with minimal latency
- **Smooth Tracking**: Proportional control with deadzone prevents oscillation
- **Robust Detection**: Dual detection methods ensure reliability
- **Web Monitoring**: Live video stream with overlaid detection data

### Performance Monitoring
- Frame rate monitoring
- Processing time tracking
- Detection statistics
- Servo movement counting

## Troubleshooting

### Camera Issues
```bash
# Check camera detection
libcamera-hello --list-cameras

# Test camera capture
libcamera-jpeg -o test.jpg
```

### I2C Issues
```bash
# Check I2C devices
sudo i2cdetect -y 1

## Troubleshooting

### Common Issues and Solutions

#### Camera Not Detected
```bash
# Check camera connection
libcamera-hello --list-cameras

# If no cameras detected:
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

#### I2C Communication Errors
```bash
# Check I2C is enabled
sudo raspi-config
# Interface Options → I2C → Enable

# Scan for I2C devices
sudo i2cdetect -y 1
# Should show PCA9685 at address 0x40

# If no devices found:
# - Check wiring connections
# - Verify 5V power to PCA9685
# - Check SDA/SCL connections
```

#### Dependency Conflicts
```bash
# Remove conflicting packages
pip3 uninstall numpy opencv-python

# Use system packages only
sudo apt install python3-numpy python3-opencv
```

#### Servo Movement Issues
- **Check PCA9685 connections**: Verify VCC (5V), GND, SDA (GPIO 2), SCL (GPIO 3)
- **Power supply**: Ensure adequate 5V current for servos (minimum 2A)
- **Servo channels**: Verify pan servo on channel 2, tilt servo on channel 3
- **Servo direction**: If movement is inverted, check servo mounting orientation

#### Hailo NPU Issues
```bash
# Check Hailo installation
python3 -c "import hailo_platform"

# Verify model files exist
ls -la resources/models/hailo8/

# Check Hailo logs
tail -f hailort.log
```

#### Performance Issues
- **High CPU usage**: Lower camera resolution in config.py
- **Slow frame rate**: Reduce CAMERA_FPS or image processing complexity
- **Memory issues**: Check available RAM and swap usage
- **Thermal throttling**: Monitor CPU temperature

### System Monitoring
```bash
# Check system resources
htop

# Monitor CPU temperature
vcgencmd measure_temp

# Check memory usage
free -h

# View application logs
tail -f ball_tracking.log
```

## Advanced Configuration

### Custom Detection Objects
Modify detection targets in `hailo_detector.py`:
```python
# Change target class for different sports equipment
TARGET_CLASS_NAME = "tennis ball"  # or "baseball", "basketball"
```

### Servo Calibration
Fine-tune servo ranges in `config.py`:
```python
# Adjust based on your pan-tilt bracket limitations
PAN_MIN = 20        # Minimum safe pan angle
PAN_MAX = 160       # Maximum safe pan angle
TILT_MIN = 30       # Minimum safe tilt angle
TILT_MAX = 150      # Maximum safe tilt angle

# Fine-tune tracking sensitivity
TRACKING_DEADZONE = 30      # Reduce for more sensitive tracking
TRACKING_SENSITIVITY = 0.8  # Increase for faster response
```

### Color Detection Tuning
Use HSV color picker tools to optimize color detection:
```python
# Orange ping pong ball (typical values)
BALL_COLOR_LOWER = (15, 100, 100)  # Lower HSV bound
BALL_COLOR_UPPER = (35, 255, 255)  # Upper HSV bound

# White ping pong ball
# BALL_COLOR_LOWER = (0, 0, 200)
# BALL_COLOR_UPPER = (180, 30, 255)
```

## System Service Setup

To run the tracking system as a background service:

1. **Create service file**:
   ```bash
   sudo nano /etc/systemd/system/ball-tracker.service
   ```

2. **Service configuration**:
   ```ini
   [Unit]
   Description=Ping Pong Ball Tracking System
   After=network.target
   
   [Service]
   Type=simple
   User=spark
   WorkingDirectory=/home/spark/RR2025/ObjectDetectionAndTracking
   ExecStart=/usr/bin/python3 main.py
   Restart=always
   RestartSec=5
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service**:
   ```bash
   sudo systemctl enable ball-tracker
   sudo systemctl start ball-tracker
   
   # Check status
   sudo systemctl status ball-tracker
   
   # View logs
   sudo journalctl -u ball-tracker -f
   ```

## API Reference

The system provides REST API endpoints for integration:

### Status Endpoints
- `GET /api/status` - System status and statistics
- `GET /api/config` - Current configuration parameters

### Control Endpoints  
- `POST /api/start_tracking` - Start ball tracking
- `POST /api/stop_tracking` - Stop ball tracking
- `POST /api/center_camera` - Center pan-tilt servos
- `POST /api/config` - Update configuration parameters

### Example API Usage
```bash
# Get system status
curl http://localhost:5000/api/status

# Start tracking
curl -X POST http://localhost:5000/api/start_tracking

# Center camera
curl -X POST http://localhost:5000/api/center_camera
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on actual hardware
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hailo AI for NPU acceleration technology
- Adafruit for PCA9685 CircuitPython libraries
- Raspberry Pi Foundation for the excellent hardware platform
- OpenCV community for computer vision tools
├── requirements.txt         # Python dependencies
├── setup.sh                # Setup script
├── start_tracking.sh       # Startup script
├── ball-tracker.service    # Systemd service
├── templates/
│   └── index.html          # Web interface
├── logs/                   # Log files
└── venv/                   # Virtual environment
```

## Contributing

When modifying the system:

1. **Test thoroughly** on actual hardware
2. **Update configuration** options in `config.py`
3. **Add logging** for debugging
4. **Update documentation** as needed
5. **Test web interface** functionality

## License

This project is part of the RR2025 robot competition framework.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files in the `logs/` directory
3. Test individual components separately
4. Verify hardware connections

---

**Note**: This system is optimized for Raspberry Pi 5 with actual hardware. Some features may not work in simulation or on other platforms.
