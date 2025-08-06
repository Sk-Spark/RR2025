# AiBot - Intelligent Robot Control System

A modular AI-powered robot control system using Semantic Kernel and Ollama LLM for natural language command processing with LED and movement control capabilities.

## Features

- **Natural Language Processing**: Uses Ollama LLM for understanding voice/text commands
- **LED Control**: GPIO-based LED control with simulation mode
- **Motor Control**: PCA9685 PWM driver for precise motor control
- **Safety Features**: 1-second auto-stop for all movements
- **Mecanum Wheels**: Support for omnidirectional movement patterns
- **WebSocket Communication**: Real-time communication capabilities
- **Modular Architecture**: Plugin-based system for easy extension

## Project Structure

```
AiBot/
├── src/aibot/                 # Main source code
│   ├── core/                  # Core application logic
│   │   ├── app.py            # Main application
│   │   └── config.py         # Configuration management
│   ├── hardware/             # Hardware controllers
│   │   ├── led_controller.py
│   │   ├── pca9685_controller.py
│   │   └── movement_controller.py
│   ├── plugins/              # Semantic Kernel plugins
│   │   ├── led_plugin.py
│   │   └── movement_plugin.py
│   ├── agents/               # AI agents
│   │   └── ollama_agent.py
│   └── communication/        # Communication protocols
│       ├── message_protocol.py
│       └── orchestrator_client.py
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── scripts/                 # Utility scripts
├── config/                  # Configuration files
├── docs/                    # Documentation
├── main.py                  # Entry point
├── setup.py                 # Package setup
└── requirements.txt         # Dependencies
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sk-Spark/RR2025.git
   cd RR2025/AiBot
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

## Hardware Requirements

- **Raspberry Pi 5** (or compatible)
- **PCA9685 PWM Driver** (I2C address 0x40)
- **Motors** with motor driver board (L298N recommended)
- **LED** connected to GPIO pin 18
- **External power supply** for motors (6-12V)

## Quick Start

1. **Start Ollama** (required for AI processing):
   ```bash
   ollama serve
   ollama pull llama3.2:1b
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Try voice commands**:
   - "turn on the LED"
   - "move forward"
   - "turn left"
   - "strafe right"
   - "stop robot"

## Movement Commands

All movement commands automatically stop after 1 second for safety:

- **move forward** / **go ahead**
- **move backward** / **go back**
- **turn left** / **turn right**
- **strafe left** / **strafe right**
- **stop robot** / **stop moving**

## Configuration

Edit `config/orchestrator_config.txt` to modify:
- Motor configurations
- PWM settings
- Communication parameters
- Safety timeouts

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Run specific test
pytest tests/integration/test_movement.py
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Hardware Testing

Use the diagnostic scripts to test hardware:

```bash
# Test hardware connections
python tests/hardware_diagnostic.py

# Test individual motors
python tests/integration/test_hardware.py

# Test movement patterns
python tests/integration/test_movement.py
```

## Architecture

### Core Components

1. **OllamaLEDAgent**: Main AI agent for command processing
2. **LEDController**: GPIO-based LED control
3. **MovementController**: Motor control with safety features
4. **PCA9685Controller**: PWM driver interface

### Plugin System

The system uses Semantic Kernel plugins for modularity:
- **LEDControlPlugin**: LED commands
- **MovementControlPlugin**: Movement commands

### Safety Features

- **Auto-stop**: All movements stop after 1 second
- **Error handling**: Graceful failure recovery
- **Hardware simulation**: Runs without physical hardware

## Troubleshooting

### Common Issues

1. **No motor movement**: Check power supply and connections
2. **Import errors**: Ensure virtual environment is activated
3. **Ollama connection**: Verify Ollama service is running
4. **Permission errors**: Check GPIO permissions on Raspberry Pi

### Hardware Diagnostics

```bash
# Test PCA9685 connection
python tests/hardware_diagnostic.py

# Check motor configurations
python tests/integration/test_poc_style.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

- **1.0.0**: Initial release with LED and movement control
- **0.9.0**: Added 1-second auto-stop safety
- **0.8.0**: Integrated Semantic Kernel plugins
- **0.7.0**: Added Ollama LLM support

## Author

**Spark** - Initial work and development

## Acknowledgments

- Semantic Kernel team for the AI framework
- Ollama team for the local LLM support
- Adafruit for the CircuitPython libraries
