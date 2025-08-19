#!/home/spark/RR2025/AiBot/venv/bin/python
"""
Interactive Mock Orchestrator Server
A WebSocket server for testing RPi agent communication with interactive command interface.
Uses the AiBot virtual environment for dependencies.
"""

import asyncio
import json
import logging
import uuid
import time
import websockets
import sys
from typing import Dict, Set, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleOrchestrator:
    """Interactive test orchestrator for RPi agent communication."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """Initialize the test orchestrator."""
        self.host = host
        self.port = port
        self.connected_agents: Dict[str, Dict[str, Any]] = {}
        self.websockets: Dict[str, Any] = {}
        self.agent_id = None  # Placeholder for agent ID, can be set during registration
        self.command_queue = asyncio.Queue()
        self.shutdown_event = asyncio.Event()
        
    async def register_agent(self, websocket: Any, agent_data: Dict[str, Any]):
        """Register a new agent."""
        agent_id = agent_data.get("agent_id")
        if not agent_id:
            logger.error("Agent registration missing agent_id")
            return
        
        self.agent_id = agent_id  # Store the agent ID for later use
        
        self.connected_agents[agent_id] = {
            "agent_id": agent_id,
            "connection_time": time.time(),
            "last_heartbeat": time.time(),
            "capabilities": agent_data.get("payload", {}).get("capabilities", []),
            "location": agent_data.get("payload", {}).get("location", ""),
            "agent_type": agent_data.get("payload", {}).get("agent_type", "unknown"),
            "status": "connected"
        }
        
        self.websockets[agent_id] = websocket
        
        logger.info(f"✅ Agent {agent_id} registered successfully")
        logger.info(f"🔧 Agent capabilities: {self.connected_agents[agent_id]['capabilities']}")
        
        # Notify user of new agent connection
        print(f"\n🤖 New agent connected: {agent_id}")
        print(f"   Type: {self.connected_agents[agent_id]['agent_type']}")
        print(f"   Capabilities: {', '.join(self.connected_agents[agent_id]['capabilities']) if self.connected_agents[agent_id]['capabilities'] else 'None'}")
        print("🎯 Command> ", end="", flush=True)
        
        # Send welcome message
        await self.send_to_agent(agent_id, {
            "message_type": "welcome",
            "payload": {
                "message": "Successfully registered with orchestrator",
                "orchestrator_id": "simple_orchestrator",
                "timestamp": time.time()
            }
        })
    
    async def handle_message(self, websocket: Any, message: str):
        """Handle incoming message from agent."""
        try:
            data = json.loads(message)
            message_type = data.get("message_type")
            agent_id = data.get("agent_id")
            
            logger.info(f"📨 Received {message_type} from {agent_id}")
            
            if message_type == "register":
                await self.register_agent(websocket, data)
                
            elif message_type == "response":
                self.handle_response(data)
                
            elif message_type == "status_update":
                self.handle_status_update(data)
                
            elif message_type == "heartbeat":
                self.handle_heartbeat(data)
                
            elif message_type == "pong":
                logger.debug(f"🏓 Received pong from {agent_id}")
                
            else:
                logger.warning(f"❓ Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    def handle_response(self, data: Dict[str, Any]):
        """Handle response from agent."""
        agent_id = data.get("agent_id")
        payload = data.get("payload", {})
        request_id = payload.get("request_id")
        success = payload.get("success")
        response = payload.get("response")
        
        # Print response for user visibility
        status_emoji = "✅" if success else "❌"
        print(f"\n{status_emoji} Response from {agent_id}:")
        print(f"   Request: {request_id}")
        print(f"   Success: {success}")
        print(f"   Response: {response}")
        
        if payload.get("data"):
            print(f"   Data: {payload['data']}")
        
        logger.info(f"📋 Agent {agent_id} response to {request_id}: {response} (success: {success})")
        
        if payload.get("data"):
            logger.info(f"📊 Response data: {payload['data']}")
        
        # Show command prompt again
        print("🎯 Command> ", end="", flush=True)
    
    def handle_status_update(self, data: Dict[str, Any]):
        """Handle status update from agent."""
        agent_id = data.get("agent_id")
        payload = data.get("payload", {})
        
        if agent_id in self.connected_agents:
            self.connected_agents[agent_id]["last_status_update"] = time.time()
        
        # Show status update to user
        print(f"\n🔄 Status Update from {agent_id}: {payload}")
        logger.info(f"🔄 Agent {agent_id} status update: {payload}")
        
        # Show command prompt again
        print("🎯 Command> ", end="", flush=True)
    
    def handle_heartbeat(self, data: Dict[str, Any]):
        """Handle heartbeat from agent."""
        agent_id = data.get("agent_id")
        
        if agent_id in self.connected_agents:
            self.connected_agents[agent_id]["last_heartbeat"] = time.time()
        
        logger.debug(f"💓 Heartbeat from {agent_id}")
    
    async def send_to_agent(self, agent_id: str, message: Dict[str, Any]):
        """Send message to specific agent."""
        if agent_id not in self.websockets:
            logger.error(f"❌ Agent {agent_id} not connected")
            return False
        
        try:
            websocket = self.websockets[agent_id]
            await websocket.send(json.dumps(message))
            logger.info(f"📤 Sent message to {agent_id}: {message.get('message_type')}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send message to {agent_id}: {e}")
            return False
    
    async def send_command_to_agent(self, agent_id: str, full_command: str):
        """Send a complete command string to a specific agent."""
        if agent_id not in self.websockets:
            print(f"❌ Agent {agent_id} not connected")
            return False
        
        request_id = str(uuid.uuid4())
        message = {
            "message_type": "command",
            "agent_id": "orchestrator",
            "request_id": request_id,
            "payload": {
                "command": full_command,
                "timestamp": time.time()
            }
        }
        
        success = await self.send_to_agent(agent_id, message)
        if success:
            print(f"✅ Command '{full_command}' sent to agent {agent_id}")
        return success
    
    def list_connected_agents(self):
        """List all connected agents."""
        if not self.connected_agents:
            print("📭 No agents currently connected")
            return
        
        print("\n🤖 Connected Agents:")
        print("-" * 50)
        for agent_id, info in self.connected_agents.items():
            connection_time = time.strftime("%H:%M:%S", time.localtime(info["connection_time"]))
            capabilities = ", ".join(info["capabilities"]) if info["capabilities"] else "None"
            print(f"Agent ID: {agent_id}")
            print(f"  Type: {info['agent_type']}")
            print(f"  Location: {info['location']}")
            print(f"  Connected: {connection_time}")
            print(f"  Capabilities: {capabilities}")
            print(f"  Status: {info['status']}")
            print()
    
    def show_help(self):
        """Show available commands."""
        print("\n🔧 Available Commands:")
        print("-" * 50)
        print("help                              - Show this help message")
        print("list                              - List connected agents")
        print("<agent_id> <full_command>         - Send command directly to agent")
        print("status <agent_id>                 - Get agent status")
        print("ping <agent_id>                   - Ping agent")
        print("quit                              - Shutdown orchestrator")
        print("\nExample commands:")
        print("  rpi_agent_01 get system info")
        print("  rpi_agent_01 move forward 10 speed 50")
        print("  rpi_agent_01 check sensor temperature")
        print("  status rpi_agent_01")
        print("  ping rpi_agent_01")
        print()
        print("Note: Commands are sent directly to agents without 'cmd' prefix.")
        print()
    
    async def process_user_command(self, user_input: str):
        """Process user command input."""
        parts = user_input.strip().split()
        if not parts:
            return
        
        command = parts[0].lower()
        
        if command == "help" or command == "h":
            self.show_help()
            
        elif command == "list" or command == "l":
            self.list_connected_agents()
            
        elif command == "quit" or command == "q" or command == "exit":
            print("👋 Shutting down orchestrator...")
            self.shutdown_event.set()
            
        elif command == "status" and len(parts) >= 2:
            agent_id = parts[1]
            await self.send_command_to_agent(agent_id, "get_status")
            
        elif command == "ping" and len(parts) >= 2:
            agent_id = parts[1]
            await self.send_command_to_agent(agent_id, "ping")
            
        elif len(parts) >= 2:
            # Treat the first part as agent_id and rest as command
            agent_id = parts[0]
            full_command = " ".join(parts[1:])
            
            # Check if agent exists
            if agent_id in self.connected_agents:
                await self.send_command_to_agent(agent_id, full_command)
            else:
                print(f"❌ Agent '{agent_id}' not connected. Use 'list' to see connected agents.")
            
        else:
            print("❓ Unknown command. Type 'help' for available commands.")
    
    async def user_input_handler(self):
        """Handle user input in a separate task."""
        print("\n" + "="*60)
        print("🎮 INTERACTIVE ORCHESTRATOR CONSOLE")
        print("="*60)
        print("Type 'help' for available commands")
        print("Type 'quit' to shutdown")
        print("-"*60)
        
        while not self.shutdown_event.is_set():
            try:
                # Use asyncio to handle input without blocking
                print("\n🎯 Command> ", end="", flush=True)
                
                # Read input in a non-blocking way
                loop = asyncio.get_event_loop()
                user_input = await loop.run_in_executor(None, sys.stdin.readline)
                
                if user_input:
                    await self.process_user_command(user_input.strip())
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except EOFError:
                print("\n👋 EOF received, shutting down...")
                self.shutdown_event.set()
                break
            except KeyboardInterrupt:
                print("\n👋 Keyboard interrupt received, shutting down...")
                self.shutdown_event.set()
                break
            except Exception as e:
                logger.error(f"❌ Error in user input handler: {e}")
                await asyncio.sleep(1)
    
    async def handle_client(self, websocket: Any):
        """Handle WebSocket client connection."""
        logger.info(f"🔗 New client connected from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Client disconnected")
        except Exception as e:
            logger.error(f"❌ Error handling client: {e}")
        finally:
            # Remove disconnected agent
            agent_to_remove = None
            for agent_id, ws in self.websockets.items():
                if ws == websocket:
                    agent_to_remove = agent_id
                    break
            
            if agent_to_remove:
                del self.websockets[agent_to_remove]
                if agent_to_remove in self.connected_agents:
                    del self.connected_agents[agent_to_remove]
                logger.info(f"🗑️  Agent {agent_to_remove} disconnected and removed")
    
    async def start_server(self):
        """Start the WebSocket server and user input handler."""
        logger.info(f"🚀 Starting orchestrator server on {self.host}:{self.port}")
        
        # Create server
        server = await websockets.serve(self.handle_client, self.host, self.port)
        logger.info(f"🌐 Orchestrator server running on ws://{self.host}:{self.port}")
        logger.info("⏳ Waiting for RPi agents to connect...")
        
        # Start user input handler
        input_task = asyncio.create_task(self.user_input_handler())
        
        try:
            # Wait for shutdown event
            await self.shutdown_event.wait()
            
        except asyncio.CancelledError:
            logger.info("🛑 Server shutdown requested")
            raise
        finally:
            # Clean shutdown
            input_task.cancel()
            server.close()
            await server.wait_closed()
            logger.info("🔌 Server closed")


async def main():
    """Main entry point."""
    orchestrator = SimpleOrchestrator()
    
    try:
        await orchestrator.start_server()   
        
    except KeyboardInterrupt:
        logger.info("🔄 Received keyboard interrupt")
        print("\n👋 Shutting down orchestrator...")
    except asyncio.CancelledError:
        logger.info("🔄 Server task was cancelled")
        print("\n👋 Shutting down orchestrator...")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        print(f"\n💥 Error occurred: {e}")
    finally:
        # Ensure shutdown event is set
        orchestrator.shutdown_event.set()
        logger.info("✅ Orchestrator shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
