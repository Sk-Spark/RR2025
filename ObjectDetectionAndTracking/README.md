# Ping Pong Ball Tracking System with Robot Following

A real-time ping pong ball tracking system for Raspberry Pi 5 with Hailo NPU acceleration, featuring servo-controlled pan-tilt camera movement, robot movement for ball following, and web-based monitoring interface.

## Features

- **Hailo NPU-Accelerated Detection**: Real-time sports ball detection using AI acceleration
- **Real-time Servo Control**: SG90 servos for smooth pan-tilt camera movement  
- **Robot Ball Following**: Mecanum wheel robot movement to follow detected balls
- **Shared Hardware Control**: Unified PCA9685 control for both servos and motors
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

### Optional Components for Robot Following
- **4x DC Motors with Mecanum Wheels** (for robot movement)
- **4x Motor Driver Modules** (H-bridge or similar)
- **Robot chassis** with mecanum wheel setup
- **Additional power supply** for motors (depends on motor specifications)
- **Hailo AI Hat** (for NPU acceleration - enables AI detection)

### Hardware Connections

#### Core System (Camera + Servos)
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

#### Robot Following System (Optional)
```
Motors → PCA9685 (uses same chip as servos):
- Front Right Motor: PWM Channel 15, Direction Channels 14 & 13
- Front Left Motor:  PWM Channel 4,  Direction Channels 5 & 6
- Rear Right Motor:  PWM Channel 10, Direction Channels 12 & 11
- Rear Left Motor:   PWM Channel 9,  Direction Channels 7 & 8

Motor Power:
- Connect motor power supply according to motor specifications
- Ensure common ground between RPi and motor power supply
```

## System Architecture

### Shared PCA9685 Controller
The system uses a **single PCA9685 chip** to control both servos and motors:

- **Frequency**: 50Hz (optimized for servo control)
- **Servo Channels**: 2-3 (pan-tilt camera control)
- **Motor Channels**: 4-15 (mecanum wheel robot control)
- **Shared Control**: One `pca9685_controller.py` module manages all PWM operations

### Why 50Hz for Both Servos and Motors?
- **Servos**: Require exactly 50Hz for proper position control ✅
- **Motors**: Prefer 1000Hz but work acceptably at 50Hz ⚠️
- **Trade-off**: Prioritizes servo precision over motor smoothness
- **Single Chip**: More cost-effective than separate controllers

## Project Structure

```
RR2025/ObjectDetectionAndTracking/
├── main.py                    # Main application entry point
├── config.py                  # System configuration settings
├── 
├── # Core Components
├── camera_manager.py          # Camera operations and frame management
├── hailo_detector.py          # Hailo NPU-based ball detection
├── servo_controller.py        # Servo control and camera tracking
├── motor_controller.py        # Motor control for robot movement
├── pca9685_controller.py      # Shared PCA9685 hardware controller
├── ball_tracker.py           # Main tracking coordination with motor integration
├── web_interface.py          # Flask web server and API
├── system_status.py          # System monitoring and status
├── 
├── # Test Scripts
├── test_hailo_detection.py   # Standalone detection with web interface
├── test_camera_colors.py    # Camera and color detection test
├── test_servo_movement.py   # Servo movement and calibration test
├── test_motor_control.py    # Motor control test
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

### Core Settings
```python
# Camera Configuration
CAMERA_RESOLUTION = (640, 640)  # Camera resolution
CAMERA_FRAMERATE = 30           # Frames per second

# PCA9685 Hardware Configuration
PCA9685_ADDRESS = 0x40          # I2C address of PCA9685
PCA9685_FREQUENCY = 50          # PWM frequency (50Hz for servos)

