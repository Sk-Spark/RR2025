# 🤖 AI Bot Controller for Raspberry Pi 5

A comprehensive web-based controller for an AI-powered robot running on Raspberry Pi 5 with Hailo NPU acceleration. This system integrates real-time object detection, mecanum wheel motor control, camera pan/tilt servos, and IMU sensor data into a unified web interface.

## ✨ Features

### 🎯 AI & Vision
- **Real-time Object Detection** using Hailo NPU acceleration
- **Live Video Streaming** with detection overlays
- **COCO dataset** object recognition (80+ classes)
- **Configurable detection threshold**
- **Toggle detection on/off** during operation

### 🚗 Robot Control
- **4-Wheel Mecanum Drive** for omnidirectional movement
- **Variable speed control** (10-100%)
- **Precise movement commands**: Forward, Backward, Left, Right, Strafe Left, Strafe Right
- **Emergency stop** functionality
- **Keyboard controls** (WASD + QE for strafing)

### 📷 Camera Control
- **Pan/Tilt servo control** (0-180° range)
- **Smooth servo movements** with configurable speed and easing
- **Real-time adjustment** via web sliders
- **Quick position presets** (Up, Down, Left, Right, Center)
- **Simultaneous pan/tilt** movements
- **Camera position feedback**
- **Multiple easing types**: Linear, Ease-in, Ease-out, Ease-in-out

### 📊 Sensors & Monitoring
- **MPU6050 IMU** data (accelerometer, gyroscope, temperature)
- **Real-time sensor readings** via WebSocket
- **System status monitoring**
- **Live detection count**
- **Connection status indicator**

### 🌐 Web Interface
- **Responsive design** for desktop and mobile
- **Real-time updates** via WebSocket
- **Intuitive control layout**
- **Live video feed**
- **Modern glassmorphism UI**

## 🔧 Hardware Requirements

### Core Components
- **Raspberry Pi 5** (4GB+ recommended)
- **Hailo AI Hat+** or compatible NPU
- **RPi Camera Module** (v2/v3 or compatible)
- **MicroSD Card** (32GB+ Class 10)

### Motor System
- **4x BO Motors** with encoders
- **PCA9685 PWM Driver** (16-channel)
- **Motor driver boards** (L298N or similar)
- **Mecanum wheels** (4x)

### Servo System
- **2x SG90 Micro Servos** for camera pan/tilt
- **Servo mount/bracket** for camera

### Sensors
- **MPU6050** 6-axis IMU sensor
- **I2C connection** capability

### Power & Connectivity
- **Power supply** (5V 4A+ recommended)
- **Wi-Fi** or Ethernet connection
- **Proper grounding** and wiring

## 📋 Software Requirements

### System Requirements
- **Raspberry Pi OS** (64-bit recommended)
- **Python 3.8+**
- **I2C enabled**
- **Camera interface enabled**

### Dependencies
See `requirements.txt` for complete Python package list.

Key packages:
- Flask & Flask-SocketIO
- OpenCV
- NumPy
- picamera2
- Adafruit CircuitPython libraries
- GPIO libraries

## 🚀 Installation

### Quick Setup
1. **Clone or download** this project to your Raspberry Pi
2. **Navigate** to the AiBot directory:
   ```bash
   cd /home/spark/RR2025/AiBot
   ```
3. **Run the setup script**:
   ```bash
   ./setup.sh
   ```
4. **Reboot** the system:
   ```bash
   sudo reboot
   ```

### Manual Setup
If you prefer manual installation:

1. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install system dependencies**:
   ```bash
   sudo apt install python3-pip python3-venv i2c-tools -y
   ```

3. **Enable interfaces**:
   ```bash
   sudo raspi-config nonint do_i2c 0
   sudo raspi-config nonint do_camera 0
   ```

4. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

## 🔌 Hardware Connections

### Motor Connections (PCA9685)
```
Front Right Motor:
- PWM Channel: 15
- IN1: GPIO 14
- IN2: GPIO 13

Front Left Motor:
- PWM Channel: 4
- IN1: GPIO 5
- IN2: GPIO 6

Rear Right Motor:
- PWM Channel: 10
- IN1: GPIO 12
- IN2: GPIO 11

Rear Left Motor:
- PWM Channel: 9
- IN1: GPIO 7
- IN2: GPIO 8
```

### Servo Connections (PCA9685)
```
Camera Pan Servo:
- PWM Channel: 2

Camera Tilt Servo:
- PWM Channel: 3
```

### MPU6050 Connections
```
VCC → 3.3V
GND → GND
SCL → GPIO 3 (Pin 5)
SDA → GPIO 2 (Pin 3)
```

