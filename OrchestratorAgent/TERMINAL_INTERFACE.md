# Orchestrator Agent Terminal Interface

The Orchestrator Agent now includes an interactive terminal interface that allows users to control and monitor the system through command-line commands.

## Getting Started

### Running with Terminal Interface

There are several ways to start the orchestrator with terminal interface:

```bash
# Activate virtual environment first
source /home/spark/.venv/bin/activate

# Method 1: Using the main script with interactive flag
python main.py --interactive
# or
python main.py -i

# Method 2: Using the dedicated interactive script
python main_interactive.py

# Method 3: Using the demo script (includes help text)
python demo_terminal.py
```

### Running in Daemon Mode (Original)

For background operation without terminal interface:

```bash
python main.py
```

## Available Commands

### System Management
- `help` - Show all available commands and examples
- `status` - Display current system status (agents, tasks, uptime)
- `metrics` - Show detailed system metrics and statistics
- `clear` - Clear the terminal screen
- `exit` / `quit` - Exit the terminal interface gracefully

### Agent Management
- `agents` - List all registered agents and their capabilities
- `capabilities` - Show all available agent capabilities

### Task Management
- `tasks` - List all tasks by status (pending, running, completed, failed)
- `create <description>` - Create a new task from natural language description
- `execute <task_id>` - Force execution of a specific task
- `cancel <task_id>` - Cancel a running task
- `orchestrate <description>` - Create complex multi-agent orchestration

### Monitoring
- `history` - Show command history
- `orchestrate` - View active orchestrations (if using concurrent orchestration)

## Command Examples

### Creating Tasks
```bash
orchestrator> create Move robot forward 2 meters
orchestrator> create Take a photo with camera
orchestrator> create Read temperature sensor
orchestrator> create Navigate to kitchen
```

### Complex Orchestrations
```bash
orchestrator> orchestrate Scan the entire room and create a detailed map
orchestrator> orchestrate Patrol the house and report any anomalies
orchestrator> orchestrate Collect data from all sensors and generate report
```

### System Monitoring
```bash
orchestrator> status
orchestrator> agents
orchestrator> tasks
orchestrator> metrics
```

## Features

### Intelligent Task Analysis
The terminal interface uses the Semantic Kernel planner to:
- Analyze natural language task descriptions
- Determine required capabilities
- Find suitable agents
- Create execution plans
- Handle dependencies

### Real-time Status Updates
- Live system status monitoring
- Agent availability tracking
- Task execution progress
- Performance metrics

### Concurrent Orchestration
When using the Concurrent Orchestration Pattern:
- Multi-agent task coordination
- Dependency-aware execution
- Parallel task processing
- Intelligent resource management

### Error Handling
- Graceful error reporting
- Command validation
- System health monitoring
- Recovery suggestions

## Integration with Existing System

The terminal interface integrates seamlessly with:
- **WebSocket Server**: Continues to operate for agent connections
- **Agent Manager**: Real-time agent status and capability management
- **Task Manager**: Complete task lifecycle management
- **Semantic Kernel Planner**: AI-powered task analysis and routing
- **Ollama Integration**: LLM-powered intelligent decision making

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Terminal Interface                      │
├─────────────────────────────────────────────────────────┤
│                   Orchestrator                         │
├─────────────────┬─────────────────┬─────────────────────┤
│  Agent Manager  │  Task Manager   │ Semantic Kernel     │
├─────────────────┼─────────────────┼─────────────────────┤
│ WebSocket Server│ Message Router  │ Ollama Integration  │
└─────────────────┴─────────────────┴─────────────────────┘
```

## Configuration

The terminal interface uses the same configuration as the main orchestrator:
- WebSocket settings for agent communication
- Ollama configuration for AI capabilities
- Semantic Kernel settings for intelligent planning
- Logging configuration for debugging

## Advanced Usage

### Batch Commands
You can chain commands or use the interface programmatically:

```bash
# Example of complex workflow
orchestrator> status
orchestrator> create Initialize robot systems
orchestrator> agents
orchestrator> orchestrate Perform morning patrol routine
orchestrator> metrics
```

### Development and Testing
The terminal interface is perfect for:
- Testing agent capabilities
- Debugging task execution
- Monitoring system performance
- Developing new orchestration patterns

## Troubleshooting

### Common Issues

1. **No agents available**
   - Check agent connections with `agents` command
   - Verify WebSocket server status with `status`
   - Ensure agents are running and connected

2. **Task creation fails**
   - Check system status with `status`
   - Verify Ollama service is running
   - Check available capabilities with `capabilities`

3. **Terminal interface unresponsive**
   - Use Ctrl+C to interrupt current operation
   - Use `exit` command to quit gracefully
   - Check logs directory for error details

### Debug Mode
For detailed debugging, check the logs directory:
```bash
tail -f logs/orchestrator.log
tail -f logs/semantic_kernel.log
```

## Future Enhancements

Planned improvements:
- Command auto-completion
- Colorized output
- Interactive task progress bars
- Real-time log streaming
- Voice command support
- Web-based terminal interface
