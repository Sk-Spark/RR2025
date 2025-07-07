# Semantic Kernel LED Control with Ollama (Modular Version)

A modular Python application that uses Semantic Kernel and Ollama to control an LED on Raspberry Pi 5 via natural language commands through the terminal.

## 📁 Project Structure

```
SemanticKernal/
├── __init__.py           # Package initialization
├── main.py               # Main entry point (backward compatibility)
├── app.py                # Main application class
├── config.py             # Configuration management
├── led_controller.py     # GPIO hardware control
├── led_plugin.py         # Semantic Kernel plugin
├── ollama_agent.py       # Ollama LLM integration
├── test_modules.py       # Comprehensive test suite
├── test_led.py           # Legacy LED-only tests
├── requirements.txt      # Dependencies
├── run.sh                # Startup script
└── README.md             # This file
```

## 🏗️ Modular Architecture

### **Core Modules**

1. **`config.py`** - Configuration Management
   - `AppConfig`: Dataclass for application settings
   - `ConfigManager`: Manages configuration with environment variable support
   - Validation and error handling

2. **`led_controller.py`** - Hardware Control
   - `LEDController`: GPIO control using gpiozero
   - Error handling and simulation mode
   - Resource management and cleanup

3. **`led_plugin.py`** - Semantic Kernel Integration
   - `LEDControlPlugin`: Semantic Kernel plugin with `@kernel_function` decorators
   - Function calling interface for LLM
   - Type annotations and documentation

4. **`ollama_agent.py`** - LLM Integration
   - `OllamaLEDAgent`: Main agent coordinating LLM and LED control
   - Prompt engineering for function calling
   - Decision parsing and execution

5. **`app.py`** - Application Logic
   - `LEDControlApp`: Main application class
   - Interactive loop and user interface
   - Error handling and resource management

6. **`main.py`** - Entry Point
   - Simple entry point for backward compatibility
   - Initializes and runs the application

## 🔧 Key Features

### **Separation of Concerns**
- **Hardware**: Isolated in `led_controller.py`
- **AI Logic**: Contained in `ollama_agent.py`
- **Configuration**: Centralized in `config.py`
- **User Interface**: Managed in `app.py`

### **Configurable**
- Environment variable support
- Validation and error handling
- Easy to extend with new settings

### **Testable**
- Each module can be tested independently
- Comprehensive test suite in `test_modules.py`
- Integration tests included

### **Extensible**
- Easy to add new hardware controls
- Plugin system for new LLM functions
- Configuration-driven customization

## 🚀 Usage

### **Quick Start**
```bash
# Using the startup script
./run.sh

# Or manually
source env/bin/activate
python main.py
```

### **Custom Configuration**
```bash
# Set environment variables
export LED_PIN=22
export OLLAMA_MODEL=llama3.2:3b
export LOG_LEVEL=DEBUG

python main.py
```

### **Using as a Module**
```python
from app import LEDControlApp
from config import AppConfig, ConfigManager

# Custom configuration
config = AppConfig(led_pin=22, model_name="llama3.2:3b")
config_manager = ConfigManager(config)

# Run the application
app = LEDControlApp(config_manager)
await app.run()
```

## 🧪 Testing

### **Test All Modules**
```bash
python test_modules.py
```

### **Test Individual Components**
```bash
# Test LED controller only
python -c "from led_controller import LEDController; c = LEDController(); c.turn_on()"

# Test configuration
python -c "from config import ConfigManager; print(ConfigManager().get_config())"
```

## 📋 Configuration Options

### **Environment Variables**
| Variable | Default | Description |
|----------|---------|-------------|
| `LED_PIN` | `18` | GPIO pin for LED |
| `OLLAMA_MODEL` | `llama3.2:1b` | Ollama model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `TIMEOUT_SECONDS` | `30` | Operation timeout |

### **Programmatic Configuration**
```python
from config import AppConfig

config = AppConfig(
    led_pin=22,
    model_name="llama3.2:3b",
    base_url="http://localhost:11434",
    log_level="DEBUG"
)
```

## � Hardware Setup

1. **Connect LED to GPIO pin 18** (or configured pin)
2. **Use 220Ω resistor** in series with LED
3. **Connect to ground** through resistor

## 📝 Adding New Features

### **New Hardware Control**
1. Create controller class in new file (e.g., `buzzer_controller.py`)
2. Create plugin class (e.g., `buzzer_plugin.py`)
3. Add to `ollama_agent.py` initialization
4. Update prompts to include new functions

### **New Configuration Options**
1. Add to `AppConfig` dataclass in `config.py`
2. Update environment variable parsing
3. Add validation if needed

### **New Commands**
1. Add `@kernel_function` to appropriate plugin
2. Update LLM prompts to include new function
3. Test with `test_modules.py`

## 🛠️ Development

### **Code Style**
- Type hints for all functions
- Comprehensive docstrings
- Logging for debugging
- Error handling with meaningful messages

### **Testing**
- Unit tests for each module
- Integration tests for component interaction
- Hardware simulation for CI/CD

### **Documentation**
- Each module has comprehensive docstrings
- README files for complex components
- Usage examples and tutorials

## 🔍 Troubleshooting

### **Module Import Errors**
- Ensure you're in the correct directory
- Check virtual environment activation
- Verify all dependencies are installed

### **GPIO Permission Errors**
- Run with `sudo` if necessary
- Add user to `gpio` group
- Check hardware connections

### **Ollama Connection Issues**
- Verify Ollama is running: `ollama serve`
- Check model availability: `ollama list`
- Verify base URL in configuration

## 📊 Benefits of Modular Design

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Components can be tested in isolation
3. **Reusability**: Modules can be used in other projects
4. **Scalability**: Easy to add new features without affecting existing code
5. **Debugging**: Issues can be isolated to specific modules
6. **Documentation**: Each module is self-contained and well-documented

This modular architecture makes the LED control system highly maintainable, extensible, and professional-grade!
