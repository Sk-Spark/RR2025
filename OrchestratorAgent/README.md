# 🤖 Orchestrator Agent - AI Multi-Agent System

A sophisticated Python-based orchestrator using Microsoft's Semantic Kernel for coordinating multiple AI agents on Raspberry Pi 5 systems. This orchestrator intelligently routes tasks to agents based on their capabilities and handles real-time communication via WebSockets.

## 🌟 Features

- **🧠 Intelligent Task Planning**: Uses Microsoft Semantic Kernel with local LLaMA models
- **🔄 Real-time Communication**: WebSocket-based agent communication
- **📡 Agent Management**: Dynamic agent registration and lifecycle management
- **🎯 Capability-based Routing**: Smart task assignment based on agent capabilities
- **🔍 System Monitoring**: Comprehensive logging and metrics collection
- **🚀 Scalable Architecture**: Modular design for easy extension
- **🌐 Local LLM Integration**: Works with local Ollama LLaMA 3.2:3B models
- **💾 Async Operation**: Full asynchronous operation for high performance

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │ Semantic Kernel │  │  Task Manager    │  │Agent Manager│ │
│  │    Planner      │  │                  │  │             │ │
│  └─────────────────┘  └──────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │ Ollama Client   │  │ WebSocket Server │  │Message Router│ │
│  │ (LLaMA 3.2:3B)  │  │                  │  │             │ │
│  └─────────────────┘  └──────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
              │                    │                    │
              ▼                    ▼                    ▼
     ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
     │ Movement    │      │ Camera      │      │ Sensor      │
     │ Agent       │      │ Agent       │      │ Agent       │
     │ (RPI 5)     │      │ (RPI 5)     │      │ (RPI 5)     │
     └─────────────┘      └─────────────┘      └─────────────┘
```

## 📂 Project Structure

```
OrchestratorAgent/
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── .env                       # Environment configuration
├── README.md                  # This file
├── config/                    # Configuration management
│   ├── __init__.py
│   └── config.py
├── src/                       # Source code
│   ├── __init__.py
│   ├── orchestrator.py        # Main orchestrator class
│   ├── core/                  # Core data models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── agents/                # Agent and task management
│   │   ├── __init__.py
│   │   ├── agent_manager.py
│   │   └── task_manager.py
│   ├── communication/         # WebSocket communication
│   │   ├── __init__.py
│   │   ├── websocket_server.py
│   │   └── message_router.py
│   ├── integrations/          # External service integrations
│   │   ├── __init__.py
│   │   └── ollama_client.py
│   ├── planner/              # Semantic Kernel planning
│   │   ├── __init__.py
│   │   └── semantic_kernel_planner.py
│   └── utils/                # Utilities and helpers
│       ├── __init__.py
│       ├── logging_utils.py
│       └── helpers.py
└── logs/                     # Log files (created at runtime)
```

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**: Python 3.8+ with virtual environment
2. **Ollama Service**: Local Ollama installation with LLaMA 3.2:3B model
3. **Raspberry Pi 5**: Running agents with network connectivity

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd /home/spark/RR2025/OrchestratorAgent
   ```

2. **Activate the Python virtual environment**:
   ```bash
   source /home/spark/.venv/bin/activate
   ```

3. **Install dependencies** (if needed):
   ```bash
   /home/spark/.venv/bin/python -m pip install -r requirements.txt
   ```

4. **Configure environment** (edit `.env` if needed):
   ```bash
   # Check current configuration
   cat .env
   ```

5. **Ensure Ollama is running** with LLaMA model:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Pull LLaMA model if not available
   ollama pull llama3.2:3b
   ```

### Running the Orchestrator

```bash
# Start the orchestrator
/home/spark/.venv/bin/python main.py
```

You should see output like:
```
============================================================
🤖 ORCHESTRATOR AGENT STARTED SUCCESSFULLY! 🤖
============================================================
📡 WebSocket Server: ws://0.0.0.0:8080
🧠 Ollama Model: llama3.2:3b
🔗 Ollama URL: http://localhost:11434
============================================================
💡 The orchestrator is ready to accept agent connections and tasks!
📝 Check the logs/ directory for detailed operation logs.
🛑 Press Ctrl+C to stop the orchestrator gracefully.
============================================================
```

## 🔧 Configuration

The orchestrator uses environment variables for configuration. Key settings in `.env`:

```bash
# Debug and Logging
DEBUG=True
LOG_LEVEL=INFO

# WebSocket Configuration
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8080
MAX_CONNECTIONS=10

# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.2:3b