### I2C Addresses
- **PCA9685**: 0x40 (default)
- **MPU6050**: 0x68 (default)

## 🎮 Usage

### Starting the System

#### Method 1: Direct execution
```bash
cd /home/spark/RR2025/AiBot
source venv/bin/activate
python main.py
```

#### Method 2: Using startup script
```bash
./start_aibot.sh
```

#### Method 3: System service
```bash
sudo systemctl start aibot.service
```

### Accessing the Web Interface
1. **Find your Pi's IP address**:
   ```bash
   hostname -I
   ```
2. **Open web browser** and navigate to:
   ```
   http://YOUR_PI_IP:5000
   ```
3. **Use the interface** to control your robot!

### Web Interface Controls

#### Robot Movement
- **Arrow buttons**: Forward, Backward, Left, Right
- **Strafe buttons**: Diagonal movement (mecanum wheels)
- **Stop button**: Emergency stop
- **Speed slider**: Adjust movement speed (10-100%)

#### Camera Control
- **Pan slider**: Horizontal camera movement (0-180°)
- **Tilt slider**: Vertical camera movement (0-180°)
- **Smooth Movement Toggle**: Enable/disable smooth servo movements
- **Movement Speed**: Adjust movement duration (0.2-3.0 seconds)
- **Quick Position Buttons**: 
  - ⬆️ Up (Pan: 90°, Tilt: 45°)
  - ⬅️ Left (Pan: 0°, Tilt: 90°)
  - 🎯 Center (Pan: 90°, Tilt: 90°)
  - ➡️ Right (Pan: 180°, Tilt: 90°)
  - ⬇️ Down (Pan: 90°, Tilt: 135°)

#### Keyboard Shortcuts
- **W**: Forward
- **S**: Backward
- **A**: Turn Left
- **D**: Turn Right
- **Q**: Strafe Left
- **E**: Strafe Right
- **Space**: Stop

#### Detection Control
- **Toggle switch**: Enable/disable object detection
- **Live feed**: Real-time video with detection overlays

## 📊 Monitoring & Logs

### System Status
The web interface displays:
- **Connection status**
- **Detection count**
- **Robot movement status**
- **Sensor readings** (accelerometer, gyroscope, temperature)

### Log Files
- **Application logs**: `aibot.log`
- **System service logs**: `sudo journalctl -u aibot.service -f`

### Service Management
```bash
# Check service status
sudo systemctl status aibot.service

# View live logs
sudo journalctl -u aibot.service -f

# Restart service
sudo systemctl restart aibot.service
```

## 🔧 Configuration

### Environment Variables
You can customize behavior using environment variables:

```bash
export VIDEO_WIDTH=640
export VIDEO_HEIGHT=480
export DETECTION_THRESHOLD=0.5
export LOG_LEVEL=INFO
export PORT=5000
```

### Configuration File
Edit `config.py` to modify:
- **Motor pin assignments**
- **Servo configurations**
- **I2C addresses**
- **Default parameters**

## 🛠️ Troubleshooting

### Common Issues

#### Camera not working
```bash
# Check camera detection
libcamera-hello --list-cameras

# Test camera
libcamera-still -o test.jpg
```

#### I2C devices not detected
```bash
# Scan I2C bus
i2cdetect -y 1

# Check I2C is enabled
sudo raspi-config
```

#### Permission errors
```bash
# Add user to groups
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER

# Reboot required after group changes
sudo reboot
```

#### Hailo NPU not available
```bash
# Check Hailo installation
python3 -c "from picamera2.devices import Hailo; print('Hailo OK')"

# Install Hailo drivers (follow official documentation)
```

#### Web interface not accessible
```bash
# Check if service is running
sudo systemctl status aibot.service

# Check network connectivity
ip addr show

# Check firewall settings
sudo ufw status
```

### Debug Mode
Run with debug output:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 🔄 Updates & Maintenance

### Updating the Code
```bash
cd /home/spark/RR2025/AiBot
git pull  # if using git
sudo systemctl restart aibot.service
```

### Updating Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 🤝 Contributing

Feel free to contribute improvements:
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## 📝 License

This project is open source. Please check individual component licenses for specific terms.

## 🆘 Support

For issues and questions:
1. **Check** the troubleshooting section
2. **Review** log files
3. **Test** hardware connections
4. **Search** existing issues
5. **Create** a new issue with detailed information

## 🚀 Future Enhancements

Planned features:
- **Voice control** integration
- **Autonomous navigation**
- **Object tracking**
- **Remote access** via cloud
- **Multi-robot** coordination
- **Custom model** support
- **Mobile app** companion

---

**Happy robotics! 🤖✨**