# Servo Configuration  
PAN_SERVO_CHANNEL = 2           # PCA9685 channel for pan servo
TILT_SERVO_CHANNEL = 3          # PCA9685 channel for tilt servo
PAN_MIN_ANGLE = 0               # Minimum pan angle
PAN_MAX_ANGLE = 180             # Maximum pan angle
TILT_MIN_ANGLE = 45             # Minimum tilt angle  
TILT_MAX_ANGLE = 135            # Maximum tilt angle
```

### Motor Following Configuration
```python
# Motor Following Enable/Disable
ENABLE_MOTOR_FOLLOWING = True   # Set to False to disable robot movement

# Motor Configuration (Mecanum Wheel Setup)
MOTOR_CONFIG = {
    "front_right": {"channel": 15, "in1": 14, "in2": 13},
    "front_left":  {"channel": 4,  "in1": 5,  "in2": 6},
    "rear_right":  {"channel": 10, "in1": 12, "in2": 11},
    "rear_left":   {"channel": 9,  "in1": 7,  "in2": 8},
}

# Motor Control Parameters
MOTOR_FOLLOW_SPEED = 40         # Default following speed (0-100)
MOTOR_DEADZONE_X = 0.15         # Horizontal movement deadzone
MOTOR_DEADZONE_Y = 0.15         # Vertical movement deadzone  
MOTOR_MAX_SPEED = 60            # Maximum motor speed limit
```

### Detection Parameters
```python
# Hailo NPU Detection
CONFIDENCE_THRESHOLD = 0.5      # AI detection confidence threshold
HAILO_BALL_CLASS_NAME = "sports ball"  # COCO class for detection

# Tracking Control
TRACKING_DEADZONE = 50          # Servo deadzone in pixels
PAN_SENSITIVITY = 15            # Pan control sensitivity
TILT_SENSITIVITY = 10           # Tilt control sensitivity
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

# Run the main tracking system with web interface
python3 main.py

# Access the web interface
# Open browser to: http://localhost:5000
# or: http://[raspberry-pi-ip]:5000
```

### Test Scripts

1. **Ball Detection Test with Web Interface**
   ```bash
   # Test Hailo NPU detection with web streaming
   python3 test_hailo_detection.py
   ```

2. **Individual Component Tests**
   ```bash
   # Test camera and HSV color detection
   python3 test_camera_colors.py
   
   # Test servo movement and calibration
   python3 test_servo_movement.py
   
   # Test motor control (if robot following enabled)
   python3 test_motor_control.py
   ```

### Command Line Options
```bash
# Run without web interface (tracking only)
python3 main.py --no-web

# Set logging level
python3 main.py --log-level DEBUG

# Use custom configuration
python3 main.py --config custom_config.py
```

## System Operation

### Ball Tracking and Following Process

1. **Detection Phase**
   - **Primary**: Hailo NPU detects "sports ball" class using YOLOv8
   - **Confidence Filtering**: Only detections above threshold processed
   - **Area Filtering**: Minimum area requirement eliminates noise

2. **Camera Tracking Phase**  
   - **Position Calculation**: Ball center relative to frame center
   - **Deadzone Application**: Ignore small movements (prevent jitter)
   - **Servo Control**: Pan/tilt servos move camera to center ball
   - **Smooth Movement**: Proportional control with movement limiting

3. **Robot Following Phase** (if enabled)
   - **Distance Assessment**: Ball size indicates distance from camera
   - **Movement Decision**: Calculate required robot movement
   - **Mecanum Control**: Strafe, forward/backward, and rotation
   - **Motor Commands**: Shared PCA9685 controls all 4 motors

### Shared Hardware Management

The system uses **intelligent hardware sharing**:

```python
# Initialization Order (main.py)
1. servo_controller = BallTrackingServoController()  # Creates PCA9685 at 50Hz
2. motor_controller = MotorController(pca_controller=servo_controller.pca)  # Shares PCA9685
3. ball_tracker = BallTracker(servo_controller, motor_controller)  # Coordinates both
```

**Benefits:**
- ✅ No hardware conflicts between servos and motors
- ✅ Cost-effective single chip solution  
- ✅ Unified 50Hz PWM frequency
- ✅ Coordinated servo and motor control
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

#### Motor Controller Issues
```bash
# If servos stop working when motor following is enabled:
# This indicates PCA9685 hardware conflict (now fixed with shared controller)

