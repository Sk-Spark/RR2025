#!/usr/bin/env python3
"""
Simple Test Orchestrator Server (Server Only)
A basic WebSocket server for testing the RPi agent communication without interactive console.
"""

import asyncio
import json
import logging
import uuid
import time
import websockets
from typing import Dict, Set, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleOrchestrator:
    """Simple test orchestrator for RPi agent communication."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """Initialize the test orchestrator."""
        self.host = host
        self.port = port
        self.connected_agents: Dict[str, Dict[str, Any]] = {}
        self.websockets: Dict[str, Any] = {}
        
    async def register_agent(self, websocket: Any, agent_data: Dict[str, Any]):
        """Register a new agent."""
        agent_id = agent_data.get("agent_id")
        if not agent_id:
            logger.error("Agent registration missing agent_id")
            return
        
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
        
        logger.info(f"📋 Agent {agent_id} response to {request_id}: {response} (success: {success})")
        
        if payload.get("data"):
            logger.info(f"📊 Response data: {payload['data']}")
    
    def handle_status_update(self, data: Dict[str, Any]):
        """Handle status update from agent."""
        agent_id = data.get("agent_id")
        payload = data.get("payload", {})
        led_status = payload.get("led_status")
        
        if agent_id in self.connected_agents:
            self.connected_agents[agent_id]["led_status"] = led_status
            self.connected_agents[agent_id]["last_status_update"] = time.time()
        
        logger.info(f"🔄 Agent {agent_id} status update - LED: {led_status}")
    
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
        """Start the WebSocket server."""
        logger.info(f"🚀 Starting orchestrator server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"🌐 Orchestrator server running on ws://{self.host}:{self.port}")
            logger.info("⏳ Waiting for RPi agents to connect...")
            logger.info("💡 Press Ctrl+C to stop the server")
            
            # Keep server running until cancelled
            try:
                await asyncio.Future()  # Run forever
            except asyncio.CancelledError:
                logger.info("🛑 Server shutdown requested")
                raise


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
        logger.info("✅ Orchestrator shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