# Timeouts
AGENT_REGISTRATION_TIMEOUT=30
AGENT_HEARTBEAT_INTERVAL=10
TASK_EXECUTION_TIMEOUT=60
```

## 📡 Agent Communication Protocol

### Agent Registration
```json
{
  "message_type": "register_agent",
  "sender_id": "movement_agent_001",
  "payload": {
    "agent": {
      "agent_id": "movement_agent_001",
      "name": "Movement Controller",
      "agent_type": "movement",
      "capabilities": [
        {
          "name": "move_forward",
          "description": "Move robot forward",
          "category": "movement",
          "parameters": {"distance": "float", "speed": "float"}
        }
      ]
    }
  }
}
```

### Task Assignment Response
```json
{
  "message_type": "task_assignment",
  "sender_id": "orchestrator",
  "recipient_id": "movement_agent_001",
  "payload": {
    "task": {
      "task_id": "task_12345",
      "name": "Move Forward 2 meters",
      "description": "Move the robot forward by 2 meters at normal speed",
      "capability_required": "move_forward",
      "parameters": {"distance": 2.0, "speed": 1.0}
    }
  }
}
```

### Heartbeat
```json
{
  "message_type": "heartbeat",
  "sender_id": "movement_agent_001",
  "payload": {
    "agent_id": "movement_agent_001",
    "status": "online",
    "cpu_usage": 25.5,
    "memory_usage": 45.2,
    "active_tasks": ["task_12345"]
  }
}
```

## 🧠 Using the Semantic Kernel Planner

The orchestrator uses Microsoft Semantic Kernel for intelligent task planning:

### Creating Tasks from Natural Language
```python
# Example: User says "Move the robot forward and take a picture"
task_id = await orchestrator.create_task_from_user_input(
    user_input="Move the robot forward and take a picture",
    priority=7
)
```

The planner will:
1. Analyze the request using LLaMA
2. Identify required capabilities (movement + camera)
3. Find suitable agents
4. Create optimized execution plan
5. Assign tasks to best available agents

### Capability-Based Routing
The system automatically routes tasks based on agent capabilities:
- **Movement tasks** → Movement agents
- **Camera tasks** → Camera agents  
- **Sensor tasks** → Sensor agents
- **Complex tasks** → Multi-agent coordination

## 📊 Monitoring and Logs

### Log Files
- `logs/orchestrator.log` - Main system logs
- `logs/orchestrator_errors.log` - Error logs only

### System Status
The orchestrator provides real-time system status including:
- Connected agents and their status
- Pending and active tasks
- System performance metrics
- Agent capability distribution

### WebSocket Monitoring
Monitor WebSocket connections:
```bash
# Check active connections
curl http://localhost:8080/status  # If status endpoint is implemented
```

## 🛠️ Development and Extension

### Adding New Agent Types

1. **Define capabilities** in your agent:
   ```python
   capabilities = [
       AgentCapability(
           name="custom_action",
           description="Performs custom action",
           category="custom",
           parameters={"param1": "string", "param2": "int"}
       )
   ]
   ```

2. **Register with orchestrator** via WebSocket
3. **Handle task assignments** in your agent
4. **Send progress updates** and results

### Extending the Planner

1. **Add custom plugins** to Semantic Kernel:
   ```python
   # In semantic_kernel_planner.py
   custom_plugin = CustomTaskPlugin()
   self.kernel.add_plugin(custom_plugin, "custom")
   ```

2. **Implement new planning strategies**
3. **Add domain-specific knowledge**

### Adding New Integrations

1. **Create integration class** in `src/integrations/`
2. **Implement async interface**
3. **Add to orchestrator initialization**
4. **Update configuration as needed**

## 🔍 Troubleshooting

### Common Issues

1. **Orchestrator won't start**:
   ```bash
   # Check Python environment
   /home/spark/.venv/bin/python --version
   
   # Check dependencies
   /home/spark/.venv/bin/python -c "import semantic_kernel; print('SK OK')"
   ```

2. **Ollama connection failed**:
   ```bash
   # Check Ollama service
   systemctl status ollama  # If using systemd
   curl http://localhost:11434/api/tags
   
   # Check model availability
   ollama list
   ```

3. **Agents can't connect**:
   ```bash
   # Check WebSocket server
   netstat -tlnp | grep 8080
   
   # Test WebSocket connection
   wscat -c ws://localhost:8080
   ```

4. **Tasks not being assigned**:
   - Check agent capabilities match task requirements
   - Verify agents are online and not busy
   - Review orchestrator logs for planning errors

### Log Analysis
```bash
# Follow real-time logs
tail -f logs/orchestrator.log

# Search for errors
grep ERROR logs/orchestrator.log

# Check agent connections
grep "CONNECTION_ESTABLISHED" logs/orchestrator.log

# Monitor task execution
grep "TASK_EXECUTION" logs/orchestrator.log
```

## 🤝 Contributing

1. **Follow the modular structure**
2. **Add comprehensive logging**
3. **Include error handling**
4. **Update documentation**
5. **Test with real Raspberry Pi agents**

## 📄 License

This project is part of the RR2025 robotics system. See the main project license for details.

## 🙏 Acknowledgments

- **Microsoft Semantic Kernel** for intelligent planning capabilities
- **Ollama** for local LLM inference
- **WebSockets** for real-time communication
- **Raspberry Pi Foundation** for excellent hardware platform

---

**Ready to orchestrate your AI agents! 🎯🤖**

For questions or issues, check the logs first, then review this README. The orchestrator is designed to be robust and self-healing, but monitoring the logs will help you understand what's happening under the hood.
