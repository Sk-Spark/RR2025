#!/usr/bin/env python3
"""
Message Protocol for DummyAiBot - Testing Communication
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class MessageType(Enum):
    """Message types for bot communication"""
    REGISTER = "register"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    LOG = "log"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Message:
    """Base message class for bot communication"""
    
    def __init__(self, message_type: MessageType, data: Dict[str, Any] = None,
                 message_id: str = None, timestamp: str = None):
        self.message_id = message_id or str(uuid.uuid4())
        self.message_type = message_type
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'timestamp': self.timestamp,
            'data': self.data
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            message_type=MessageType(data['message_type']),
            data=data.get('data', {}),
            message_id=data.get('message_id'),
            timestamp=data.get('timestamp')
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class RegistrationMessage(Message):
    """Message for bot registration with orchestrator"""
    
    def __init__(self, bot_id: str, bot_name: str, capabilities: list, **kwargs):
        data = {
            'bot_id': bot_id,
            'bot_name': bot_name,
            'capabilities': capabilities,
            **kwargs
        }
        super().__init__(MessageType.REGISTER, data)


class TaskRequestMessage(Message):
    """Message for task requests from orchestrator"""
    
    def __init__(self, task_id: str, task_type: str, task_description: str,
                 parameters: Dict[str, Any] = None, **kwargs):
        data = {
            'task_id': task_id,
            'task_type': task_type,
            'task_description': task_description,
            'parameters': parameters or {},
            **kwargs
        }
        super().__init__(MessageType.TASK_REQUEST, data)


class TaskResponseMessage(Message):
    """Message for task responses to orchestrator"""
    
    def __init__(self, task_id: str, status: TaskStatus, result: Any = None,
                 error_message: str = None, **kwargs):
        data = {
            'task_id': task_id,
            'status': status.value,
            'result': result,
            'error_message': error_message,
            **kwargs
        }
        super().__init__(MessageType.TASK_RESPONSE, data)


class StatusUpdateMessage(Message):
    """Message for status updates to orchestrator"""
    
    def __init__(self, bot_status: str, current_task: str = None,
                 system_info: Dict[str, Any] = None, **kwargs):
        data = {
            'bot_status': bot_status,
            'current_task': current_task,
            'system_info': system_info or {},
            **kwargs
        }
        super().__init__(MessageType.STATUS_UPDATE, data)


class HeartbeatMessage(Message):
    """Heartbeat message to keep connection alive"""
    
    def __init__(self, bot_id: str, **kwargs):
        data = {
            'bot_id': bot_id,
            **kwargs
        }
        super().__init__(MessageType.HEARTBEAT, data)


class ErrorMessage(Message):
    """Error message for communication issues"""
    
    def __init__(self, error_code: str, error_message: str, context: Dict[str, Any] = None, **kwargs):
        data = {
            'error_code': error_code,
            'error_message': error_message,
            'context': context or {},
            **kwargs
        }
        super().__init__(MessageType.ERROR, data)


def create_registration_message(config) -> RegistrationMessage:
    """Create a registration message from bot config"""
    return RegistrationMessage(
        bot_id=config.agent_id,
        bot_name=config.agent_name,
        capabilities=config.capabilities,
        bot_type=getattr(config, 'bot_type', 'test_agent')
    )


def create_heartbeat_message(bot_id: str) -> HeartbeatMessage:
    """Create a heartbeat message"""
    return HeartbeatMessage(bot_id=bot_id)


def create_status_update_message(bot_id: str, status: str, task: str = None) -> StatusUpdateMessage:
    """Create a status update message"""
    return StatusUpdateMessage(
        bot_status=status,
        current_task=task,
        system_info={'bot_id': bot_id}
    )
