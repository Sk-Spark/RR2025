# Semantic Kernel LED Control with Ollama

A Python script that uses Semantic Kernel and Ollama to control an LED on Raspberry Pi 5 via natural language commands through the terminal.

## Features

- 🤖 Natural language LED control using Ollama's llama3.2:1b model
- 🔌 GPIO control using gpiozero library
- 🧠 Semantic Kernel integration for function calling
- 🛡️ Comprehensive error handling and logging
- 🔧 Modular design for easy extension

## Hardware Requirements

- Raspberry Pi 5 with RPi AI Hat+
- LED connected to GPIO pin 18 (configurable)
- Resistor (220Ω recommended) in series with LED

## Software Requirements

- Python 3.8+
- Ollama running locally with llama3.2:1b model
- Virtual environment (recommended)

## Setup

1. **Create and activate virtual environment:**
   ```bash
   cd /home/spark/RR2025/SemanticKernal
   python3 -m venv env
   source env/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure Ollama is running:**
   ```bash
   # Start Ollama service
   ollama serve
   
   # Pull the required model (if not already available)
   ollama pull llama3.2:1b
   ```

4. **Connect LED to GPIO:**
   - Connect LED anode (+) to GPIO pin 18
   - Connect LED cathode (-) to GND through a 220Ω resistor

## Usage

1. **Activate the virtual environment:**
   ```bash
   source env/bin/activate
   ```

2. **Run the script:**
   ```bash
   python main.py
   ```

3. **Try these commands:**
   - "turn on the LED"
   - "switch on the light"
   - "turn off the LED"
   - "switch off the light"
   - "what's the LED status?"
   - "is the LED on?"
   - "quit" or "exit" to stop

## Code Structure

### Classes

- **`LEDController`**: Handles hardware GPIO control with error handling
- **`LEDControlPlugin`**: Semantic Kernel plugin that exposes LED functions
- **`OllamaLEDAgent`**: Main agent that coordinates Ollama and Semantic Kernel

### Key Features

- **Error Handling**: Graceful fallback to simulation mode if GPIO unavailable
- **Logging**: Comprehensive logging for debugging and monitoring
- **Modular Design**: Easy to extend for additional hardware control
- **Function Calling**: Uses Semantic Kernel's function calling for precise control

## Configuration

You can modify these parameters in the code:

- **GPIO Pin**: Change `led_pin` parameter in `main()` function
- **Ollama Model**: Change `model_name` in `OllamaLEDAgent` constructor
- **Ollama URL**: Change `base_url` in `OllamaLEDAgent` constructor

## Troubleshooting

1. **"gpiozero not available" warning:**
   - Install gpiozero: `pip install gpiozero`
   - The script will run in simulation mode without actual GPIO control

2. **"Failed to initialize agent" error:**
   - Ensure Ollama is running: `ollama serve`
   - Check that llama3.2:1b model is available: `ollama list`

3. **GPIO permission errors:**
   - Run with sudo if necessary: `sudo python main.py`
   - Or add user to gpio group: `sudo usermod -a -G gpio $USER`

## Example Session

```
🤖 Semantic Kernel LED Control Agent
==================================================
Commands you can try:
- 'turn on the LED' or 'switch on the light'
- 'turn off the LED' or 'switch off the light'
- 'what's the LED status?' or 'is the LED on?'
- 'quit' or 'exit' to stop
==================================================
✅ Agent initialized successfully!

Type your commands below:

🔹 You: turn on the LED
🤔 Processing...
🤖 Agent: LED has been turned on successfully

🔹 You: what's the status?
🤔 Processing...
🤖 Agent: LED is currently ON

🔹 You: switch it off
🤔 Processing...
🤖 Agent: LED has been turned off successfully

🔹 You: quit
👋 Goodbye!
```

## Extending the Code

To add more hardware controls:

1. Create a new controller class (similar to `LEDController`)
2. Create a new plugin class with `@kernel_function` decorators
3. Add the plugin to the kernel in `OllamaLEDAgent.initialize()`
4. Update the prompt template to include new functions

Example for adding a buzzer:

```python
class BuzzerController:
    def __init__(self, pin: int = 22):
        self.buzzer = Buzzer(pin)
    
    def beep(self, duration: float = 1.0):
        self.buzzer.beep(on_time=duration, off_time=0.1, n=1)

class BuzzerPlugin:
    def __init__(self, buzzer_controller):
        self.buzzer_controller = buzzer_controller
    
    @kernel_function(description="Make the buzzer beep", name="beep_buzzer")
    def beep_buzzer(self, duration: Annotated[float, "Duration in seconds"] = 1.0):
        self.buzzer_controller.beep(duration)
        return f"Buzzer beeped for {duration} seconds"
```
