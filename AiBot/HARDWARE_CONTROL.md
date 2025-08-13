# AiBot - Hardware Control Documentation

## Overview
AiBot is an intelligent robot control system designed for Raspberry Pi 5 with real hardware control capabilities. The system uses Ollama LLM with Semantic Kernel for natural language command processing and direct hardware control.

## Key Changes Made

### 1. System Prompt Update
Updated the system prompt in the Ollama agent to:
```
"You are a robot control assistant. You are responsible for using the available functions to complete the task provided by user."
```

### 2. Removed Simulation Logic
- Eliminated all `is_simulated` flags and simulation logic
- Hardware controllers now either work with real hardware or report errors
- No more mock/simulation behavior for sensor data or movement

### 3. Enhanced Error Handling
- LED Controller: Clear error messages when hardware is unavailable
- PCA9685 Controller: Proper hardware availability checking
- Movement Plugin: Detailed execution feedback with success/failure reporting

### 4. Hardware Requirements
- **Target Platform**: Raspberry Pi 5
- **Python Environment**: `/home/spark/.venv` (virtual environment)
- **GPIO Control**: gpiozero library for LED control
- **PWM Control**: PCA9685 with Adafruit CircuitPython libraries
- **I2C/SPI**: Hardware interfaces enabled

## Hardware Setup

### Prerequisites
1. Raspberry Pi 5 with enabled I2C and GPIO interfaces
2. LED connected to GPIO pin 18
3. PCA9685 PWM controller for motor control
4. Mecanum wheels connected via PCA9685

### Installation
```bash
# Run the setup script
./setup_hardware.sh

# Or manually:
source /home/spark/.venv/bin/activate
pip install -r requirements.txt
```

### Dependencies
- **semantic-kernel>=1.0.0**: AI framework
- **gpiozero>=1.6.2**: GPIO control
- **ollama>=0.1.0**: LLM integration
- **adafruit-circuitpython-pca9685>=3.4.0**: PWM control
- **adafruit-blinka>=8.0.0**: Hardware abstraction
- **websockets>=11.0.0**: WebSocket communication

## Available Commands

### LED Control
- `turn_led_on`: Turn on the LED
- `turn_led_off`: Turn off the LED  
- `get_led_status`: Get current LED status

### Movement Control
- `move_forward`: Move forward for 1 second
- `move_backward`: Move backward for 1 second
- `turn_left`: Turn left for 1 second
- `turn_right`: Turn right for 1 second
- `strafe_left`: Strafe left for 1 second
- `strafe_right`: Strafe right for 1 second
- `stop_robot`: Stop immediately
- `get_movement_status`: Get movement status

## Usage Modes

### Interactive Mode (Default)
```bash
python main.py
# or
python main.py --mode interactive
```

### Orchestrator Mode (WebSocket)
```bash
python main.py --mode orchestrator
```

## Architecture

### Modular Structure
```
/home/spark/RR2025/AiBot/
├── src/
│   └── aibot/
│       ├── agents/
│       │   └── ollama_agent.py      # Main AI agent
│       ├── hardware/
│       │   ├── led_controller.py    # GPIO LED control
│       │   ├── pca9685_controller.py # PWM control
│       │   └── movement_controller.py # Mecanum movement
│       ├── plugins/
│       │   ├── led_plugin.py        # LED functions
│       │   └── movement_plugin.py   # Movement functions
│       └── __init__.py
├── config/
│   └── aibot_config.py             # Configuration
├── main.py                         # Entry point
├── requirements.txt                # Dependencies
└── setup_hardware.sh              # Hardware setup
```

### Safety Features
- **Auto-Stop**: All movements stop after 1 second
- **Error Handling**: Comprehensive exception handling
- **Hardware Validation**: Checks for hardware availability
- **Speed Limiting**: Motor speeds clamped to safe ranges (0-100%)

## Error Handling

### Hardware Not Available
- LED Controller: Reports "LED hardware not available"
- PCA9685 Controller: Reports "PCA9685 hardware not available"
- Movement fails gracefully with error messages

### Command Execution
- All functions return success/failure status
- Detailed error logging
- User-friendly error messages

## Logging
- Detailed logging at INFO and ERROR levels
- Hardware initialization status
- Command execution tracking
- Error reporting

## Configuration
Edit `/home/spark/RR2025/AiBot/config/aibot_config.py`:
```python
ORCHESTRATOR_URL = "ws://localhost:8080"
AGENT_ID = "rpi5_agent"
LED_PIN = 18
OLLAMA_MODEL = "llama3.2:1b"
```

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure user is in `gpio` and `i2c` groups
2. **Module Not Found**: Run `pip install -r requirements.txt`
3. **Hardware Not Detected**: Check I2C/GPIO interfaces are enabled
4. **Ollama Connection**: Ensure Ollama server is running on localhost:11434

### Hardware Verification
```bash
# Check I2C devices
i2cdetect -y 1

# Test GPIO permissions
python3 -c "from gpiozero import LED; led = LED(18); led.on()"

# Verify PCA9685
python3 -c "import board, busio; from adafruit_pca9685 import PCA9685"
```

## Future Enhancements
- Add sensor integration (MPU6050, cameras)
- Implement path planning algorithms
- Add voice command support
- Extend to multi-robot coordination
