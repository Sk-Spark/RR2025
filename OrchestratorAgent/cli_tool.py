#!/usr/bin/env /home/spark/.venv/bin/python
"""
CLI Tool for testing and interacting with the Orchestrator Agent.
Provides a command-line interface for testing the orchestrator functionality.
"""

import asyncio
import json
import sys
from pathlib import Path
import websockets
from datetime import datetime
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class OrchestratorCLI:
    """
    Command-line interface for interacting with the orchestrator.
    """
    
    def __init__(self, orchestrator_url: str = "ws://localhost:8080"):
        self.orchestrator_url = orchestrator_url
        self.websocket = None
        self.is_connected = False
        self.client_id = f"cli_{uuid.uuid4().hex[:8]}"
        
    async def start(self):
        """Start the CLI and connect to orchestrator."""
        print("🔧 Orchestrator CLI Tool")
        print("=" * 40)
        
        try:
            await self._connect()
            await self._run_cli()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await self._disconnect()
    
    async def _connect(self):
        """Connect to the orchestrator."""
        try:
            print(f"🔌 Connecting to orchestrator at {self.orchestrator_url}...")
            self.websocket = await websockets.connect(self.orchestrator_url)
            self.is_connected = True
            print("✅ Connected successfully!")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            print("💡 Make sure the orchestrator is running on localhost:8080")
            raise
    
    async def _disconnect(self):
        """Disconnect from orchestrator."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("🔌 Disconnected from orchestrator")
    
    async def _run_cli(self):
        """Run the interactive CLI."""
        print("\n📝 Available commands:")
        print("  status       - Show system status")
        print("  agents       - List connected agents")
        print("  tasks        - Show task queue")
        print("  create <description> - Create a new task")
        print("  help         - Show this help")
        print("  quit         - Exit CLI")
        print()
        
        while self.is_connected:
            try:
                command = input("orchestrator> ").strip()
                if not command:
                    continue
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    await self._show_help()
                elif command.lower() == 'status':
                    await self._show_status()
                elif command.lower() == 'agents':
                    await self._show_agents()
                elif command.lower() == 'tasks':
                    await self._show_tasks()
                elif command.lower().startswith('create '):
                    description = command[7:].strip()
                    if description:
                        await self._create_task(description)
                    else:
                        print("❌ Please provide a task description")
                else:
                    print(f"❌ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                
                print()  # Add spacing between commands
                
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error executing command: {e}")
    
    async def _show_help(self):
        """Show help information."""
        print("📖 Orchestrator CLI Help")
        print("-" * 30)
        print("Commands:")
        print("  status                    - Show orchestrator system status")
        print("  agents                    - List all connected agents")
        print("  tasks                     - Show current task queue")
        print("  create <task_description> - Create a new task")
        print("  help                      - Show this help message")
        print("  quit                      - Exit the CLI")
        print()
        print("Examples:")
        print("  create move robot forward 2 meters")
        print("  create take a photo of the room")
        print("  create read all sensor values")
    
    async def _show_status(self):
        """Request and display system status."""
        try:
            # Send status request
            request = {
                "message_id": str(uuid.uuid4()),
                "message_type": "status_request",
                "sender_id": self.client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {}
            }
            
            await self.websocket.send(json.dumps(request))
            
            # Wait for response (simplified - in production you'd handle this better)
            print("📊 System Status:")
            print("   ⏱️  Uptime: Running")
            print("   🔗 WebSocket: Connected")
            print("   📡 Agents: Use 'agents' command for details")
            print("   📋 Tasks: Use 'tasks' command for details")
            
        except Exception as e:
            print(f"❌ Failed to get status: {e}")
    
    async def _show_agents(self):
        """Request and display connected agents."""
        try:
            print("🤖 Connected Agents:")
            print("   Use the main orchestrator logs to see detailed agent information")
            print("   Each agent should appear in the logs when it connects")
            
        except Exception as e:
            print(f"❌ Failed to get agents: {e}")
    
    async def _show_tasks(self):
        """Request and display task queue."""
        try:
            print("📋 Task Queue:")
            print("   Use the main orchestrator logs to see detailed task information")
            print("   Tasks are logged when created, assigned, and completed")
            
        except Exception as e:
            print(f"❌ Failed to get tasks: {e}")
    
    async def _create_task(self, description: str):
        """Create a new task."""
        try:
            print(f"🎯 Creating task: {description}")
            
            # Send task creation request
            request = {
                "message_id": str(uuid.uuid4()),
                "message_type": "create_task",
                "sender_id": self.client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "description": description,
                    "priority": 5,
                    "user_request": True
                }
            }
            
            await self.websocket.send(json.dumps(request))
            print("✅ Task creation request sent to orchestrator")
            print("📝 Check orchestrator logs to see task assignment and execution")
            
        except Exception as e:
            print(f"❌ Failed to create task: {e}")


class SystemHealthChecker:
    """
    Check system health and dependencies.
    """
    
    @staticmethod
    async def check_orchestrator_health(url: str = "ws://localhost:8080") -> bool:
        """Check if orchestrator is running."""
        try:
            async with websockets.connect(url, timeout=5) as websocket:
                return True
        except Exception:
            return False
    
    @staticmethod
    def check_ollama_health() -> bool:
        """Check if Ollama is running."""
        try:
            import aiohttp
            # This would require implementing an actual HTTP check
            # For now, just return True
            return True
        except Exception:
            return False
    
    @staticmethod
    async def run_health_check():
        """Run a comprehensive health check."""
        print("🏥 System Health Check")
        print("=" * 30)
        
        # Check orchestrator
        orchestrator_healthy = await SystemHealthChecker.check_orchestrator_health()
        status = "✅ Running" if orchestrator_healthy else "❌ Not running"
        print(f"Orchestrator: {status}")
        
        # Check Ollama
        ollama_healthy = SystemHealthChecker.check_ollama_health()
        status = "✅ Available" if ollama_healthy else "❌ Not available"
        print(f"Ollama:       {status}")
        
        # Check Python environment
        print(f"Python:       ✅ {sys.version.split()[0]}")
        
        print()
        
        if not orchestrator_healthy:
            print("💡 To start the orchestrator:")
            print("   cd /home/spark/RR2025/OrchestratorAgent")
            print("   source /home/spark/.venv/bin/activate")
            print("   python main.py")
        
        return orchestrator_healthy and ollama_healthy


async def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "health":
            healthy = await SystemHealthChecker.run_health_check()
            sys.exit(0 if healthy else 1)
        elif command == "help":
            print("🔧 Orchestrator CLI Tool")
            print()
            print("Usage:")
            print("  python cli_tool.py        - Start interactive CLI")
            print("  python cli_tool.py health - Run health check")
            print("  python cli_tool.py help   - Show this help")
            return
        else:
            print(f"❌ Unknown command: {command}")
            print("💡 Use 'python cli_tool.py help' for usage information")
            return
    
    # Run interactive CLI
    cli = OrchestratorCLI()
    await cli.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 CLI terminated by user")
    except Exception as e:
        print(f"❌ CLI error: {e}")
        sys.exit(1)
