# Robot Controller for Raspberry Pi 5

A modular Python robot controller for 4 motors and 2 servos using PCA9685 PWM driver, optimized for Raspberry Pi 5.

## 🚀 Features

- **Mecanum Wheel Control**: Full omnidirectional movement (forward/backward/strafe/diagonal/rotate)
- **Smooth Servo Control**: Professional camera movements with easing functions
- **Raspberry Pi 5 Compatible**: Direct I2C implementation without GPIO issues
- **Multiple Operation Modes**: Demo, test, camera, and interactive control
- **Modular Design**: Clean separation of motor, servo, and PWM control

## 🔧 Hardware Setup

### Motor Configuration
```python
motors = {
    "front_right": {"channel": 15, "in1": 14, "in2": 13},
    "front_left": {"channel": 4, "in1": 5, "in2": 6},
    "rear_right": {"channel": 10, "in1": 12, "in2": 11},
    "rear_left": {"channel": 9, "in1": 7, "in2": 8},
}
```

### Servo Configuration
```python
servos = {
    "camera_tilt": 3,
    "camera_pan": 2,
}
```

## 📦 Installation

### Quick Setup
```bash
# Clone and navigate to project
cd /home/spark/RR2025/Motors_Servo_POC

# Run automated setup
./setup.sh

# Or manual setup:
sudo apt update && sudo apt install python3-pip python3-venv i2c-tools
sudo raspi-config nonint do_i2c 0  # Enable I2C
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Verify Hardware
```bash
i2cdetect -y 1  # Should show PCA9685 at address 0x40
```

## 🎮 Usage

### Simple Start
```bash
./run_robot.sh --mode demo    # Demonstration of all features
./run_robot.sh --mode test    # Test all components
./run_robot.sh --mode interactive  # Manual control
./run_robot.sh --mode camera  # Camera movement test
```

### Interactive Controls
| Key | Action | Key | Action |
|-----|--------|-----|--------|
| `w/s` | Forward/Backward | `a/d` | Turn Left/Right |
| `z/x` | Strafe Left/Right | `q/e` | Pivot Left/Right |
| `u/o` | Diagonal Forward | `r/t` | Rotate CCW/CW |
| `i/k` | Camera Up/Down | `j/l` | Camera Left/Right |
| `c` | Center Camera | `n` | Stop All |

## 🛠 Technical Details

### Dependencies (Minimal Set)
- `adafruit-blinka` - CircuitPython for Pi
- `adafruit-circuitpython-busdevice` - I2C communication
- `adafruit-circuitpython-pca9685` - PWM control

### Key Components
- `main.py` - Entry point with operation modes
- `robot_controller.py` - Main orchestrator
- `motor_controller.py` - Mecanum wheel control
- `camera_pan_tilt_controller.py` - Smooth servo movements
- `pca9685_controller_simple.py` - Pi 5 compatible PWM driver

## 🔧 Troubleshooting

### Common Issues
```bash
# I2C not detected
sudo raspi-config nonint do_i2c 0
sudo reboot

# Permission issues
sudo usermod -a -G i2c,gpio $USER
logout

# Import errors
source venv/bin/activate
pip install -r requirements.txt
```

### Hardware Check
```bash
# Test I2C connection
i2cdetect -y 1

# Quick system test
./run_robot.sh --mode test
```

## 📁 Project Structure
```
Motors_Servo_POC/
├── main.py                          # Entry point
├── robot_controller.py              # Main controller
├── motor_controller.py              # Motor control
├── camera_pan_tilt_controller.py    # Servo control
├── pca9685_controller_simple.py     # PWM driver (Pi 5 compatible)
├── requirements.txt                 # Dependencies
├── run_robot.sh                     # Launch script
└── setup.sh                         # Installation script
```

## 🚀 Getting Started

1. **Connect Hardware**: PCA9685 to Pi via I2C, motors/servos to PCA9685
2. **Run Setup**: `./setup.sh`
3. **Test System**: `./run_robot.sh --mode test`
4. **Start Controlling**: `./run_robot.sh --mode interactive`

---
*Optimized for Raspberry Pi 5 - No sudo required - Clean, minimal dependencies*

**Basic Movement:**
- `w/s` - Move forward/backward
- `a/d` - Turn left/right  
- `q/e` - Pivot left/right

**Mecanum Movement:**
- `z/x` - Strafe left/right
- `u/o` - Diagonal forward-left/right
- `m/.` - Diagonal backward-left/right
- `r/t` - Rotate counter-clockwise/clockwise

**Camera Controls:**
- `i/k` - Camera up/down
- `j/l` - Camera left/right
- `c` - Center camera

**System Controls:**
- `n` - Stop all movement
- `speed=X` - Set speed (0-100)
- `status` - Show system status
- `mecanum x y rot` - Advanced control (e.g., `mecanum 50 30 -20`)
- `exit` - Exit program### Custom I2C Address
```bash
python3 main.py --i2c-address 0x41
```

## Code Structure

### Core Classes

1. **PCA9685Controller** (`pca9685_controller_gpiozero.py`)
   - Base controller for PWM driver with GPIO Zero integration
   - Channel management and PWM control
   - Raspberry Pi 5 compatibility with LGPIO
   - Resource cleanup

2. **MotorController** (`motor_controller.py`)
   - DC motor control with direction and speed
   - High-level movement functions (forward, backward, turn, pivot)
   - Individual motor control

3. **CameraPanTiltController** (`camera_pan_tilt_controller.py`)
   - SG90 servo control for camera pan and tilt
   - Camera positioning functions
   - Servo calibration and testing

4. **RobotController** (`robot_controller.py`)
   - Main controller combining motor and camera pan-tilt control
   - Autonomous behaviors and demonstration modes
   - Signal handling and cleanup

### Example Usage in Code

```python
from robot_controller import RobotController

