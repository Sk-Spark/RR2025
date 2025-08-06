#!/usr/bin/env python3
"""
Message Protocol for DummyAiBot
Defines message types and structures for communication with orchestrator
"""

import json
import time
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional, List


class MessageType(Enum):
    """Enumeration of message types."""
    REGISTRATION = "registration"
    COMMAND = "command"
    RESPONSE = "response"
    STATUS_UPDATE = "status_update"
    EVENT = "event"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    ACK = "ack"


@dataclass
class BaseMessage:
    """Base class for all messages."""
    message_type: str
    message_id: str
    timestamp: float
    agent_id: str
    
    def __post_init__(self):
        """Ensure message_id and timestamp are set."""
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create message from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class RegistrationMessage(BaseMessage):
    """Message for agent registration with orchestrator."""
    agent_name: str
    agent_description: str
    capabilities: List[str]
    status: str = "online"
    message_type: str = MessageType.REGISTRATION.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""


@dataclass
class CommandMessage(BaseMessage):
    """Message for sending commands to agent."""
    command: str
    parameters: Dict[str, Any]
    priority: int = 1
    requires_response: bool = True
    timeout: float = 30.0
    message_type: str = MessageType.COMMAND.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""


@dataclass
class ResponseMessage(BaseMessage):
    """Message for responding to commands."""
    command_id: str
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    message_type: str = MessageType.RESPONSE.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""


@dataclass
class StatusUpdateMessage(BaseMessage):
    """Message for status updates."""
    status: str
    details: Dict[str, Any]
    health_score: float = 1.0
    message_type: str = MessageType.STATUS_UPDATE.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""


@dataclass
class EventMessage(BaseMessage):
    """Message for events."""
    event_type: str
    data: Dict[str, Any]
    severity: str = "info"
    message_type: str = MessageType.EVENT.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""


@dataclass
class HeartbeatMessage(BaseMessage):
    """Message for heartbeat."""
    status: str = "alive"
    system_info: Dict[str, Any] = None
    message_type: str = MessageType.HEARTBEAT.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        if self.system_info is None:
            self.system_info = {}


@dataclass
class ErrorMessage(BaseMessage):
    """Message for errors."""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = None
    message_type: str = MessageType.ERROR.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        if self.context is None:
            self.context = {}


@dataclass
class AckMessage(BaseMessage):
    """Message for acknowledgment."""
    ack_message_id: str
    message_type: str = MessageType.ACK.value
    message_id: str = ""
    timestamp: float = 0.0
    agent_id: str = ""


class MessageFactory:
    """Factory for creating messages."""
    
    @staticmethod
    def create_registration(agent_id: str, agent_name: str, agent_description: str, 
                          capabilities: List[str]) -> RegistrationMessage:
        """Create a registration message."""
        return RegistrationMessage(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_description=agent_description,
            capabilities=capabilities
        )
    
    @staticmethod
    def create_command(agent_id: str, command: str, parameters: Dict[str, Any], 
                      priority: int = 1, requires_response: bool = True,
                      timeout: float = 30.0) -> CommandMessage:
        """Create a command message."""
        return CommandMessage(
            agent_id=agent_id,
            command=command,
            parameters=parameters,
            priority=priority,
            requires_response=requires_response,
            timeout=timeout
        )
    
    @staticmethod
    def create_response(agent_id: str, command_id: str, success: bool, 
                       result: Any, error_message: Optional[str] = None,
                       execution_time: float = 0.0) -> ResponseMessage:
        """Create a response message."""
        return ResponseMessage(
            agent_id=agent_id,
            command_id=command_id,
            success=success,
            result=result,
            error_message=error_message,
            execution_time=execution_time
        )
    
    @staticmethod
    def create_status_update(agent_id: str, status: str, details: Dict[str, Any],
                           health_score: float = 1.0) -> StatusUpdateMessage:
        """Create a status update message."""
        return StatusUpdateMessage(
            agent_id=agent_id,
            status=status,
            details=details,
            health_score=health_score
        )
    
    @staticmethod
    def create_event(agent_id: str, event_type: str, data: Dict[str, Any],
                    severity: str = "info") -> EventMessage:
        """Create an event message."""
        return EventMessage(
            agent_id=agent_id,
            event_type=event_type,
            data=data,
            severity=severity
        )
    
    @staticmethod
    def create_heartbeat(agent_id: str, status: str = "alive",
                        system_info: Dict[str, Any] = None) -> HeartbeatMessage:
        """Create a heartbeat message."""
        return HeartbeatMessage(
            agent_id=agent_id,
            status=status,
            system_info=system_info or {}
        )
    
    @staticmethod
    def create_error(agent_id: str, error_type: str, error_message: str,
                    stack_trace: Optional[str] = None,
                    context: Dict[str, Any] = None) -> ErrorMessage:
        """Create an error message."""
        return ErrorMessage(
            agent_id=agent_id,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context or {}
        )
    
    @staticmethod
    def create_ack(agent_id: str, ack_message_id: str) -> AckMessage:
        """Create an acknowledgment message."""
        return AckMessage(
            agent_id=agent_id,
            ack_message_id=ack_message_id
        )
    
    @staticmethod
    def from_json(json_str: str) -> BaseMessage:
        """Create message from JSON string."""
        try:
            data = json.loads(json_str)
            message_type = data.get('message_type')
            
            if message_type == MessageType.REGISTRATION.value:
                return RegistrationMessage.from_dict(data)
            elif message_type == MessageType.COMMAND.value:
                return CommandMessage.from_dict(data)
            elif message_type == MessageType.RESPONSE.value:
                return ResponseMessage.from_dict(data)
            elif message_type == MessageType.STATUS_UPDATE.value:
                return StatusUpdateMessage.from_dict(data)
            elif message_type == MessageType.EVENT.value:
                return EventMessage.from_dict(data)
            elif message_type == MessageType.HEARTBEAT.value:
                return HeartbeatMessage.from_dict(data)
            elif message_type == MessageType.ERROR.value:
                return ErrorMessage.from_dict(data)
            elif message_type == MessageType.ACK.value:
                return AckMessage.from_dict(data)
            else:
                raise ValueError(f"Unknown message type: {message_type}")
                
        except Exception as e:
            raise ValueError(f"Failed to parse message: {e}")


def validate_message(message_data: Dict[str, Any]) -> bool:
    """
    Validate message structure
    
    Args:
        message_data: Message data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['message_type', 'message_id', 'timestamp', 'agent_id']
    
    # Check required fields
    for field in required_fields:
        if field not in message_data:
            return False
    
    # Check message type
    message_type = message_data.get('message_type')
    valid_types = [t.value for t in MessageType]
    if message_type not in valid_types:
        return False
    
    return True
