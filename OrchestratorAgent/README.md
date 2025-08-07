# 🤖 Orchestrator Agent - AI Bot Fleet Manager

The Orchestrator Agent is a comprehensive system for managing and coordinating AI bot agents. It runs exclusively in **interactive mode** and is designed to maintain persistent connections with AI bot minions, receive scenarios from users, break them down into tasks, and assign them to available agents.

## 🎯 Overview

The Orchestrator Agent serves as a **central command center** for AI bot fleets. It maintains persistent connections to all AI bot agents, processes complex scenarios from users, intelligently breaks them down into manageable tasks, and coordinates their execution across available bot minions.

### Key Purpose
- **Maintains Connections**: Keeps persistent connections to all AI bot agents
- **Processes Scenarios**: Receives complex scenarios from users via interactive terminal
- **Breaks Down Tasks**: Intelligently breaks scenarios into executable tasks
- **Assigns Work**: Distributes tasks across available AI bot minions
- **Monitors Progress**: Tracks completion and handles failures

## 🌟 Key Features

### Interactive Mode Only
- **Simplified Operation**: No daemon mode - exclusively interactive terminal interface
- **Real-time Control**: Direct user interaction for scenario management
- **Rich Terminal Interface**: Command-line interface with comprehensive features

### Persistent Agent Connections
- **WebSocket Server**: Maintains long-running connections to all AI bot agents
- **Agent Management**: Tracks and manages connected AI bot minions
- **Health Monitoring**: Real-time status monitoring of all connected bots

### Scenario Processing
- **Natural Language Input**: Process complex scenarios in plain English
- **Intelligent Breakdown**: Uses AI planning to parse scenarios into actionable tasks
- **Sequential Execution**: Creates dependent tasks that execute in logical order
- **Task Assignment**: Automatically assigns tasks to available AI bot minions

### Real-time Monitoring
- **Live Status**: Track progress of scenarios and individual tasks
- **Agent Health**: Monitor connectivity and status of all AI bots
- **System Metrics**: Comprehensive system health and performance metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with virtual environment at `/home/spark/.venv/`
- Ollama running locally (for AI planning)
- AI bot agents (test agents provided)

### Start the Orchestrator
```bash
# Method 1: Use the startup script (recommended)
./start_interactive.sh

# Method 2: Direct execution
/home/spark/.venv/bin/python main.py

# Method 3: Using the dedicated interactive script
/home/spark/.venv/bin/python main_interactive.py
```

### Start AI Bot Agents
In separate terminals, start some test AI bot agents:
```bash
cd test_agents

# Start individual bots
/home/spark/.venv/bin/python run_test_agents.py --type aibot --id bot1
/home/spark/.venv/bin/python run_test_agents.py --type aibot --id bot2
/home/spark/.venv/bin/python run_test_agents.py --type aibot --id bot3

# Or start a full test fleet
/home/spark/.venv/bin/python run_test_agents.py --type fleet
```

## 🎮 Usage Guide

Once the orchestrator is running, you'll see the interactive terminal. Here are the key commands:

### Scenario Management (Primary Feature)
```bash
# Break down complex scenarios into tasks
scenario Navigate to kitchen, pick up the red cup, and bring it to living room
scenario Patrol the entire house and report any anomalies you find
scenario Clean the office area and organize the desk
scenario Go to living room, find the TV remote, and bring it to the couch
scenario Check all windows and doors to ensure they are properly closed
```

### System Monitoring
```bash
# Check overall system status
status

# List all connected AI bot agents
agents

# Monitor task progress and completion
tasks

# View detailed system metrics
metrics

# Show available agent capabilities
capabilities
```

### Individual Task Management
```bash
# Create a single task (for simple operations)
create Move robot forward 1 meter
create Scan the room for objects
create Turn left 90 degrees

# Execute a specific task immediately
execute task_abc123

# Cancel a running task
cancel task_abc123

# View command history
history

# Clear the terminal screen
clear

# Exit the orchestrator
exit
```

### Interactive Help
```bash
# Show all available commands and examples
help
```

## 🤖 AI Bot Architecture

### Unified AI Bot Minions
- **Identical Capabilities**: All connected agents are AI bot minions with the same capabilities
- **Capability Categories**: Movement, vision, manipulation, navigation, sensors, general tasks
- **Load Balancing**: Orchestrator automatically distributes tasks across available bots
- **Fault Tolerance**: Failed tasks can be reassigned to other available agents

### Task Assignment Logic
- **Capability Matching**: Tasks are assigned based on required capabilities
- **Agent Availability**: Only assigns to online and available agents
- **Priority Handling**: Higher priority tasks are processed first
- **Dependency Management**: Sequential tasks wait for dependencies to complete

