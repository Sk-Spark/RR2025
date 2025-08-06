"""
Message router for handling and routing different types of messages.
Provides centralized message processing and routing logic.
"""

import asyncio
from typing import Dict, Callable, Any, Optional
from datetime import datetime

from ..core.models import (
    Message, MessageType, AgentRegistration, Heartbeat,
    TaskAssignment, TaskUpdate, TaskResult, Agent
)
from ..agents import AgentManager, TaskManager
from ..utils import get_logger, log_websocket_event, format_error_message


class MessageRouter:
    """
    Routes and processes different types of messages from agents.
    Acts as the central message processing hub for the orchestrator.
    """
    
    def __init__(self, agent_manager: AgentManager, task_manager: TaskManager):
        """
        Initialize the message router.
        
        Args:
            agent_manager: Agent manager instance
            task_manager: Task manager instance
        """
        self.agent_manager = agent_manager
        self.task_manager = task_manager
        self.logger = get_logger(__name__)
        
        # Message processing statistics
        self._messages_processed = 0
        self._processing_errors = 0
        
        # Response callbacks
        self._response_callbacks: Dict[str, Callable] = {}
        
        self.logger.info("MessageRouter initialized")
    
    async def route_message(self, message: Message, connection_id: str) -> Optional[Message]:
        """
        Route a message to the appropriate handler.
        
        Args:
            message: Message to route
            connection_id: WebSocket connection ID
            
        Returns:
            Optional response message
        """
        try:
            self._messages_processed += 1
            
            # Route based on message type
            if message.message_type == MessageType.REGISTER_AGENT:
                return await self._handle_agent_registration(message, connection_id)
            
            elif message.message_type == MessageType.HEARTBEAT:
                return await self._handle_heartbeat(message, connection_id)
            
            elif message.message_type == MessageType.TASK_UPDATE:
                return await self._handle_task_update(message, connection_id)
            
            elif message.message_type == MessageType.TASK_RESULT:
                return await self._handle_task_result(message, connection_id)
            
            elif message.message_type == MessageType.CAPABILITY_UPDATE:
                return await self._handle_capability_update(message, connection_id)
            
            elif message.message_type == MessageType.STATUS_UPDATE:
                return await self._handle_status_update(message, connection_id)
            
            else:
                self.logger.warning(f"Unhandled message type: {message.message_type.value}")
                return self._create_error_response(
                    message, 
                    f"Unhandled message type: {message.message_type.value}"
                )
        
        except Exception as e:
            self._processing_errors += 1
            self.logger.error(f"Error routing message: {format_error_message(e)}")
            return self._create_error_response(message, f"Routing error: {e}")
    
    async def _handle_agent_registration(self, message: Message, connection_id: str) -> Optional[Message]:
        """Handle agent registration message."""
        try:
            # Parse registration data
            payload = message.payload
            
            # Create agent from payload
            agent_data = payload.get('agent', {})
            if not agent_data:
                return self._create_error_response(message, "Missing agent data in registration")
            
            # Convert to Agent object
            agent = Agent(**agent_data)
            registration = AgentRegistration(
                agent=agent,
                connection_info=payload.get('connection_info', {})
            )
            
            # Register with agent manager
            success = await self.agent_manager.register_agent(registration, connection_id)
            
            if success:
                self.logger.info(f"Successfully registered agent {agent.agent_id}")
                return self._create_success_response(
                    message, 
                    {
                        'status': 'registered',
                        'agent_id': agent.agent_id,
                        'registered_at': datetime.utcnow().isoformat()
                    }
                )
            else:
                return self._create_error_response(message, "Failed to register agent")
        
        except Exception as e:
            self.logger.error(f"Error handling agent registration: {e}")
            return self._create_error_response(message, f"Registration error: {e}")
    
    async def _handle_heartbeat(self, message: Message, connection_id: str) -> Optional[Message]:
        """Handle heartbeat message."""
        try:
            # Parse heartbeat data
            payload = message.payload
            heartbeat = Heartbeat(**payload)
            
            # Process with agent manager
            success = await self.agent_manager.handle_heartbeat(heartbeat, connection_id)
            
            if success:
                # Send heartbeat acknowledgment
                return self._create_success_response(
                    message,
                    {
                        'status': 'heartbeat_received',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
            else:
                return self._create_error_response(message, "Failed to process heartbeat")
        
        except Exception as e:
            self.logger.error(f"Error handling heartbeat: {e}")
            return self._create_error_response(message, f"Heartbeat error: {e}")
    
    async def _handle_task_update(self, message: Message, connection_id: str) -> Optional[Message]:
        """Handle task update message."""
        try:
            # Parse task update data
            payload = message.payload
            task_update = TaskUpdate(**payload)
            
            # Process with task manager
            success = await self.task_manager.update_task_progress(task_update)
            
            if success:
                self.logger.info(f"Task {task_update.task_id} updated by agent {message.sender_id}")
                return self._create_success_response(
                    message,
                    {
                        'status': 'task_update_received',
                        'task_id': task_update.task_id
                    }
                )
            else:
                return self._create_error_response(message, f"Failed to update task {task_update.task_id}")
        
        except Exception as e:
            self.logger.error(f"Error handling task update: {e}")
            return self._create_error_response(message, f"Task update error: {e}")
    
    async def _handle_task_result(self, message: Message, connection_id: str) -> Optional[Message]:
        """Handle task result message."""
        try:
            # Parse task result data
            payload = message.payload
            task_result = TaskResult(**payload)
            
            # Process with task manager
            success = await self.task_manager.complete_task(task_result)
            
            if success:
                self.logger.info(f"Task {task_result.task_id} completed by agent {message.sender_id}")
                return self._create_success_response(
                    message,
                    {
                        'status': 'task_result_received',
                        'task_id': task_result.task_id
                    }
                )
            else:
                return self._create_error_response(message, f"Failed to process task result {task_result.task_id}")
        
        except Exception as e:
            self.logger.error(f"Error handling task result: {e}")
            return self._create_error_response(message, f"Task result error: {e}")
    
    async def _handle_capability_update(self, message: Message, connection_id: str) -> Optional[Message]:
        """Handle capability update message."""
        try:
            # Get agent
            agent = self.agent_manager.get_agent_by_websocket(connection_id)
            if not agent:
                return self._create_error_response(message, "Agent not found")
            
            # Update capabilities
            payload = message.payload
            new_capabilities = payload.get('capabilities', [])
            
            # Convert to AgentCapability objects
            from ..core.models import AgentCapability
            capabilities = [AgentCapability(**cap_data) for cap_data in new_capabilities]
            
            # Update agent capabilities
            agent.capabilities = capabilities
            
            self.logger.info(f"Updated capabilities for agent {agent.agent_id}")
            return self._create_success_response(
                message,
                {
                    'status': 'capabilities_updated',
                    'capability_count': len(capabilities)
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error handling capability update: {e}")
            return self._create_error_response(message, f"Capability update error: {e}")
    
    async def _handle_status_update(self, message: Message, connection_id: str) -> Optional[Message]:
        """Handle status update message."""
        try:
            # Get agent
            agent = self.agent_manager.get_agent_by_websocket(connection_id)
            if not agent:
                return self._create_error_response(message, "Agent not found")
            
            # Update status
            payload = message.payload
            from ..core.models import AgentStatus
            new_status = AgentStatus(payload.get('status'))
            
            success = await self.agent_manager.update_agent_status(agent.agent_id, new_status)
            
            if success:
                self.logger.info(f"Updated status for agent {agent.agent_id} to {new_status.value}")
                return self._create_success_response(
                    message,
                    {
                        'status': 'agent_status_updated',
                        'new_status': new_status.value
                    }
                )
            else:
                return self._create_error_response(message, "Failed to update agent status")
        
        except Exception as e:
            self.logger.error(f"Error handling status update: {e}")
            return self._create_error_response(message, f"Status update error: {e}")
    
    def _create_success_response(self, original_message: Message, payload: Dict[str, Any]) -> Message:
        """Create a success response message."""
        from ..utils import generate_unique_id
        
        return Message(
            message_id=generate_unique_id("msg"),
            message_type=MessageType.STATUS_UPDATE,
            sender_id="orchestrator",
            recipient_id=original_message.sender_id,
            payload=payload,
            correlation_id=original_message.message_id
        )
    
    def _create_error_response(self, original_message: Message, error_message: str) -> Message:
        """Create an error response message."""
        from ..utils import generate_unique_id
        
        return Message(
            message_id=generate_unique_id("msg"),
            message_type=MessageType.ERROR,
            sender_id="orchestrator",
            recipient_id=original_message.sender_id,
            payload={
                'error': error_message,
                'original_message_id': original_message.message_id
            },
            correlation_id=original_message.message_id
        )
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get message routing statistics."""
        return {
            'messages_processed': self._messages_processed,
            'processing_errors': self._processing_errors,
            'error_rate': self._processing_errors / max(self._messages_processed, 1)
        }
    
    def add_response_callback(self, correlation_id: str, callback: Callable) -> None:
        """Add a callback for a specific message response."""
        self._response_callbacks[correlation_id] = callback
    
    def remove_response_callback(self, correlation_id: str) -> None:
        """Remove a response callback."""
        self._response_callbacks.pop(correlation_id, None)
