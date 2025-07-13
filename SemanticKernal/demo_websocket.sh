#!/bin/bash

echo "🚀 WebSocket Communication Demo"
echo "==============================="
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🧹 Cleaning up background processes..."
    pkill -f test_orchestrator.py 2>/dev/null
    pkill -f "python main.py" 2>/dev/null
    exit 0
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

echo "1️⃣  Starting Test Orchestrator Server..."
python test_orchestrator.py &
ORCHESTRATOR_PID=$!

# Wait for server to start
sleep 3

echo "2️⃣  Starting RPi Agent in Orchestrator Mode..."
export ORCHESTRATOR_URL='ws://localhost:8080/ws'
export AGENT_ID='rpi_demo_led'

# Run agent for 10 seconds to show connection
timeout 10s python main.py &
AGENT_PID=$!

echo ""
echo "🔄 Agent and Orchestrator are running..."
echo "   Agent should connect to orchestrator"
echo "   Check the logs above for connection status"
echo ""

# Wait for agent to finish
wait $AGENT_PID

echo ""
echo "✅ Demo completed!"
echo "   To test manually:"
echo "   Terminal 1: python test_orchestrator.py"
echo "   Terminal 2: ORCHESTRATOR_URL='ws://localhost:8080/ws' python main.py"
