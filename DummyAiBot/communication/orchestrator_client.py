#!/usr/bin/env python3
"""
Orchestrator Client for DummyAiBot - Testing WebSocket Communication
"""

import asyncio
import logging
import websockets
import json
from typing import Optional, Callable, Any
from communication.protocol import (
    Message, MessageType, RegistrationMessage, HeartbeatMessage,
    TaskRequestMessage, TaskResponseMessage, StatusUpdateMessage,
    create_registration_message, create_heartbeat_message
)

logger = logging.getLogger(__name__)


class OrchestratorClient:
    """Simple WebSocket client for connecting to orchestrator"""
    
    def __init__(self, config, message_handler: Optional[Callable] = None):
        self.config = config
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.message_handler = message_handler
        self.heartbeat_task = None
        self.reconnect_task = None
        self._running = False
        
    async def connect(self) -> bool:
        """Connect to orchestrator WebSocket"""
        try:
            logger.info(f"Connecting to orchestrator at {self.config.orchestrator_url}")
            
            self.websocket = await websockets.connect(
                self.config.orchestrator_url,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.connected = True
            logger.info("Connected to orchestrator")
            
            # Register with orchestrator
            await self._register()
            
            # Start heartbeat
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to orchestrator: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from orchestrator"""
        self._running = False
        self.connected = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            
        if self.reconnect_task:
            self.reconnect_task.cancel()
            
        if self.websocket:
            await self.websocket.close()
            
        logger.info("Disconnected from orchestrator")
    
    async def send_message(self, message: Message) -> bool:
        """Send message to orchestrator"""
        if not self.connected or not self.websocket:
            logger.error("Not connected to orchestrator")
            return False
        
        try:
            await self.websocket.send(message.to_json())
            logger.debug(f"Sent message: {message.message_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.connected = False
            return False
    
    async def listen(self):
        """Listen for messages from orchestrator"""
        self._running = True
        
        while self._running:
            try:
                if not self.connected:
                    await self._reconnect()
                    continue
                
                # Listen for incoming messages
                message_str = await self.websocket.recv()
                message = Message.from_json(message_str)
                
                logger.debug(f"Received message: {message.message_type.value}")
                
                # Handle message
                if self.message_handler:
                    await self.message_handler(message)
                else:
                    await self._default_message_handler(message)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                self.connected = False
                
            except Exception as e:
                logger.error(f"Error in message listener: {e}")
                await asyncio.sleep(1)
    
    async def _register(self):
        """Register bot with orchestrator"""
        try:
            registration_msg = create_registration_message(self.config)
            await self.send_message(registration_msg)
            logger.info(f"Registered bot {self.config.agent_id} with orchestrator")
            
        except Exception as e:
            logger.error(f"Failed to register with orchestrator: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.connected and self._running:
            try:
                heartbeat_msg = create_heartbeat_message(self.config.agent_id)
                await self.send_message(heartbeat_msg)
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                break
    
    async def _reconnect(self):
        """Attempt to reconnect to orchestrator"""
        if self.reconnect_task and not self.reconnect_task.done():
            return
        
        self.reconnect_task = asyncio.create_task(self._reconnect_loop())
        await self.reconnect_task
    
    async def _reconnect_loop(self):
        """Reconnection loop with exponential backoff"""
        attempt = 0
        max_attempts = self.config.max_reconnect_attempts
        
        while self._running and (max_attempts == -1 or attempt < max_attempts):
            try:
                attempt += 1
                logger.info(f"Reconnection attempt {attempt}")
                
                if await self.connect():
                    logger.info("Reconnected successfully")
                    return
                    
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt} failed: {e}")
            
            # Wait before next attempt
            wait_time = min(self.config.reconnect_interval * (2 ** min(attempt-1, 5)), 60)
            await asyncio.sleep(wait_time)
        
        if max_attempts != -1 and attempt >= max_attempts:
            logger.error(f"Max reconnection attempts ({max_attempts}) reached")
    
    async def _default_message_handler(self, message: Message):
        """Default message handler"""
        logger.info(f"Received {message.message_type.value} message: {message.data}")
        
        if message.message_type == MessageType.TASK_REQUEST:
            # Simple acknowledgment for testing
            task_id = message.data.get('task_id')
            response = TaskResponseMessage(
                task_id=task_id,
                status='completed',
                result='Task completed by dummy bot'
            )
            await self.send_message(response)
    
    async def send_status_update(self, status: str, current_task: str = None):
        """Send status update to orchestrator"""
        status_msg = StatusUpdateMessage(
            bot_status=status,
            current_task=current_task,
            system_info={'bot_id': self.config.agent_id}
        )
        await self.send_message(status_msg)
    
    async def send_task_response(self, task_id: str, status: str, result: Any = None, error: str = None):
        """Send task response to orchestrator"""
        response_msg = TaskResponseMessage(
            task_id=task_id,
            status=status,
            result=result,
            error_message=error
        )
        await self.send_message(response_msg)