## 📋 Scenario Examples

### Home Assistance Scenarios
```bash
scenario Go to the living room, find the TV remote, and bring it to the couch
scenario Navigate to the kitchen, check if the stove is off, and report back
scenario Find my keys in the house and bring them to the front door
```

### Security and Patrol Scenarios
```bash
scenario Patrol all rooms on the first floor and report any unusual objects
scenario Check all windows and doors to ensure they are secure
scenario Monitor the front entrance for 30 minutes and log any activity
```

### Cleaning and Organization Scenarios
```bash
scenario Vacuum the living room, then mop the kitchen floor, and organize the dining table
scenario Clean up the office desk and organize all papers into neat stacks
scenario Collect all items from the floor and place them in appropriate locations
```

### Delivery and Transport Scenarios
```bash
scenario Pick up the package from the front door and deliver it to the home office
scenario Move all books from the coffee table to the bookshelf
scenario Transport the laundry basket from the bedroom to the laundry room
```

### Investigation and Reporting Scenarios
```bash
scenario Search the entire house for a lost phone and report its location
scenario Count all the chairs in the house and provide a detailed report
scenario Inspect all plants and report which ones need watering
```

## 🏗️ System Architecture

### Core Components

1. **Orchestrator Core** (`src/orchestrator.py`)
   - Main coordination logic with scenario processing
   - Component lifecycle management
   - System status and metrics collection

2. **Terminal Interface** (`src/interfaces/terminal_interface.py`)
   - Interactive command processing with scenario commands
   - Real-time status display and user feedback
   - Rich command-line interface for fleet management

3. **Agent Manager** (`src/agents/agent_manager.py`)
   - AI bot registration and discovery
   - Capability tracking and health monitoring
   - Agent-to-task matching and assignment

4. **Task Manager** (`src/agents/task_manager.py`)
   - Task lifecycle management and queue processing
   - Scenario breakdown and dependency tracking
   - Execution monitoring and completion handling

5. **Communication Layer** (`src/communication/`)
   - WebSocket server for persistent agent connections
   - Message routing and protocol handling
   - Real-time bidirectional communication

6. **AI Planning** (`src/planner/`)
   - Semantic Kernel integration for intelligent planning
   - Scenario analysis and task breakdown
   - Capability matching and execution optimization

### Communication Flow
```
User Scenario → Terminal Interface → Orchestrator Core → Task Manager
                     ↑                                        ↓
               Status Updates ← Message Router ← WebSocket ← AI Bot Agents
```

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)
```yaml
websocket:
  host: "localhost"
  port: 8765

ollama:
  base_url: "http://localhost:11434"
  model: "llama3.1"

logging:
  level: "INFO"
  directory: "logs"

task_management:
  default_timeout: 300
  max_concurrent_tasks: 10
```

### Environment Setup
- **Virtual Environment**: Uses `/home/spark/.venv/`
- **Python Version**: Requires Python 3.8+
- **Dependencies**: All required packages included in venv

## 📊 Monitoring and Logging

### Real-time Monitoring
- **Live Status**: Use `status` command for live system metrics
- **Task Tracking**: Use `tasks` command to monitor scenario progress
- **Agent Health**: Use `agents` command to check AI bot connectivity
- **Performance Metrics**: Use `metrics` command for detailed statistics

### Comprehensive Logging
- **Operation Logs**: `logs/orchestrator.log` - Main system operations
- **Task Execution**: `logs/task_execution.log` - Detailed task tracking
- **Semantic Kernel**: `logs/semantic_kernel.log` - AI planning events
- **WebSocket Communication**: Message routing and agent communication

### Available Metrics
- Total/online/offline AI bot agents
- Pending/active/completed/failed tasks
- System uptime and performance statistics
- Task assignment efficiency and completion rates

## 🛠️ Development and Testing

### Project Structure
```
OrchestratorAgent/
├── main.py                     # Main entry point (interactive mode only)
├── main_interactive.py         # Dedicated interactive mode launcher
├── start_interactive.sh        # Quick startup script
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
├── config/                     # Configuration management
│   ├── __init__.py
│   └── config.py
├── src/                        # Core source code
│   ├── __init__.py
│   ├── orchestrator.py         # Main orchestrator with scenario processing
│   ├── core/                   # Core models and data structures
│   ├── agents/                 # Agent and task management
│   ├── communication/          # WebSocket communication layer
│   ├── interfaces/             # Terminal interface implementation
│   ├── planner/                # AI planning and scenario breakdown
│   └── utils/                  # Utilities and logging
├── test_agents/                # Test AI bot agents for development
│   ├── run_test_agents.py      # Test agent runner
│   ├── aibot_agent.py          # AI bot implementation
│   └── test_agent_manager.py   # Test fleet management
└── logs/                       # System logs (created at runtime)
```

