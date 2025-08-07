#!/usr/bin/env python3
"""
Simple test script to send scenario commands to the orchestrator.
"""

import asyncio
import json
import websockets
from datetime import datetime

async def send_scenario_command(scenario_text):
    """Send a scenario command to the orchestrator."""
    uri = "ws://localhost:8080"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"🔌 Connected to orchestrator at {uri}")
            
            # Create a test message (following the orchestrator's message format)
            message = {
                "type": "user_input",
                "timestamp": datetime.utcnow().isoformat(),
                "content": {
                    "command": "scenario",
                    "description": scenario_text,
                    "user_id": "test_user"
                }
            }
            
            # Send the message
            await websocket.send(json.dumps(message))
            print(f"📤 Sent scenario: {scenario_text}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📥 Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 10 seconds")
                
    except Exception as e:
        print(f"❌ Error connecting to orchestrator: {e}")

async def main():
    """Main test function."""
    scenarios = [
        "Move the robot forward 2 meters and then turn left",
        "Navigate to the kitchen and pick up a red cup",
        "Patrol the house perimeter and report any anomalies"
    ]
    
    print("🤖 Testing Orchestrator Natural Language Scenarios")
    print("=" * 60)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Test {i}: {scenario}")
        await send_scenario_command(scenario)
        await asyncio.sleep(2)  # Wait between tests

if __name__ == "__main__":
    asyncio.run(main())
