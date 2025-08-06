# DummyAiBot Terminal Mode - NEW FEATURE! 🚀

## Overview

The DummyAiBot now supports **Terminal Mode** - an interactive command-line interface that allows you to control the bot directly from your terminal, perfect for testing and manual control!

## Features Added

### ✅ Real Ollama Integration
- **Uses actual Ollama service** for LLM-powered task analysis
- **Model**: LLaMA 3.2:3B via Ollama API
- **Natural language understanding** for complex commands
- **Graceful fallback** when Ollama is not available

### ✅ Terminal Mode
- **Interactive command prompt** for direct bot control
- **Two operation modes**: Orchestrator mode (original) or Terminal mode (new)
- **Rich command set** with both structured and natural language commands
- **Real-time feedback** on command execution
- **Windows compatible** (no Unicode issues)

## Usage

### Command Line Options

```bash
# Terminal Mode (NEW!)
python main.py --terminal --bot-id "my_bot"

# Orchestrator Mode (Original)
python main.py --bot-id "my_bot"

# Full options
python main.py --help
```

### Available Arguments
- `--terminal, -t`: Run in terminal mode
- `--orchestrator-url`: WebSocket URL (default: ws://localhost:8765)
- `--bot-id`: Bot identifier (default: dummy_ai_bot_001)
- `--ollama-url`: Ollama API URL (default: http://localhost:11434)
- `--ollama-model`: Ollama model (default: llama3.2:3b)

### Quick Start Scripts

```bash
# Windows PowerShell
./start_terminal.ps1

# Python script
python start_terminal.py
```

## Terminal Mode Commands

### System Commands
- `help` - Show available commands
- `status` - Display bot status
- `quit`/`exit`/`q` - Exit the bot

### Movement Commands (Simulated)
- `move forward [seconds]` - Move forward (default 1s)
- `move backward [seconds]` - Move backward (default 1s)  
- `turn left [seconds]` - Turn left (default 0.5s)
- `turn right [seconds]` - Turn right (default 0.5s)

### Camera Commands (Simulated)
- `camera center` - Center camera
- `camera pan left [degrees]` - Pan camera left
- `camera pan right [degrees]` - Pan camera right
- `camera tilt up [degrees]` - Tilt camera up
- `camera tilt down [degrees]` - Tilt camera down
- `camera scan [range] [steps]` - Scan area

### Complex Tasks
- `scan area` - Perform 360° scan
- `patrol [points] [duration]` - Patrol with N points

### Natural Language (Powered by Ollama!)
- `look around and then move forward`
- `scan the area for 30 seconds`
- `patrol the perimeter`
- Any natural language description!

## Example Session

```
** DUMMY AI BOT - TERMINAL MODE **
============================================================
Bot is now ready to accept commands from terminal!
Type 'help' for available commands or 'quit' to exit.
============================================================

Bot > status
BOT STATUS:
Bot ID: terminal_bot_001
Status: ready
Current Task: None
Movement Status: ready
Camera Status: ready

Bot > move forward 2
Processing: move forward 2
Movement completed: SIMULATED forward movement
New position: {'x': 0, 'y': 2.0, 'heading': 0}

Bot > look around carefully
Analyzing command with LLM...
LLM Analysis: camera task
Understanding: Pan camera left and right to scan surroundings
Task completed successfully!
Actions taken: simulated_camera_centered

Bot > quit
Shutting down bot...
```

## Configuration

The bot now supports terminal mode configuration in `config/settings.py`:

```python
@dataclass
class BotConfig:
    # Operation mode
    terminal_mode: bool = False  # Set to True for terminal mode
    
    # Ollama/LLM configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
```

## Technical Details

### Orchestrator Client Handling
- **Conditional initialization**: Only creates orchestrator client when not in terminal mode
- **Graceful degradation**: All orchestrator-dependent features skip safely in terminal mode
- **No network dependencies**: Terminal mode works completely offline (except for Ollama)

### LLM Integration
- **Real API calls** to Ollama service at `localhost:11434`
- **Model verification** ensures LLaMA 3.2:3B is available
- **Fallback behavior** when Ollama is unavailable
- **Natural language parsing** for complex task understanding

### Error Handling
- **Windows compatibility** - no Unicode encoding issues
- **Graceful failures** with helpful error messages
- **Robust input handling** for malformed commands

## Benefits

1. **Easy Testing**: No need for orchestrator setup
2. **Manual Control**: Direct command execution  
3. **LLM Integration**: Real natural language understanding
4. **Development**: Perfect for debugging and development
5. **Demonstration**: Great for showing bot capabilities

## Next Steps

1. **Start Ollama**: `ollama serve` (if you want LLM features)
2. **Run Terminal Mode**: `python main.py --terminal`
3. **Try Commands**: Start with `help` and `status`
4. **Test LLM**: Try natural language commands!

This makes the DummyAiBot much more versatile and easier to test and demonstrate! 🎉
