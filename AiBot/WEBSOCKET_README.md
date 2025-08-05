# WebSocket Communication for RPi LED Agent

This implementation adds WebSocket communication capabilities to your RPi LED control agent, allowing it to communicate with an orchestrator agent in real-time.

## 🌟 Features

- **Real-time bidirectional communication** between RPi agent and orchestrator
- **Automatic reconnection** with configurable retry logic
- **Message queuing** for reliable delivery during disconnections
- **Heartbeat monitoring** for connection health
- **Dual mode operation** - Interactive or Orchestrator mode
- **Comprehensive message protocol** with structured message types

## 📁 New Files Added

- `message_protocol.py` - Defines the WebSocket message protocol
- `orchestrator_client.py` - WebSocket client for orchestrator communication
- `test_orchestrator.py` - Simple test orchestrator server
- `setup_websocket.sh` - Setup and usage guide script

## 🔧 Updated Files

- `app.py` - Enhanced with orchestrator integration
- `config.py` - Added orchestrator configuration options
- `requirements.txt` - Added WebSocket dependencies

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test with Local Orchestrator

**Terminal 1 - Start Test Orchestrator:**
```bash
python test_orchestrator.py
```

**Terminal 2 - Start RPi Agent in Orchestrator Mode:**
```bash
export ORCHESTRATOR_URL='ws://localhost:8080/ws'
export AGENT_ID='rpi_bedroom_led'
python main.py
```

### 3. Test Commands

From the orchestrator console, try:
```
list                              # List connected agents
cmd rpi_bedroom_led turn on LED   # Send command to agent
query rpi_bedroom_led status      # Query agent status
```

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ORCHESTRATOR_URL` | WebSocket URL of orchestrator | None (interactive mode) |
| `AGENT_ID` | Unique identifier for this agent | Auto-generated |
| `HEARTBEAT_INTERVAL` | Heartbeat interval in seconds | 30 |
| `MAX_RECONNECT_ATTEMPTS` | Max reconnection attempts | -1 (unlimited) |
| `RECONNECT_DELAY` | Delay between reconnection attempts | 5 seconds |

## 📨 Message Protocol

### Message Types
- `register` - Agent announces itself to orchestrator
- `command` - Orchestrator sends commands to agent
- `query` - Orchestrator requests information
- `response` - Agent responds to commands/queries
- `status_update` - Agent sends periodic status
- `heartbeat` - Health check mechanism
- `event` - Agent reports events
- `ping/pong` - Connection health checks

### Example Messages

**Registration:**
```json
{
  "message_type": "register",
  "agent_id": "rpi_bedroom_led",
  "timestamp": 1720872345.123,
  "payload": {
    "agent_type": "rpi_led_controller",
    "capabilities": ["led_control", "status_monitoring"],
    "location": "bedroom"
  }
}
```

**Command:**
```json
{
  "message_type": "command",
  "agent_id": "rpi_bedroom_led",
  "payload": {
    "request_id": "cmd_001",
    "command": "turn on the LED",
    "priority": "normal"
  }
}
```

**Response:**
```json
{
  "message_type": "response",
  "agent_id": "rpi_bedroom_led",
  "payload": {
    "request_id": "cmd_001",
    "success": true,
    "response": "LED turned on successfully",
    "data": {"led_status": "on"}
  }
}
```

## 🔄 Operation Modes

### Interactive Mode (Default)
- No orchestrator URL configured
- User can type commands directly
- Agent responds in real-time

### Orchestrator Mode
- Orchestrator URL configured
- Agent connects to orchestrator
- Waits for commands from orchestrator
- Sends periodic status updates

## 🛠️ Integration with Your Orchestrator

To integrate with your own orchestrator:

1. **Implement WebSocket Server** that accepts connections on `/ws` endpoint
2. **Handle Registration** - Store agent capabilities and information
3. **Send Commands** - Use the command message format
4. **Process Responses** - Handle agent responses and status updates
5. **Monitor Health** - Use heartbeat/ping-pong for connection monitoring

## 🎯 Use Cases

1. **Smart Home Orchestration** - Control multiple RPi agents from central hub
2. **Emergency Response** - Coordinate alerts across all devices
3. **Scheduled Tasks** - Centrally managed automation
4. **Health Monitoring** - Track all agent statuses from one place
5. **Load Balancing** - Distribute tasks across available agents

## 🔧 Troubleshooting

### Connection Issues
- Check orchestrator URL format: `ws://host:port/ws`
- Verify orchestrator server is running
- Check network connectivity
- Review logs for connection errors

### Message Handling
- Ensure message handlers are registered
- Check JSON format of messages
- Verify agent ID matches
- Monitor for connection drops

### Performance
- Adjust heartbeat interval for your needs
- Monitor message queue size
- Check connection statistics with `get_stats()`

## 📊 Monitoring

The client provides connection statistics:
```python
stats = orchestrator_client.get_stats()
print(f"Messages sent: {stats['messages_sent']}")
print(f"Connection uptime: {stats['uptime']}s")
print(f"Is connected: {stats['is_connected']}")
```

This WebSocket implementation provides a robust foundation for your RPi agent to communicate with any orchestrator system while maintaining high performance and reliability! 🚀
