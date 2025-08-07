#!/usr/bin/env python3
"""
Simple test script to demonstrate the AI Bot Agent capabilities
Run this script to see a comprehensive AI bot in action
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aibot_agent import AIBotAgent

async def demo_aibot_capabilities():
    """Demonstrate various AI bot capabilities"""
    
    print("=" * 60)
    print("🤖 AI BOT AGENT CAPABILITY DEMONSTRATION")
    print("=" * 60)
    
    # Create AI bot agent
    agent = AIBotAgent("demo_aibot")
    
    print(f"\n📋 Agent Info:")
    print(f"   ID: {agent.agent_id}")
    print(f"   Name: {agent.agent_name}")
    print(f"   Type: {agent.agent_type}")
    print(f"   Capabilities: {len(agent.capabilities)} total")
    
    print(f"\n🔧 Available Capabilities:")
    capability_groups = {
        "Movement": [cap for cap in agent.capabilities if any(word in cap for word in ["move", "turn", "stop", "speed", "position", "rotate"])],
        "Vision": [cap for cap in agent.capabilities if any(word in cap for word in ["capture", "video", "detect", "track", "camera", "pan", "zoom"])],
        "Sensors": [cap for cap in agent.capabilities if any(word in cap for word in ["read_", "scan", "battery", "temperature", "humidity"])],
        "Navigation": [cap for cap in agent.capabilities if any(word in cap for word in ["destination", "path", "navigate", "obstacle", "location"])],
        "AI": [cap for cap in agent.capabilities if any(word in cap for word in ["analyze", "decision", "learn", "communicate"])]
    }
    
    for group, caps in capability_groups.items():
        print(f"   {group}: {len(caps)} capabilities")
        for cap in caps[:3]:  # Show first 3
            print(f"     • {cap}")
        if len(caps) > 3:
            print(f"     • ... and {len(caps) - 3} more")
    
    print(f"\n🧪 TESTING KEY CAPABILITIES")
    print("-" * 40)
    
    # Test movement
    print("\n🚶 Testing Movement:")
    result = await agent.execute_command("move_forward", {"distance": 2.0})
    print(f"   ✅ Moved forward: {result['distance_moved']}m to {result['new_position']}")
    
    result = await agent.execute_command("turn_left", {"angle": 45})
    print(f"   ✅ Turned left: {result['angle_turned']}° to {result['new_orientation']['yaw']}°")
    
    # Test vision
    print("\n👁️ Testing Vision:")
    result = await agent.execute_command("capture_image", {"filename": "test_image.jpg"})
    print(f"   ✅ Captured image: {result['filename']} ({result['file_size']} bytes)")
    
    result = await agent.execute_command("detect_objects", {"confidence": 0.7})
    print(f"   ✅ Detected objects: {result['total_objects']} objects found")
    for obj in result['detections'][:2]:  # Show first 2
        print(f"      • {obj['type']} (confidence: {obj['confidence']}, distance: {obj['distance']}m)")
    
    # Test sensors
    print("\n🌡️ Testing Sensors:")
    result = await agent.execute_command("read_temperature", {})
    print(f"   ✅ Temperature: {result['temperature']}°C")
    
    result = await agent.execute_command("read_battery", {})
    print(f"   ✅ Battery: {result['battery_level']}% ({result['voltage']}V)")
    
    result = await agent.execute_command("scan_environment", {})
    env = result['environment_data']
    print(f"   ✅ Environment scan:")
    print(f"      • Temperature: {env['temperature']}°C, Humidity: {env['humidity']}%")
    print(f"      • Light: {env['light_level']} lux, Air quality: {env['air_quality']}")
    
    # Test navigation
    print("\n🗺️ Testing Navigation:")
    result = await agent.execute_command("set_destination", {"x": 10.0, "y": 5.0})
    print(f"   ✅ Destination set: {result['destination']} ({result['distance_to_destination']}m away)")
    
    result = await agent.execute_command("plan_path", {})
    print(f"   ✅ Path planned: {result['waypoint_count']} waypoints, {result['total_distance']}m total")
    
    # Test AI capabilities
    print("\n🧠 Testing AI Capabilities:")
    result = await agent.execute_command("analyze_scene", {})
    analysis = result['analysis']
    print(f"   ✅ Scene analysis:")
    print(f"      • Scene type: {analysis['scene_type']}, Complexity: {analysis['complexity']}")
    print(f"      • Elements: {', '.join(analysis['elements_detected'])}")
    print(f"      • Safety: {analysis['safety_level']}, Recommended: {analysis['recommended_action']}")
    
    result = await agent.execute_command("make_decision", {
        "context": "navigation_obstacle", 
        "options": ["go_around", "wait", "back_up"]
    })
    decision = result['decision']
    print(f"   ✅ Decision made: {decision['chosen_option']} (confidence: {decision['confidence']})")
    
    result = await agent.execute_command("communicate", {
        "message": "Hello, I am an AI bot ready for tasks!",
        "recipient": "human_operator"
    })
    print(f"   ✅ Communication: Sent message to {result['recipient']}")
    print(f"      Response: {result['response_received']}")
    
    print(f"\n📊 FINAL STATUS:")
    result = await agent.execute_command("get_position", {})
    print(f"   Position: ({result['position']['x']:.1f}, {result['position']['y']:.1f})")
    print(f"   Heading: {result['orientation']['yaw']:.1f}°")
    print(f"   Speed: {result['speed']} m/s")
    print(f"   Status: {'Moving' if result['is_moving'] else 'Stationary'}")
    
    print(f"\n✅ DEMONSTRATION COMPLETE!")
    print("   The AI bot successfully demonstrated all major capability groups:")
    print("   • Movement and locomotion")
    print("   • Vision and object detection") 
    print("   • Environmental sensing")
    print("   • Navigation and pathfinding")
    print("   • AI decision making and communication")
    print("\n🎯 This AI bot agent is ready to connect to your orchestrator!")

async def demo_orchestrator_connection():
    """Demonstrate connecting to orchestrator"""
    
    print("\n" + "=" * 60)
    print("🔗 ORCHESTRATOR CONNECTION DEMONSTRATION")
    print("=" * 60)
    
    agent = AIBotAgent("connection_demo")
    
    print(f"\n🚀 Attempting to connect to orchestrator...")
    print(f"   Agent: {agent.agent_name}")
    print(f"   Target: ws://localhost:8080")
    print(f"   Capabilities: {len(agent.capabilities)} total")
    
    try:
        print(f"\n⏳ Connecting... (timeout in 5 seconds)")
        # Try to connect with timeout
        await asyncio.wait_for(agent.connect_to_orchestrator(), timeout=5.0)
        
    except asyncio.TimeoutError:
        print(f"   ⚠️  Connection timeout - orchestrator not running")
        print(f"   ℹ️  To connect to orchestrator:")
        print(f"      1. Start orchestrator: python main.py")
        print(f"      2. Run this demo: python test_simple_aibot.py")
        
    except ConnectionRefusedError:
        print(f"   ❌ Connection refused - orchestrator not running")
        print(f"   ℹ️  Start the orchestrator first: python main.py")
        
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        
    finally:
        if agent.is_connected:
            await agent.disconnect()
            print(f"   ✅ Disconnected successfully")

async def main():
    """Main demo function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--connect":
        await demo_orchestrator_connection()
    else:
        await demo_aibot_capabilities()
        
        print(f"\n💡 TIP: Run with --connect to test orchestrator connection")
        print(f"   Example: python test_simple_aibot.py --connect")

if __name__ == "__main__":
    asyncio.run(main())