# Hardware configuration
motors = {
    "rear_left": {"channel": 0, "in1": 1, "in2": 2},
    "rear_right": {"channel": 6, "in1": 7, "in2": 8},
    "front_left": {"channel": 5, "in1": 4, "in2": 3},
    "front_right": {"channel": 11, "in1": 10, "in2": 9},
}

servos = {
    "camera_tilt": 12,
    "camera_pan": 13,
}

# Initialize robot with camera pan-tilt control
robot = RobotController(motors, servos)

# Basic movement
robot.move_forward(speed=50, duration=2)
robot.turn_left(speed=30, duration=1)
robot.stop_movement()

# Camera pan-tilt control
robot.set_camera_position(tilt_angle=45, pan_angle=90)
robot.look_up(30)
robot.center_camera()

# Cleanup
robot.cleanup()
```

## API Reference

### Motor Control
- `move_forward(speed, duration)` - Move forward
- `move_backward(speed, duration)` - Move backward  
- `turn_left(speed, duration)` - Turn left
- `turn_right(speed, duration)` - Turn right
- `pivot_left(speed, duration)` - Pivot left
- `pivot_right(speed, duration)` - Pivot right
- `stop_movement()` - Stop all motors
- `set_motor_speed(motor_name, speed, direction)` - Control individual motor

### Mecanum Wheel Control
- `strafe_left(speed, duration)` - Strafe left
- `strafe_right(speed, duration)` - Strafe right
- `move_diagonal_forward_left(speed, duration)` - Diagonal forward-left
- `move_diagonal_forward_right(speed, duration)` - Diagonal forward-right
- `move_diagonal_backward_left(speed, duration)` - Diagonal backward-left
- `move_diagonal_backward_right(speed, duration)` - Diagonal backward-right
- `rotate_clockwise(speed, duration)` - Rotate clockwise in place
- `rotate_counterclockwise(speed, duration)` - Rotate counter-clockwise in place
- `mecanum_move(x_speed, y_speed, rotation_speed, duration)` - Advanced combined movement

### Camera Pan-Tilt Control
- `set_camera_position(tilt_angle, pan_angle)` - Set camera position
- `look_up(angle)` - Tilt camera up
- `look_down(angle)` - Tilt camera down
- `look_left(angle)` - Pan camera left
- `look_right(angle)` - Pan camera right
- `center_camera()` - Center camera
- `set_servo_angle(servo_name, angle)` - Set servo to specific angle

### System Functions
- `get_status()` - Get system status
- `demo_mode()` - Run demonstration
- `patrol_mode()` - Run patrol behavior
- `test_all_motors()` - Test all motors
- `test_all_servos()` - Test all servos
- `cleanup()` - Clean up resources

## Troubleshooting

1. **I2C Communication Issues**:
   - Check wiring connections
   - Verify I2C is enabled: `sudo raspi-config`
   - Check device address: `i2cdetect -y 1`

2. **Motor Not Working**:
   - Check power supply to motors
   - Verify motor driver connections
   - Test individual channels

3. **Servo Not Responding**:
   - Check servo power supply (5V)
   - Verify PWM frequency (50Hz)
   - Test servo calibration

4. **Permission Errors**:
   - Run with sudo if needed
   - Check user permissions for I2C
   - Add user to i2c group: `sudo usermod -a -G i2c $USER`

## Safety Notes

- Always ensure proper power supply for motors and servos
- Use appropriate voltage levels (3.3V for Pi, 5V for servos)
- Implement emergency stops in autonomous modes
- Test individual components before full system integration
- Keep motors and servos within their rated specifications

## License

This project is open source. Feel free to modify and distribute according to your needs.
