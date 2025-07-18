# Robot Controller for RPi 5 with PCA9685

A modular Python robot controller for controlling 4 BO motors and 2 SG90 servos using a PCA9685 16-channel 12-bit PWM driver connected to a Raspberry Pi 5.

## Features

- **Modular Design**: Separate classes for PCA9685, motor control, and servo control
- **GPIO Zero Integration**: Uses gpiozero library with LGPIO for Raspberry Pi 5 compatibility
- **4 BO Motor Control**: Independent control of 4 DC motors with direction and speed
- **2 SG90 Servo Control**: Precise angle control for camera tilt and pan
- **High-Level Robot Functions**: Movement patterns, camera positioning, and autonomous modes
- **Safety Features**: Graceful shutdown, error handling, and resource cleanup
- **Multiple Operation Modes**: Demo, patrol, test, and interactive modes

## Hardware Configuration

### Motors (Connected to PCA9685)
```python
motors = {
    "rear_left": {"channel": 0, "in1": 1, "in2": 2},
    "rear_right": {"channel": 6, "in1": 7, "in2": 8},
    "front_left": {"channel": 5, "in1": 4, "in2": 3},
    "front_right": {"channel": 11, "in1": 10, "in2": 9},
}
```

### Servos (Connected to PCA9685)
```python
servos = {
    "camera_tilt": 12,
    "camera_pan": 13,
}
```

## Installation

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv i2c-tools
   ```

2. **Enable I2C on Raspberry Pi**:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options -> I2C -> Enable
   ```

3. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify I2C connection**:
   ```bash
   i2cdetect -y 1
   # Should show device at address 0x40 (or your configured address)
   ```

## Usage

### Basic Usage
```bash
python3 main.py --mode demo
```

### Available Modes

1. **Demo Mode** (default):
   ```bash
   python3 main.py --mode demo
   ```
   Demonstrates all robot capabilities including motor and servo tests.

2. **Patrol Mode**:
   ```bash
   python3 main.py --mode patrol
   ```
   Autonomous patrol with movement and camera scanning.

3. **Test Mode**:
   ```bash
   python3 main.py --mode test
   ```
   Tests all motors and servos individually.

4. **Interactive Mode**:
   ```bash
   python3 main.py --mode interactive
   ```
   Manual control via keyboard commands.

### Interactive Mode Commands
- `w/s` - Move forward/backward
- `a/d` - Turn left/right
- `q/e` - Pivot left/right
- `i/k` - Camera up/down
- `j/l` - Camera left/right
- `c` - Center camera
- `x` - Stop all movement
- `speed=X` - Set speed (0-100)
- `status` - Show system status
- `exit` - Exit program

### Custom I2C Address
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

3. **ServoController** (`servo_controller.py`)
   - SG90 servo angle control
   - Camera positioning functions
   - Servo calibration and testing

4. **RobotController** (`robot_controller.py`)
   - Main controller combining motor and servo control
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

# Initialize robot
robot = RobotController(motors, servos)

# Basic movement
robot.move_forward(speed=50, duration=2)
robot.turn_left(speed=30, duration=1)
robot.stop_movement()

# Camera control
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

### Servo Control
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
