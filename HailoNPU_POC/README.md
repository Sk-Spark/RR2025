# RPi AI Hat+ Object Detection System

A real-time object detection system for Raspberry Pi 5 with AI Hat+ using the heloRT library and YOLOv8 model. This system provides hardware-accelerated inference with a web-based interface for monitoring and visualization.

## 🚀 Features

- **Real-time Object Detection**: YOLOv8 model for accurate object detection
- **Hardware Acceleration**: Leverages RPi AI Hat+ with heloRT library for fast inference
- **Web Interface**: Flask-based web server with live video streaming
- **Headless Operation**: Runs without GUI, perfect for remote deployment
- **Multi-class Detection**: Supports 80+ object classes from COCO dataset
- **Performance Monitoring**: Real-time FPS and system status monitoring
- **Mobile Responsive**: Web interface optimized for mobile devices
- **Automatic Startup**: Systemd service for automatic startup on boot

## 🛠️ Hardware Requirements

- **Raspberry Pi 5** (4GB or 8GB RAM recommended)
- **RPi AI Hat+** (Hailo-8L NPU)
- **Raspberry Pi Camera Module 3** (or compatible camera)
- **MicroSD Card** (32GB+ recommended, Class 10 or better)
- **Power Supply** (Official RPi 5 power supply recommended)

## 📋 Software Requirements

- **Raspberry Pi OS** (64-bit, Bookworm or later)
- **Python 3.11+**
- **heloRT Library** (Hailo Runtime Library)
- **YOLOv8 Model** (Hailo-optimized .hef format)

## 🔧 Installation

### Quick Setup (Automated)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd HailoNPU_POC
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Reboot your Raspberry Pi:**
   ```bash
   sudo reboot
   ```

### Manual Installation

1. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt install -y python3-dev python3-pip python3-venv cmake build-essential
   sudo apt install -y libopencv-dev libavcodec-dev libavformat-dev libswscale-dev
   sudo apt install -y python3-picamera2 libcamera-apps libcamera-dev
   ```

3. **Enable camera interface:**
   ```bash
   sudo raspi-config nonint do_camera 0
   ```

4. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Install heloRT library:**
   ```bash
   # Download heloRT wheel from Hailo's official repository
   pip install heloRT-*.whl
   ```

### Model Setup

1. **Download YOLOv8 Hailo model:**
   - Visit [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo)
   - Download `yolov8n.hef` or convert your own model
   - Place the model file in the project directory

2. **Alternative: Use fallback CPU inference:**
   - The system automatically falls back to CPU-based inference if Hailo model is not available
   - This provides basic functionality for testing

## 🚀 Usage

### Start the System

1. **Manual start:**
   ```bash
   ./start.sh
   ```

2. **Using systemd service:**
   ```bash
   sudo systemctl start rpi-object-detection
   sudo systemctl enable rpi-object-detection  # Enable auto-start
   ```

3. **Check service status:**
   ```bash
   sudo systemctl status rpi-object-detection
   ```

### Access the Web Interface

1. **Local access:**
   - Open browser: `http://localhost:5000`

2. **Remote access:**
   - Find RPi IP address: `hostname -I`
   - Open browser: `http://[RPi-IP]:5000`

3. **Features available:**
   - Live video stream with object detection
   - Real-time performance metrics
   - System status monitoring
   - Fullscreen video viewing

## 📊 Configuration

Edit `config.py` to customize system behavior:

```python
# Camera settings
CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 30

# Model settings
MODEL_PATH = "yolov8n.hef"
CONFIDENCE_THRESHOLD = 0.5

# Web server settings
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
```

## 🔍 Monitoring and Logs

1. **View real-time logs:**
   ```bash
   journalctl -u rpi-object-detection -f
   ```

2. **View application logs:**
   ```bash
   tail -f object_detection.log
   ```

3. **Check system performance:**
   ```bash
   htop
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Camera not detected:**
   ```bash
   # Check camera connection
   libcamera-hello --list-cameras
   
   # Enable camera interface
   sudo raspi-config nonint do_camera 0
   ```

2. **heloRT library not found:**
   ```bash
   # Install heloRT manually
   pip install heloRT-*.whl
   
   # Check installation
   python -c "import heloRT; print('heloRT installed successfully')"
   ```

3. **Low FPS performance:**
   - Reduce camera resolution in `config.py`
   - Lower confidence threshold
   - Ensure adequate power supply
   - Check system temperature: `vcgencmd measure_temp`

4. **Web interface not accessible:**
   ```bash
   # Check if service is running
   sudo systemctl status rpi-object-detection
   
   # Check port availability
   sudo netstat -tulpn | grep :5000
   ```

### Performance Optimization

1. **GPU memory split:**
   ```bash
   # Add to /boot/config.txt
   gpu_mem=128
   ```

2. **Increase swap space:**
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

3. **CPU governor:**
   ```bash
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

## 📁 Project Structure

```
HailoNPU_POC/
├── main.py                 # Main application script
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── setup.sh               # Automated setup script
├── start.sh               # Manual start script
├── README.md              # This file
├── templates/
│   └── index.html         # Web interface template
├── static/                # Static web assets (auto-created)
├── logs/                  # Log files (auto-created)
└── models/                # Model files (create manually)
    └── yolov8n.hef       # Hailo-optimized YOLOv8 model
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on actual hardware
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🙏 Acknowledgments

- [Hailo AI](https://hailo.ai/) for the AI Hat+ and heloRT library
- [Raspberry Pi Foundation](https://www.raspberrypi.org/) for the excellent hardware
- [Ultralytics](https://ultralytics.com/) for the YOLOv8 model
- [OpenCV](https://opencv.org/) for computer vision tools

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on the project repository
4. Consult the official documentation for heloRT and Raspberry Pi

---

**Note**: This system requires the heloRT library and YOLOv8 Hailo model to achieve optimal performance. The system will work with CPU-only inference as a fallback, but hardware acceleration provides significant performance improvements.
