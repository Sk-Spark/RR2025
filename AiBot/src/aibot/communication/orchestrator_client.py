#!/usr/bin/env python3
"""
Enhanced Orchestrator Client
Advanced WebSocket client with reconnection, message queuing, and error handling.
"""

import asyncio
import json
import logging
import uuid
import time
from typing import Dict, Any, Optional, Callable, List
from collections import deque
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI, ConnectionClosedError

from .message_protocol import (
    MessageType, RegistrationMessage, CommandMessage, 
    ResponseMessage, StatusUpdateMessage, EventMessage
)

logger = logging.getLogger(__name__)


class OrchestratorClient:
    """Enhanced orchestrator client with robust communication features."""
    
    def __init__(self, orchestrator_url: str, agent_id: str, 
                 max_reconnect_attempts: int = -1, reconnect_delay: int = 5):
        """Initialize the orchestrator client."""
        self.orchestrator_url = orchestrator_url
        self.agent_id = agent_id
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.should_reconnect = True
        
        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.message_queue: deque = deque(maxlen=1000)
        
        # Background tasks
        self._listen_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "connection_errors": 0,
            "last_heartbeat": None,
            "connection_start_time": None
        }
    
    async def connect(self) -> bool:
        """Connect to orchestrator with retry logic."""
        self.should_reconnect = True
        
        while (self.should_reconnect and 
               (self.max_reconnect_attempts == -1 or 
                self.reconnect_attempts < self.max_reconnect_attempts)):
            try:
                logger.info(f"Attempting to connect to orchestrator at {self.orchestrator_url} (attempt {self.reconnect_attempts + 1})")
                
                self.websocket = await websockets.connect(
                    self.orchestrator_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                )
                
                self.is_connected = True
                self.reconnect_attempts = 0
                self.stats["connection_start_time"] = time.time()
                
                # Send registration
                await self._send_registration()
                
                logger.info("Successfully connected to orchestrator")
                
                # Start background tasks
                self._listen_task = asyncio.create_task(self._listen_loop())
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                # Send queued messages
                await self._send_queued_messages()
                
                return True
                
            except (ConnectionRefusedError, InvalidURI, OSError, Exception) as e:
                self.reconnect_attempts += 1
                self.stats["connection_errors"] += 1
                logger.error(f"Connection attempt {self.reconnect_attempts} failed: {e}")
                
                if (self.max_reconnect_attempts != -1 and 
                    self.reconnect_attempts >= self.max_reconnect_attempts):
                    logger.error("Max reconnection attempts reached")
                    self.should_reconnect = False
                    return False
                
                if self.should_reconnect:
                    await asyncio.sleep(self.reconnect_delay)
        
        return False
    
    async def _send_registration(self):
        """Send registration message to orchestrator."""
        try:
            registration = RegistrationMessage.create(
                agent_id=self.agent_id,
                capabilities=["led_control", "status_monitoring", "natural_language_processing"],
                location="raspberry_pi",
                agent_type="rpi_led_controller"
            )
            await self._send_raw_message(registration.to_dict())
            logger.info("Registration message sent to orchestrator")
        except Exception as e:
            logger.error(f"Failed to send registration: {e}")
    
    async def disconnect(self):
        """Gracefully disconnect from orchestrator."""
        logger.info("Disconnecting from orchestrator...")
        self.should_reconnect = False
        self.is_connected = False
        
        # Cancel background tasks
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close websocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")
        
        logger.info("Disconnected from orchestrator")
    
    async def _send_raw_message(self, data: Dict[str, Any]) -> bool:
        """Send raw message to orchestrator."""
        if not self.is_connected or not self.websocket:
            # Queue message for later sending
            self.message_queue.append(data)
            logger.warning("Not connected - message queued")
            return False
        
        try:
            message_json = json.dumps(data)
            await self.websocket.send(message_json)
            self.stats["messages_sent"] += 1
            logger.debug(f"Sent message: {data.get('message_type', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.is_connected = False
            # Queue the message for retry
            self.message_queue.append(data)
            return False
    
    async def _send_queued_messages(self):
        """Send all queued messages."""
        if not self.message_queue:
            return
        
        logger.info(f"Sending {len(self.message_queue)} queued messages")
        failed_messages = []
        
        while self.message_queue:
            try:
                message = self.message_queue.popleft()
                if not await self._send_raw_message(message):
                    failed_messages.append(message)
            except Exception as e:
                logger.error(f"Error sending queued message: {e}")
        
        # Re-queue failed messages
        for msg in failed_messages:
            self.message_queue.append(msg)
    
    async def send_command_response(self, request_id: str, success: bool, 
                                  response: str = "", data: Dict = None, error: str = ""):
        """Send response to a command."""
        response_msg = ResponseMessage.create(
            agent_id=self.agent_id,
            request_id=request_id,
            success=success,
            response=response,
            data=data,
            error=error
        )
        await self._send_raw_message(response_msg.to_dict())
    
    async def send_status_update(self, led_status: str, additional_data: Dict = None):
        """Send status update to orchestrator."""
        status_msg = StatusUpdateMessage.create(
            agent_id=self.agent_id,
            led_status=led_status,
            additional_data=additional_data
        )
        await self._send_raw_message(status_msg.to_dict())
    
    async def send_event(self, event_type: str, event_data: Dict = None):
        """Send event to orchestrator."""
        event_msg = EventMessage.create(
            agent_id=self.agent_id,
            event_type=event_type,
            event_data=event_data
        )
        await self._send_raw_message(event_msg.to_dict())
    
    async def _listen_loop(self):
        """Listen for messages from orchestrator with reconnection."""
        logger.info("Started listening for orchestrator messages")
        
        try:
            while self.is_connected and self.websocket:
                try:
                    message = await self.websocket.recv()
                    await self._handle_raw_message(message)
                    
                except ConnectionClosed:
                    logger.warning("Connection closed by orchestrator")
                    self.is_connected = False
                    break
                    
                except ConnectionClosedError:
                    logger.warning("Connection closed unexpectedly")
                    self.is_connected = False
                    break
                    
        except Exception as e:
            logger.error(f"Error in listen loop: {e}")
            self.is_connected = False
        
        # Attempt reconnection if enabled
        if self.should_reconnect and not self.is_connected:
            logger.info("Attempting to reconnect...")
            asyncio.create_task(self._reconnect())
    
    async def _reconnect(self):
        """Attempt to reconnect to orchestrator."""
        await asyncio.sleep(self.reconnect_delay)
        if self.should_reconnect:
            await self.connect()
    
    async def _handle_raw_message(self, message: str):
        """Handle incoming raw message."""
        try:
            data = json.loads(message)
            self.stats["messages_received"] += 1
            
            message_type = data.get("message_type")
            logger.debug(f"Received message: {message_type}")
            
            # Handle ping messages automatically
            if message_type == "ping":
                await self._handle_ping(data)
                return
            
            # Handle specific message types
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](data)
            else:
                logger.warning(f"No handler for message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _handle_ping(self, data: Dict[str, Any]):
        """Handle ping from orchestrator."""
        await self._send_raw_message({
            "message_type": "pong",
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "payload": {"status": "active"}
        })
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat to orchestrator."""
        logger.info("Started heartbeat loop")
        
        while self.is_connected and self.should_reconnect:
            try:
                uptime = time.time() - self.stats["connection_start_time"] if self.stats["connection_start_time"] else 0
                
                await self._send_raw_message({
                    "message_type": "heartbeat",
                    "agent_id": self.agent_id,
                    "timestamp": time.time(),
                    "payload": {
                        "status": "active",
                        "uptime": uptime,
                        "stats": self.stats
                    }
                })
                
                self.stats["last_heartbeat"] = time.time()
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(30)
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        uptime = time.time() - self.stats["connection_start_time"] if self.stats["connection_start_time"] else 0
        
        return {
            **self.stats,
            "is_connected": self.is_connected,
            "reconnect_attempts": self.reconnect_attempts,
            "queued_messages": len(self.message_queue),
            "uptime": uptime
        }
    
    def is_ready(self) -> bool:
        """Check if client is ready for communication."""
        return self.is_connected and self.websocket is not None
