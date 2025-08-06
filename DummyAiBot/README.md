# DummyAiBot - Pure Simulation Bot Agent

A purely simulated AI bot agent designed for testing communication and task execution with an Orchestrator Agent. This implementation contains **NO HARDWARE CODE** and runs entirely in simulation mode for safe testing.

## Features

- **Pure Simulation**: No hardware dependencies or actual robot control
- **WebSocket Communication**: Connects to Orchestrator Agent via WebSocket
- **Task Execution**: Receives and executes tasks from orchestrator (simulated)
- **LLM Integration**: Uses local LLaMA 3.2:3B model via Ollama API for task analysis
- **Simulated Movement**: Virtual 4-wheel robot movement simulation
- **Simulated Camera**: Virtual pan/tilt camera control simulation
- **Modular Design**: Clean separation of concerns with proper folder structure
- **Testing Focused**: Zero hardware dependencies for safe testing environment

## Project Structure

```
DummyAiBot/
├── agents/                     # Core AI agent implementations
│   ├── dummy_bot.py            # Main bot agent
│   ├── llm_service.py          # LLM integration service
│   └── __init__.py
├── communication/              # Communication protocols
│   ├── protocol.py             # Message protocol definitions
│   ├── orchestrator_client.py  # WebSocket client
│   └── __init__.py
├── config/                     # Configuration files
│   ├── settings.py             # Bot configuration
│   └── __init__.py
├── controllers/                # Hardware simulation controllers
│   ├── movement_controller.py  # Movement simulation
│   ├── camera_controller.py    # Camera simulation
│   └── __init__.py
├── logs/                       # Log files directory
├── main.py                     # Main entry point
├── test_dummy_bot.py          # Component testing script
├── requirements.txt           # Python dependencies
├── setup.sh                   # Linux/Mac setup script
├── setup.ps1                  # Windows PowerShell setup script
└── README.md                  # This file
```

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running (optional for LLM features)
- LLaMA 3.2:3B model in Ollama (optional)

## Setup Instructions

### 1. Environment Setup

**For Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**For Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

**Manual Setup:**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Ollama Setup (Optional)

If you want to use LLM features:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull LLaMA 3.2:3B model
ollama pull llama3.2:3b

# Start Ollama service
ollama serve
```

### 3. Configuration

Edit `config/simple_settings.py` or use environment variables:

```bash
export BOT_ID="dummy_ai_bot_001"
export BOT_NAME="DummyAiBot"
export ORCHESTRATOR_HOST="localhost"
export ORCHESTRATOR_PORT="8080"
export OLLAMA_HOST="localhost"
export OLLAMA_PORT="11434"
```

## Usage

### Run Component Tests

Test individual components without orchestrator:

```bash
python test_dummy_bot.py
```

### Start the Bot Agent

```bash
python main.py
```

The bot will:
1. Initialize all components
2. Connect to the orchestrator via WebSocket
3. Register itself with capabilities
4. Listen for task requests
5. Execute tasks using simulated hardware
6. Report task completion back to orchestrator

## Supported Task Types

### Movement Tasks
- **Direction**: forward, backward, left, right
- **Parameters**: duration (seconds)
- **Example**: Move forward for 2 seconds

### Camera Tasks
- **Actions**: center, pan_left, pan_right, tilt_up, tilt_down, scan
- **Parameters**: degrees, range, steps
- **Example**: Pan camera left by 30 degrees

### Complex Tasks
- **Scan**: 360-degree scan with movement and camera
- **Patrol**: Multi-point patrol with scanning
- **Generic**: LLM-analyzed tasks with custom execution

## Communication Protocol

### Message Types
- `register`: Bot registration with orchestrator
- `task_request`: Task assignment from orchestrator
- `task_response`: Task completion/failure response
- `status_update`: Bot status updates
- `heartbeat`: Keep-alive messages

### Example Task Request
```json
{
  "message_type": "task_request",
  "message_id": "task_123",
  "data": {
    "task_id": "move_001",
    "task_type": "movement",
    "task_description": "Move forward for 3 seconds",
    "parameters": {
      "direction": "forward",
      "duration": 3.0
    }
  }
}
```

## Configuration Options

### Bot Configuration (`BotConfig`)
- `bot_id`: Unique bot identifier
- `bot_name`: Human-readable bot name
- `orchestrator_host/port`: Orchestrator connection details
- `ollama_host/port`: Ollama API connection
- `capabilities`: List of bot capabilities
- `temperature`: LLM response creativity (0.0-1.0)
- `max_tokens`: Maximum LLM response length

### Capabilities
- `movement`: 4-wheel robot movement
- `camera_control`: Pan/tilt camera control
- `task_execution`: General task execution
- `llm_reasoning`: LLM-based task analysis
- `status_reporting`: System status reporting

## Testing and Development

### Run Individual Component Tests
```bash
# Test movement controller
python -c "import asyncio; from test_dummy_bot import test_movement_controller; asyncio.run(test_movement_controller())"

# Test camera controller  
python -c "import asyncio; from test_dummy_bot import test_camera_controller; asyncio.run(test_camera_controller())"

# Test LLM service
python -c "import asyncio; from test_dummy_bot import test_llm_service; asyncio.run(test_llm_service())"
```

### Debug Mode
Set logging level to DEBUG in `config/simple_settings.py`:
```python
log_level: str = "DEBUG"
```

## Logs

All logs are written to:
- Console output (INFO level and above)
- `logs/bot.log` file (all levels)

Log rotation and cleanup should be configured based on deployment needs.

## Limitations (Pure Simulation)

- **ZERO Hardware**: All operations are completely simulated - no actual hardware control
- **No Real Sensors**: No actual sensor data (GPS, IMU, cameras, motors, servos)
- **No Physical Movement**: Robot position and movement are purely virtual
- **Instant Responses**: Tasks complete based on simulation timing, not real physics
- **No Safety Concerns**: Safe to run anywhere since no hardware is involved

## Future Enhancements

- Integration with actual hardware controllers
- Real sensor data integration
- Advanced task planning with Semantic Kernel
- Computer vision capabilities
- Multi-bot coordination
- Web-based monitoring interface

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check orchestrator is running
   - Verify host/port configuration
   - Check network connectivity

2. **LLM Service Unavailable**
   - Ensure Ollama is running: `ollama serve`
   - Verify model is installed: `ollama list`
   - Check Ollama host/port configuration

3. **Import Errors**
   - Activate virtual environment
   - Install requirements: `pip install -r requirements.txt`
   - Check Python path configuration

4. **WebSocket Connection Issues**
   - Verify orchestrator WebSocket endpoint
   - Check firewall settings
   - Enable debug logging for detailed error messages

### Debug Commands

```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Test WebSocket connection (if available)
websocat ws://localhost:8080/ws/agent

# Check Python imports
python -c "from agents.dummy_bot import DummyAiBot; print('Imports OK')"
```

## Contributing

This is a testing implementation. For production use:
1. Replace simulation controllers with actual hardware interfaces
2. Add proper error handling and recovery
3. Implement comprehensive logging and monitoring
4. Add security considerations for production deployment
5. Optimize for performance and resource usage

## License

This project is part of the RR2025 robot project. See main project license for details.