### Running Tests
```bash
# Test the orchestrator help system
/home/spark/.venv/bin/python main.py --help

# Test agent connectivity (in separate terminals)
cd test_agents
/home/spark/.venv/bin/python run_test_agents.py --list
/home/spark/.venv/bin/python run_test_agents.py --type aibot --id test_bot
```

### Creating Custom AI Bot Agents

Agents must implement the standard WebSocket protocol:

```python
import asyncio
import json
import websockets

async def connect_to_orchestrator():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Register as AI bot agent
        registration = {
            "type": "agent_registration",
            "payload": {
                "agent_id": "my_aibot",
                "name": "My AI Bot",
                "capabilities": ["movement", "vision", "manipulation"]
            }
        }
        await websocket.send(json.dumps(registration))
        
        # Handle incoming tasks
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "task_assignment":
                # Process task and send updates
                task = data["payload"]["task"]
                await handle_task(websocket, task)

async def handle_task(websocket, task):
    # Send task started update
    update = {
        "type": "task_update",
        "payload": {
            "task_id": task["task_id"],
            "status": "in_progress",
            "message": "Task execution started"
        }
    }
    await websocket.send(json.dumps(update))
    
    # Simulate task execution
    await asyncio.sleep(5)
    
    # Send completion update
    result = {
        "type": "task_result",
        "payload": {
            "task_id": task["task_id"],
            "status": "completed",
            "result": {"status": "success"},
            "message": "Task completed successfully"
        }
    }
    await websocket.send(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(connect_to_orchestrator())
```

## 🚨 Troubleshooting

### Common Issues

1. **"No AI bot agents connected"**
   - Start test agents: `cd test_agents && /home/spark/.venv/bin/python run_test_agents.py --type aibot --id bot1`
   - Check WebSocket server is running on port 8765

2. **"Task manager not available"**
   - Restart the orchestrator: `/home/spark/.venv/bin/python main.py`
   - Check logs in `logs/` directory

3. **"Failed to break down scenario into tasks"**
   - Ensure Ollama is running: `ollama serve`
   - Check if LLaMA model is available: `ollama list`
   - Verify network connectivity to Ollama

4. **Tasks not executing**
   - Check that agents have required capabilities: `agents` command
   - Verify agent connectivity: `status` command
   - Review task assignments: `tasks` command

### Debug Commands
```bash
# Check system status
status

# List connected agents
agents

# View system metrics
metrics

# Show command history
history
```

### Log Analysis
```bash
# View main orchestrator logs
tail -f logs/orchestrator.log

# Monitor task execution
tail -f logs/task_execution.log

# Check AI planning logs
tail -f logs/semantic_kernel.log
```

## 🎯 Use Cases

### Smart Home Management
- Room-by-room cleaning and organization
- Security patrols and monitoring
- Object finding and retrieval
- Environmental monitoring

### Office Automation
- Document organization and filing
- Equipment monitoring and maintenance
- Visitor assistance and guidance
- Inventory tracking and reporting

### Research and Development
- Multi-agent coordination testing
- Scenario-based automation research
- AI planning and execution studies
- Human-robot interaction experiments

## 🔮 Future Enhancements

### Planned Features
- **Advanced Scenario Parsing**: More sophisticated natural language understanding
- **Multi-Agent Coordination**: Complex scenarios requiring multiple bots working together
- **Learning and Adaptation**: AI bots that learn from scenario execution patterns
- **Voice Interface**: Voice command integration for scenario input
- **Mobile Control**: Web or mobile app interface for remote scenario management

### Extensibility
- **Plugin Architecture**: Custom capability plugins for specialized tasks
- **External Integrations**: Integration with smart home systems, IoT devices
- **Custom Planners**: Alternative AI planning strategies and models
- **Scenario Templates**: Pre-defined scenario templates for common use cases

## 📄 License

This project is part of the RR2025 repository and follows the project's licensing terms.

## 🆘 Support

For issues, questions, or contributions:
1. Check the logs in `logs/` directory for error details
2. Use the `help` command in the interactive interface
3. Test with the provided test agents in `test_agents/`
4. Review the troubleshooting section above

---

**🎯 Ready to manage your AI bot fleet!** Start the orchestrator and begin coordinating scenarios across your AI bot minions.
