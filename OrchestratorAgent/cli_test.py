#!/usr/bin/env python3
"""
CLI Tool for testing and interacting with the Orchestrator Agent.
Provides commands to test task creation, agent monitoring, and system status.
"""

import asyncio
import json
import sys
import uuid
import websockets
from datetime import datetime
from typing import Dict, Any, Optional


class OrchestratorCLI:
    """Command line interface for interacting with the orchestrator."""
    
    def __init__(self, orchestrator_url: str = "ws://localhost:8080"):
        self.orchestrator_url = orchestrator_url
        self.websocket = None
        self.client_id = f"cli_{uuid.uuid4().hex[:8]}"
    
    async def connect(self):
        """Connect to the orchestrator."""
        try:
            print(f"🔌 Connecting to orchestrator at {self.orchestrator_url}")
            self.websocket = await websockets.connect(self.orchestrator_url)
            print("✅ Connected to orchestrator!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the orchestrator."""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Disconnected from orchestrator")
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message and wait for response."""
        if not self.websocket:
            print("❌ Not connected to orchestrator")
            return {}
        
        try:
            await self.websocket.send(json.dumps(message))
            
            # Wait for response (simplified - in production you'd match correlation IDs)
            response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
            return json.loads(response)
            
        except asyncio.TimeoutError:
            print("⏰ Request timed out")
            return {}
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return {}
    
    async def test_system_status(self):
        """Test getting system status (if implemented)."""
        print("\n📊 Testing System Status...")
        print("-" * 30)
        
        # This would require implementing a status endpoint or message type
        # For now, we'll just try to connect and see what agents are connected
        message = {
            "message_id": str(uuid.uuid4()),
            "message_type": "ping",
            "sender_id": self.client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {}
        }
        
        response = await self.send_message(message)
        if response:
            print(f"✅ Orchestrator is responsive: {response.get('message_type', 'unknown')}")
        else:
            print("❌ No response from orchestrator")
    
    async def simulate_user_task(self, task_description: str):
        """Simulate creating a task from user input."""
        print(f"\n🎯 Simulating User Task: '{task_description}'")
        print("-" * 50)
        
        # Note: This requires the orchestrator to implement a task creation endpoint
        # For demonstration, we'll show what the message would look like
        message = {
            "message_id": str(uuid.uuid4()),
            "message_type": "create_task",
            "sender_id": self.client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "user_input": task_description,
                "priority": 5,
                "requester": "cli_user"
            }
        }
        
        print(f"📤 Would send task creation request:")
        print(json.dumps(message, indent=2))
        print("\nNote: Task creation from CLI requires implementation of 'create_task' message type")
    
    def print_help(self):
        """Print available commands."""
        print("\n🤖 Orchestrator CLI Commands:")
        print("=" * 40)
        print("1. status      - Check orchestrator status")
        print("2. task <desc> - Create task from description")
        print("3. agents      - List connected agents (if available)")
        print("4. help        - Show this help")
        print("5. quit        - Exit CLI")
        print("=" * 40)
    
    async def interactive_mode(self):
        """Run interactive CLI mode."""
        print("\n🎮 Orchestrator CLI - Interactive Mode")
        print("Type 'help' for available commands")
        
        if not await self.connect():
            return
        
        try:
            while True:
                try:
                    command = input("\n🤖 orchestrator> ").strip().lower()
                    
                    if command == "quit" or command == "exit":
                        break
                    elif command == "help":
                        self.print_help()
                    elif command == "status":
                        await self.test_system_status()
                    elif command.startswith("task "):
                        task_desc = command[5:]  # Remove "task " prefix
                        await self.simulate_user_task(task_desc)
                    elif command == "agents":
                        print("📋 Agent listing requires implementation of agent query endpoint")
                    elif command == "":
                        continue
                    else:
                        print(f"❓ Unknown command: {command}")
                        print("Type 'help' for available commands")
                
                except KeyboardInterrupt:
                    print("\n\n🛑 Interrupted...")
                    break
                except EOFError:
                    print("\n\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        finally:
            await self.disconnect()


async def run_tests():
    """Run basic tests of orchestrator functionality."""
    print("🧪 Running Orchestrator Tests")
    print("=" * 40)
    
    cli = OrchestratorCLI()
    
    if await cli.connect():
        await cli.test_system_status()
        await cli.simulate_user_task("Move forward 2 meters and take a picture")
        await cli.disconnect()
    
    print("\n✅ Test sequence completed")


async def main():
    """Main CLI function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            await run_tests()
        elif sys.argv[1] == "interactive":
            cli = OrchestratorCLI()
            await cli.interactive_mode()
        else:
            print("Usage: python cli_test.py [test|interactive]")
    else:
        # Default to interactive mode
        cli = OrchestratorCLI()
        await cli.interactive_mode()


if __name__ == "__main__":
    print("🎛️ Orchestrator CLI Tool")
    print("=" * 30)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 CLI stopped by user")
    except Exception as e:
        print(f"\n❌ CLI error: {e}")
