# Ping Pong Ball Tracking System

A real-time ping pong ball tracking system for Raspberry Pi 5 with RPi AI Hat, featuring servo-controlled pan-tilt camera movement and web-based monitoring interface.

## Features

- **Dual Detection Methods**: 
  - Hailo NPU-accelerated object detection (primary)
  - Color-based HSV filtering (fallback)
- **Real-time Servo Control**: SG90 servos for pan-tilt camera movement
- **Web Interface**: Live video streaming with control panel
- **Modular Design**: Clean separation of components
- **Performance Optimized**: Designed for real-time operation on RPi 5
- **Configurable**: Extensive configuration options

## Hardware Requirements

### Essential Components
- Raspberry Pi 5
- RPi AI Hat (for Hailo NPU acceleration)
- Raspberry Pi Camera Module (CSI interface)
- 2x SG90 Servo Motors
- PCA9685 16-Channel PWM Driver
- Pan-tilt bracket for camera mounting

### Connections
```
PCA9685 → Raspberry Pi 5:
- VCC → 5V (Pin 2 or 4)
- GND → GND (Pin 6)
- SDA → GPIO 2 (Pin 3)
- SCL → GPIO 3 (Pin 5)

Servos → PCA9685:
- Pan Servo → Channel 0
- Tilt Servo → Channel 1

Camera → CSI connector
```

## Software Architecture

```
main.py
├── config.py                 # Configuration settings
├── camera_manager.py         # Camera operations and streaming
├── ball_detector.py          # Ball detection algorithms
├── servo_controller.py       # Servo control and tracking
├── ball_tracker.py          # Main tracking coordination
├── web_interface.py         # Flask web server
└── templates/
    └── index.html           # Web interface
```

## Installation

### 1. Quick Setup
```bash
cd /home/spark/RR2025/ObjectDetection&Tracking
./setup.sh
```

### 2. Manual Installation

#### System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip libopencv-dev python3-opencv i2c-tools python3-smbus
```

#### Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Enable I2C
```bash
sudo raspi-config nonint do_i2c 0
```

## Configuration

Edit `config.py` to customize system behavior:

### Camera Settings
```python
CAMERA_RESOLUTION = (1280, 720)  # Resolution for tracking
CAMERA_FRAMERATE = 30            # FPS
```

### Ball Detection
```python
# Color-based detection (HSV values for orange ball)
BALL_COLOR_HSV_LOWER = (10, 100, 100)
BALL_COLOR_HSV_UPPER = (20, 255, 255)

# Hailo NPU detection
USE_HAILO_DETECTION = True
HAILO_CONFIDENCE_THRESHOLD = 0.5
```

### Servo Control
```python
PAN_SERVO_CHANNEL = 0    # PCA9685 channel for pan
TILT_SERVO_CHANNEL = 1   # PCA9685 channel for tilt

# Control parameters
TRACKING_DEADZONE = 50   # Pixels from center to ignore
PAN_GAIN = 0.1          # Proportional gain for pan
TILT_GAIN = 0.1         # Proportional gain for tilt
MAX_SERVO_STEP = 5      # Maximum movement per frame (degrees)
```

## Usage

### Start the System
```bash
cd /home/spark/RR2025/ObjectDetection&Tracking
./start_tracking.sh
```

### Web Interface
Open a browser and navigate to:
```
http://localhost:5000
# or
http://[raspberry-pi-ip]:5000
```

### Web Interface Features
- **Live Video Stream**: Real-time camera feed with detection overlays
- **Control Buttons**: Start/stop tracking, center camera
- **System Status**: FPS, detection count, servo positions
- **Configuration**: Adjust tracking parameters in real-time

### Command Line Options
```bash
# Run without web interface (tracking only)
python3 main.py --no-web

# Set log level
python3 main.py --log-level DEBUG

# Show help
python3 main.py --help
```

## System Operation

### Detection Process
1. **Primary**: Hailo NPU detects "sports ball" class objects
2. **Fallback**: Color-based detection using HSV filtering
3. **Filtering**: Moving average smoothing reduces noise

### Tracking Algorithm
1. Calculate ball position relative to frame center
2. Apply deadzone to prevent jitter
3. Calculate proportional servo adjustments
4. Apply smoothing and step limiting
5. Update servo positions

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

# Should show PCA9685 at address 0x40
```

### Servo Issues
- Verify PCA9685 connections
- Check servo power supply (5V, adequate current)
- Test individual servo movement

### Hailo Issues
- Ensure RPi AI Hat is properly connected
- Check Hailo installation in HailoNPU_POC directory
- Fallback to color detection if Hailo unavailable

### Performance Issues
- Lower camera resolution if needed
- Adjust tracking parameters
- Check CPU usage and temperature

## Advanced Configuration

### Custom Detection Classes
Modify `ball_detector.py` to detect different objects:
```python
HAILO_BALL_CLASS_NAME = "tennis ball"  # or other sports equipment
```

### Servo Calibration
Adjust servo limits in `config.py`:
```python
PAN_MIN_ANGLE = 0
PAN_MAX_ANGLE = 180
TILT_MIN_ANGLE = 45
TILT_MAX_ANGLE = 135
```

### Color Detection Tuning
Use HSV color picker tools to find optimal color ranges:
```python
BALL_COLOR_HSV_LOWER = (hue_min, sat_min, val_min)
BALL_COLOR_HSV_UPPER = (hue_max, sat_max, val_max)
```

## System Service Installation

To run as a system service:

```bash
sudo cp ball-tracker.service /etc/systemd/system/
sudo systemctl enable ball-tracker
sudo systemctl start ball-tracker

# Check status
sudo systemctl status ball-tracker

# View logs
sudo journalctl -u ball-tracker -f
```

## API Endpoints

The web interface provides REST API endpoints:

- `GET /api/status` - System status
- `POST /api/start_tracking` - Start tracking
- `POST /api/stop_tracking` - Stop tracking
- `POST /api/center_camera` - Center servos
- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration

## File Structure

```
ObjectDetection&Tracking/
├── main.py                   # Main application
├── config.py                 # Configuration
├── camera_manager.py         # Camera handling
├── ball_detector.py          # Detection algorithms
├── servo_controller.py       # Servo control
├── ball_tracker.py          # Tracking coordination
├── web_interface.py         # Web server
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
