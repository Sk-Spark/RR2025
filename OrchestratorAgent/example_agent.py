#!/usr/bin/env python3
"""
Example Agent - Demonstrates how to connect to the Orchestrator Agent
This is a sample implementation showing the communication protocol.
"""

import asyncio
import json
import websockets
from datetime import datetime
import uuid
from typing import Dict, Any, Optional


class ExampleAgent:
    """
    Example agent that demonstrates the communication protocol with the orchestrator.
    This agent has basic movement and sensor capabilities.
    """
    
    def __init__(self, agent_id: str, name: str, orchestrator_url: str = "ws://localhost:8080"):
        self.agent_id = agent_id
        self.name = name
        self.orchestrator_url = orchestrator_url
        
        # Agent state
        self.status = "offline"
        self.websocket = None
        self.is_running = False
        
        # Capabilities
        self.capabilities = [
            {
                "name": "move_forward",
                "description": "Move robot forward by specified distance",
                "category": "movement",
                "parameters": {"distance": "float", "speed": "float"},
                "estimated_duration": 5
            },
            {
                "name": "turn_left",
                "description": "Turn robot left by specified degrees",
                "category": "movement", 
                "parameters": {"degrees": "float"},
                "estimated_duration": 3
            },
            {
                "name": "read_sensors",
                "description": "Read all sensor values",
                "category": "sensor",
                "parameters": {},
                "estimated_duration": 1
            }
        ]
        
        # Active tasks
        self.active_tasks = []
        
        print(f"🤖 Example Agent '{name}' initialized with ID: {agent_id}")
    
    async def start(self):
        """Start the agent and connect to orchestrator."""
        self.is_running = True
        
        try:
            print(f"🔌 Connecting to orchestrator at {self.orchestrator_url}")
            
            async with websockets.connect(self.orchestrator_url) as websocket:
                self.websocket = websocket
                print("✅ Connected to orchestrator!")
                
                # Register with orchestrator
                await self._register_with_orchestrator()
                
                # Start message handling
                await asyncio.gather(
                    self._message_handler(),
                    self._heartbeat_sender(),
                    self._task_simulator()
                )
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            self.status = "offline"
            print("🔌 Disconnected from orchestrator")
    
    async def stop(self):
        """Stop the agent."""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
    
    async def _register_with_orchestrator(self):
        """Register this agent with the orchestrator."""
        registration_message = {
            "message_id": str(uuid.uuid4()),
            "message_type": "register_agent",
            "sender_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "agent": {
                    "agent_id": self.agent_id,
                    "name": self.name,
                    "agent_type": "example_robot",
                    "capabilities": self.capabilities,
                    "location": "lab_station_1",
                    "version": "1.0.0"
                },
                "connection_info": {
                    "protocol_version": "1.0",
                    "supported_features": ["heartbeat", "task_execution", "status_updates"]
                }
            }
        }
        
        await self._send_message(registration_message)
        print("📝 Registration request sent to orchestrator")
    
    async def _message_handler(self):
        """Handle incoming messages from orchestrator."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._process_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed by orchestrator")
        except Exception as e:
            print(f"❌ Error handling message: {e}")
    
    async def _process_message(self, message: Dict[str, Any]):
        """Process a message from the orchestrator."""
        message_type = message.get("message_type")
        sender_id = message.get("sender_id")
        payload = message.get("payload", {})
        
        print(f"📨 Received message: {message_type} from {sender_id}")
        
        if message_type == "task_assignment":
            await self._handle_task_assignment(message)
        elif message_type == "status_update":
            await self._handle_status_update(message)
        elif message_type == "ping":
            await self._handle_ping(message)
        elif message_type == "error":
            print(f"❌ Error from orchestrator: {payload.get('error')}")
        else:
            print(f"⚠️ Unknown message type: {message_type}")
    
    async def _handle_task_assignment(self, message: Dict[str, Any]):
        """Handle task assignment from orchestrator."""
        task = message["payload"]["task"]
        task_id = task["task_id"]
        capability_required = task["capability_required"]
        parameters = task.get("parameters", {})
        
        print(f"🎯 Task assigned: {task['name']} (ID: {task_id})")
        print(f"   Capability: {capability_required}")
        print(f"   Parameters: {parameters}")
        
        # Add to active tasks
        self.active_tasks.append(task_id)
        
        # Send task update - started
        await self._send_task_update(task_id, "in_progress", "Task execution started")
        
        # Simulate task execution
        await self._execute_task(task)
    
    async def _execute_task(self, task: Dict[str, Any]):
        """Simulate task execution."""
        task_id = task["task_id"]
        capability = task["capability_required"]
        parameters = task.get("parameters", {})
        
        try:
            print(f"🚀 Executing task {task_id}: {capability}")
            
            # Simulate different task types
            if capability == "move_forward":
                distance = parameters.get("distance", 1.0)
                speed = parameters.get("speed", 1.0)
                print(f"   Moving forward {distance}m at speed {speed}")
                await asyncio.sleep(3)  # Simulate movement time
                result = {"final_position": f"moved_{distance}m", "actual_speed": speed}
                
            elif capability == "turn_left":
                degrees = parameters.get("degrees", 90)
                print(f"   Turning left {degrees} degrees")
                await asyncio.sleep(2)  # Simulate turn time
                result = {"final_heading": f"turned_{degrees}_degrees"}
                
            elif capability == "read_sensors":
                print("   Reading sensors...")
                await asyncio.sleep(1)  # Simulate sensor reading
                result = {
                    "temperature": 22.5,
                    "humidity": 45.2,
                    "distance_front": 150.3,
                    "battery_level": 78
                }
                
            else:
                raise Exception(f"Unknown capability: {capability}")
            
            # Send progress update
            await self._send_task_update(task_id, "in_progress", "Task 80% complete", 80)
            await asyncio.sleep(1)
            
            # Send completion result
            await self._send_task_result(task_id, "completed", result)
            print(f"✅ Task {task_id} completed successfully")
            
        except Exception as e:
            # Send failure result
            await self._send_task_result(task_id, "failed", None, str(e))
            print(f"❌ Task {task_id} failed: {e}")
        
        finally:
            # Remove from active tasks
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
    
    async def _send_task_update(self, task_id: str, status: str, message: str = "", progress: int = None):
        """Send task progress update to orchestrator."""
        update_message = {
            "message_id": str(uuid.uuid4()),
            "message_type": "task_update",
            "sender_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "task_id": task_id,
                "status": status,
                "message": message,
                "progress_percentage": progress
            }
        }
        
        await self._send_message(update_message)
    
    async def _send_task_result(self, task_id: str, status: str, result: Optional[Dict] = None, error_message: str = None):
        """Send task completion result to orchestrator."""
        result_message = {
            "message_id": str(uuid.uuid4()),
            "message_type": "task_result",
            "sender_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "task_id": task_id,
                "status": status,
                "result": result,
                "error_message": error_message,
                "execution_time_seconds": 5.0  # Simulated
            }
        }
        
        await self._send_message(result_message)
    
    async def _handle_status_update(self, message: Dict[str, Any]):
        """Handle status update from orchestrator."""
        payload = message.get("payload", {})
        if payload.get("status") == "registered":
            self.status = "online"
            print("✅ Successfully registered with orchestrator!")
    
    async def _handle_ping(self, message: Dict[str, Any]):
        """Handle ping from orchestrator."""
        pong_message = {
            "message_id": str(uuid.uuid4()),
            "message_type": "pong",
            "sender_id": self.agent_id,
            "recipient_id": message["sender_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": message["message_id"],
            "payload": {}
        }
        
        await self._send_message(pong_message)
    
    async def _heartbeat_sender(self):
        """Send periodic heartbeat to orchestrator."""
        while self.is_running:
            try:
                if self.status == "online":
                    heartbeat_message = {
                        "message_id": str(uuid.uuid4()),
                        "message_type": "heartbeat",
                        "sender_id": self.agent_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "payload": {
                            "agent_id": self.agent_id,
                            "status": self.status,
                            "cpu_usage": 25.5,  # Simulated
                            "memory_usage": 45.2,  # Simulated
                            "active_tasks": self.active_tasks.copy()
                        }
                    }
                    
                    await self._send_message(heartbeat_message)
                    print(f"💓 Heartbeat sent (Active tasks: {len(self.active_tasks)})")
                
                await asyncio.sleep(10)  # Send heartbeat every 10 seconds
                
            except Exception as e:
                print(f"❌ Error sending heartbeat: {e}")
                await asyncio.sleep(5)
    
    async def _task_simulator(self):
        """Simulate random status changes and events."""
        await asyncio.sleep(30)  # Wait a bit before starting simulation
        
        while self.is_running:
            try:
                # Occasionally simulate capability updates
                if len(self.active_tasks) == 0 and self.status == "online":
                    print("🔄 Simulating capability update...")
                    
                    # Add a new temporary capability
                    new_capability = {
                        "name": "emergency_stop",
                        "description": "Emergency stop all movement",
                        "category": "safety",
                        "parameters": {},
                        "estimated_duration": 1
                    }
                    
                    self.capabilities.append(new_capability)
                    
                    capability_update = {
                        "message_id": str(uuid.uuid4()),
                        "message_type": "capability_update", 
                        "sender_id": self.agent_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "payload": {
                            "capabilities": self.capabilities
                        }
                    }
                    
                    await self._send_message(capability_update)
                    print("📤 Capability update sent")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"❌ Error in task simulator: {e}")
                await asyncio.sleep(30)
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send a message to the orchestrator."""
        if self.websocket:
            await self.websocket.send(json.dumps(message))


async def main():
    """Main function to run the example agent."""
    print("🤖 Starting Example Agent...")
    print("=" * 50)
    
    # Create agent with unique ID
    agent_id = f"example_agent_{uuid.uuid4().hex[:8]}"
    agent = ExampleAgent(
        agent_id=agent_id,
        name="Example Movement & Sensor Robot",
        orchestrator_url="ws://localhost:8080"
    )
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent.stop()
        print("👋 Example Agent stopped")


if __name__ == "__main__":
    asyncio.run(main())
