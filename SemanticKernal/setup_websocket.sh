#!/bin/bash
"""
WebSocket Communication Setup Script
This script helps you set up and test the WebSocket communication between your RPi agent and orchestrator.
"""

echo "🚀 WebSocket Communication Setup for RPi LED Agent"
echo "=================================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. It's recommended to use one."
    echo "   You can create one with: python -m venv venv && source venv/bin/activate"
fi

# Install/upgrade required packages
echo ""
echo "📦 Installing required packages..."
pip install -r requirements.txt

echo ""
echo "🔧 WebSocket Communication Setup Complete!"
echo ""
echo "💡 Usage Examples:"
echo ""
echo "1️⃣  Start Test Orchestrator (in one terminal):"
echo "   python test_orchestrator.py"
echo ""
echo "2️⃣  Start RPi Agent in Orchestrator Mode (in another terminal):"
echo "   export ORCHESTRATOR_URL='ws://localhost:8080/ws'"
echo "   export AGENT_ID='rpi_bedroom_led'"
echo "   python main.py"
echo ""
echo "3️⃣  Or start RPi Agent in Interactive Mode (without orchestrator):"
echo "   python main.py"
echo ""
echo "🌐 Environment Variables for Orchestrator Mode:"
echo "   ORCHESTRATOR_URL - WebSocket URL of orchestrator (e.g., ws://localhost:8080/ws)"
echo "   AGENT_ID - Unique identifier for this agent (e.g., rpi_bedroom_led)"
echo "   HEARTBEAT_INTERVAL - Heartbeat interval in seconds (default: 30)"
echo "   MAX_RECONNECT_ATTEMPTS - Max reconnection attempts (-1 for unlimited)"
echo "   RECONNECT_DELAY - Delay between reconnection attempts in seconds (default: 5)"
echo ""
echo "📋 Message Types Supported:"
echo "   • register - Agent announces itself to orchestrator"
echo "   • command - Orchestrator sends commands to agent"
echo "   • query - Orchestrator requests information"
echo "   • response - Agent responds to commands/queries"
echo "   • status_update - Agent sends periodic status"
echo "   • heartbeat - Health check mechanism"
echo "   • event - Agent reports events"
echo ""
echo "🎮 Test Commands (from orchestrator console):"
echo "   list - List connected agents"
echo "   cmd <agent_id> turn on the LED - Send command to agent"
echo "   query <agent_id> status - Query agent status"
echo ""
echo "Ready to test WebSocket communication! 🎉"