# Check motor configuration in config.py
ENABLE_MOTOR_FOLLOWING = True
MOTOR_CONFIG = {
    "front_right": {"channel": 15, "in1": 14, "in2": 13},
    # ... other motors
}
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

#### Motor Following Issues
- **No robot movement**: Check `ENABLE_MOTOR_FOLLOWING = True` in config.py
- **Motor power**: Ensure adequate power supply for DC motors
- **Motor wiring**: Verify motor connections match `MOTOR_CONFIG` channels
- **Shared PCA9685**: Motor and servo controllers use same PCA9685 instance

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

### Motor Following Customization
```python
# Adjust motor following behavior in config.py
MOTOR_FOLLOW_SPEED = 30         # Reduce for gentler movement
MOTOR_DEADZONE_X = 0.2          # Increase to reduce jitter
MOTOR_DEADZONE_Y = 0.2          # Increase to reduce jitter
MOTOR_MAX_SPEED = 50            # Limit maximum speed

# Disable motor following
ENABLE_MOTOR_FOLLOWING = False  # Camera tracking only
```

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
PAN_MIN_ANGLE = 20      # Minimum safe pan angle
PAN_MAX_ANGLE = 160     # Maximum safe pan angle
TILT_MIN_ANGLE = 30     # Minimum safe tilt angle
TILT_MAX_ANGLE = 150    # Maximum safe tilt angle

# Fine-tune tracking sensitivity
TRACKING_DEADZONE = 30          # Reduce for more sensitive tracking
PAN_SENSITIVITY = 20            # Increase for faster response
TILT_SENSITIVITY = 15           # Increase for faster response
```

### Mecanum Wheel Configuration
```python
# Adjust mecanum wheel kinematics if needed
# In motor_controller.py, modify mecanum_move() for different wheel arrangements
fl_speed = y_speed + x_speed + rotation_speed  # Front left
fr_speed = y_speed - x_speed - rotation_speed  # Front right
rl_speed = y_speed - x_speed + rotation_speed  # Rear left
rr_speed = y_speed + x_speed - rotation_speed  # Rear right
```

## System Architecture Details

### Component Hierarchy
```
main.py
├── CameraManager           # Camera operations
├── BallTrackingServoController  # Servo control (creates PCA9685)
├── MotorController        # Motor control (shares PCA9685)
├── HailoBallDetector      # AI-based detection
├── BallTracker           # Coordination logic
└── WebServer             # Web interface
```

### Data Flow
1. **Camera** → captures frames
2. **HailoBallDetector** → processes frames for ball detection
3. **BallTracker** → coordinates servo movement and motor following
4. **ServoController** → moves camera via PCA9685 (50Hz)
5. **MotorController** → moves robot via shared PCA9685 (50Hz)
6. **WebServer** → streams video and provides monitoring interface

### Shared PCA9685 Benefits
- **Hardware Efficiency**: Single chip controls both servos and motors
- **Cost Effective**: No need for multiple PWM controllers
- **Conflict Prevention**: Unified management prevents I2C conflicts
- **Synchronized Control**: Coordinated servo and motor movements

## Contributing

### Development Setup
```bash
# Clone repository for development
git clone [repository-url] ObjectDetectionAndTracking
cd ObjectDetectionAndTracking

# Create development branch
git checkout -b feature/your-feature

# Make changes and test
python3 main.py --log-level DEBUG
```

### Code Structure Guidelines
- **Modular Design**: Each component has a dedicated file
- **Shared Resources**: Use pca9685_controller.py for hardware access
- **Configuration**: All settings in config.py
- **Logging**: Use logging module for debugging
- **Error Handling**: Graceful degradation when components fail

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Hailo AI** for NPU acceleration technology
- **Raspberry Pi Foundation** for the excellent hardware platform
- **Adafruit** for CircuitPython libraries and hardware support
- **OpenCV** community for computer vision tools
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
