"""
Base test agent implementation that provides common functionality
for all test dummy AI bot agents.
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseTestAgent(ABC):
    """Base class for all test agents"""
    
    def __init__(self, agent_id: str, agent_name: str, agent_type: str, capabilities: List[str]):
        """
        Initialize base test agent
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
            agent_type: Type of agent (movement, camera, sensor, etc.)
            capabilities: List of capabilities this agent provides
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.websocket = None
        self.is_connected = False
        self.orchestrator_url = "ws://localhost:8080"
        self.logger = logging.getLogger(f"TestAgent-{agent_name}")
        self.task_queue = asyncio.Queue()
        self.current_task = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def connect_to_orchestrator(self):
        """Connect to the orchestrator via WebSocket"""
        try:
            self.websocket = await websockets.connect(self.orchestrator_url)
            self.is_connected = True
            self.logger.info(f"Connected to orchestrator at {self.orchestrator_url}")
            
            # Register with orchestrator
            await self._register_agent()
            
            # Start listening for messages
            await asyncio.gather(
                self._listen_for_tasks(),
                self._process_tasks()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to connect to orchestrator: {e}")
            self.is_connected = False
    
    async def _register_agent(self):
        """Register this agent with the orchestrator"""
        registration_message = {
            "message_type": "register_agent",
            "sender_id": self.agent_id,
            "payload": {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "capabilities": self.capabilities,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        await self.websocket.send(json.dumps(registration_message))
        self.logger.info(f"Registered agent {self.agent_name} with orchestrator")
    
    async def _listen_for_tasks(self):
        """Listen for incoming tasks from orchestrator"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.task_queue.put(data)
                    self.logger.info(f"Received task: {data.get('type', 'unknown')}")
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection to orchestrator closed")
            self.is_connected = False
    
    async def _process_tasks(self):
        """Process tasks from the queue"""
        while True:
            try:
                task = await self.task_queue.get()
                await self._handle_task(task)
            except Exception as e:
                self.logger.error(f"Error processing task: {e}")
    
    async def _handle_task(self, task: Dict[str, Any]):
        """Handle incoming task based on type"""
        task_type = task.get("type")
        
        if task_type == "execute":
            await self._execute_task(task)
        elif task_type == "status_request":
            await self._send_status()
        elif task_type == "ping":
            await self._send_pong()
        else:
            self.logger.warning(f"Unknown task type: {task_type}")
    
    async def _execute_task(self, task: Dict[str, Any]):
        """Execute a task and send result back to orchestrator"""
        task_id = task.get("task_id")
        command = task.get("command")
        parameters = task.get("parameters", {})
        
        self.current_task = task_id
        self.logger.info(f"Executing task {task_id}: {command}")
        
        try:
            # Simulate task execution
            result = await self.execute_command(command, parameters)
            
            # Send success response
            response = {
                "message_type": "task_result",
                "sender_id": self.agent_id,
                "payload": {
                    "task_id": task_id,
                    "agent_id": self.agent_id,
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            # Send error response
            response = {
                "message_type": "task_result",
                "sender_id": self.agent_id,
                "payload": {
                    "task_id": task_id,
                    "agent_id": self.agent_id,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
            self.logger.error(f"Task {task_id} failed: {e}")
        
        finally:
            self.current_task = None
            await self.websocket.send(json.dumps(response))
    
    async def _send_status(self):
        """Send current status to orchestrator"""
        status = {
            "message_type": "status_update",
            "sender_id": self.agent_id,
            "payload": {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "capabilities": self.capabilities,
                "is_busy": self.current_task is not None,
                "current_task": self.current_task,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        await self.websocket.send(json.dumps(status))
    
    async def _send_pong(self):
        """Respond to ping with pong"""
        pong = {
            "message_type": "pong",
            "sender_id": self.agent_id,
            "payload": {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        await self.websocket.send(json.dumps(pong))
    
    @abstractmethod
    async def execute_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command specific to this agent type
        
        Args:
            command: The command to execute
            parameters: Parameters for the command
            
        Returns:
            Result of the command execution
        """
        pass
    
    async def disconnect(self):
        """Disconnect from orchestrator"""
        if self.websocket and self.is_connected:
            await self.websocket.close()
            self.is_connected = False
            self.logger.info("Disconnected from orchestrator")
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.agent_name}, type={self.agent_type})>"
