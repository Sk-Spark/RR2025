#!/usr/bin/env python3
"""
Message Protocol Definition
Defines the WebSocket communication protocol between RPi agent and orchestrator.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
import json
import time
import uuid
from enum import Enum


class MessageType(Enum):
    """Enumeration of message types."""
    REGISTER = "register"
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    STATUS_UPDATE = "status_update"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    EVENT = "event"


class Priority(Enum):
    """Command priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class BaseMessage:
    """Base message structure."""
    message_type: str
    agent_id: str
    timestamp: float
    payload: Dict[str, Any]
    message_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate message ID if not provided."""
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class RegistrationMessage(BaseMessage):
    """Agent registration message."""
    
    @classmethod
    def create(cls, agent_id: str, capabilities: List[str], 
               location: str = "", agent_type: str = "rpi_bot_controller"):
        """Create registration message."""
        return cls(
            message_type=MessageType.REGISTER.value,
            agent_id=agent_id,
            timestamp=time.time(),
            payload={
                "agent_type": agent_type,
                "capabilities": capabilities,
                "location": location,
                "hardware": "raspberry_pi",
                "version": "1.0.0"
            }
        )


@dataclass
class CommandMessage(BaseMessage):
    """Command message from orchestrator to agent."""
    
    @classmethod
    def create(cls, agent_id: str, command: str, request_id: str,
               priority: Priority = Priority.NORMAL, context: Dict = None):
        """Create command message."""
        return cls(
            message_type=MessageType.COMMAND.value,
            agent_id=agent_id,
            timestamp=time.time(),
            payload={
                "request_id": request_id,
                "command": command,
                "priority": priority.value,
                "context": context or {}
            }
        )


@dataclass
class ResponseMessage(BaseMessage):
    """Response message from agent to orchestrator."""
    
    @classmethod
    def create(cls, agent_id: str, request_id: str, success: bool,
               response: str = "", data: Dict = None, error: str = ""):
        """Create response message."""
        return cls(
            message_type=MessageType.RESPONSE.value,
            agent_id=agent_id,
            timestamp=time.time(),
            payload={
                "request_id": request_id,
                "success": success,
                "response": response,
                "data": data or {},
                "error": error
            }
        )


@dataclass
class StatusUpdateMessage(BaseMessage):
    """Status update message from agent."""
    
    @classmethod
    def create(cls, agent_id: str, led_status: str, additional_data: Dict = None):
        """Create status update message."""
        return cls(
            message_type=MessageType.STATUS_UPDATE.value,
            agent_id=agent_id,
            timestamp=time.time(),
            payload={
                "led_status": led_status,
                "agent_status": "active",
                "uptime": time.time(),
                "additional_data": additional_data or {}
            }
        )


@dataclass
class QueryMessage(BaseMessage):
    """Query message from orchestrator."""
    
    @classmethod
    def create(cls, agent_id: str, query_type: str, request_id: str,
               parameters: Dict = None):
        """Create query message."""
        return cls(
            message_type=MessageType.QUERY.value,
            agent_id=agent_id,
            timestamp=time.time(),
            payload={
                "request_id": request_id,
                "query_type": query_type,  # "status", "capabilities", "logs"
                "parameters": parameters or {}
            }
        )


@dataclass
class EventMessage(BaseMessage):
    """Event message from agent."""
    
    @classmethod
    def create(cls, agent_id: str, event_type: str, event_data: Dict = None):
        """Create event message."""
        return cls(
            message_type=MessageType.EVENT.value,
            agent_id=agent_id,
            timestamp=time.time(),
            payload={
                "event_type": event_type,
                "event_data": event_data or {}
            }
        )


# Protocol Examples for reference
EXAMPLE_MESSAGES = {
    "registration": {
        "message_type": "register",
        "agent_id": "rpi_bedroom_led",
        "timestamp": 1720872345.123,
        "message_id": "msg_001",
        "payload": {
            "agent_type": "rpi_bot_controller",
            "capabilities": ["led_control", "movement_control", "status_monitoring", "natural_language_processing"],
            "location": "bedroom",
            "hardware": "raspberry_pi_5",
            "version": "1.0.0"
        }
    },
    
    "command_from_orchestrator": {
        "message_type": "command",
        "agent_id": "rpi_bedroom_led",
        "timestamp": 1720872400.456,
        "message_id": "msg_002",
        "payload": {
            "request_id": "cmd_001",
            "command": "turn on the LED with a gentle fade",
            "priority": "normal",
            "context": {
                "user": "homeowner",
                "reason": "bedtime_routine"
            }
        }
    },
    
    "response_to_orchestrator": {
        "message_type": "response",
        "agent_id": "rpi_bedroom_led",
        "timestamp": 1720872401.789,
        "message_id": "msg_003",
        "payload": {
            "request_id": "cmd_001",
            "success": True,
            "response": "LED turned on successfully with gentle fade effect",
            "data": {
                "led_status": "on",
                "brightness": 80,
                "action_duration": "2.3s"
            }
        }
    }
}
