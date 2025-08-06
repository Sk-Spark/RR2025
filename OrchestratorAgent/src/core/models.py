"""
Core data models for the Orchestrator Agent.
Defines the structure for agents, tasks, messages, and other core entities.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class AgentStatus(Enum):
    """Enumeration of possible agent statuses."""
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class TaskStatus(Enum):
    """Enumeration of possible task statuses."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(Enum):
    """Enumeration of message types for communication."""
    REGISTER_AGENT = "register_agent"
    HEARTBEAT = "heartbeat"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_RESULT = "task_result"
    CAPABILITY_UPDATE = "capability_update"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class AgentCapability(BaseModel):
    """Represents a capability that an agent can perform."""
    
    name: str = Field(..., description="Name of the capability")
    description: str = Field(..., description="Description of what this capability does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Required parameters for this capability")
    category: str = Field(default="general", description="Category of the capability")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    requirements: List[str] = Field(default_factory=list, description="Any specific requirements or dependencies")


class Agent(BaseModel):
    """Represents an AI agent in the system."""
    
    agent_id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human-readable name of the agent")
    agent_type: str = Field(..., description="Type of agent (e.g., 'movement', 'camera', 'sensor')")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="List of agent capabilities")
    status: AgentStatus = Field(default=AgentStatus.OFFLINE, description="Current status of the agent")
    last_seen: Optional[datetime] = Field(None, description="Last time the agent was seen")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the agent")
    websocket_id: Optional[str] = Field(None, description="WebSocket connection ID")
    location: Optional[str] = Field(None, description="Physical location of the agent")
    version: Optional[str] = Field(None, description="Agent software version")


class Task(BaseModel):
    """Represents a task to be executed by an agent."""
    
    task_id: str = Field(..., description="Unique identifier for the task")
    name: str = Field(..., description="Human-readable name of the task")
    description: str = Field(..., description="Detailed description of the task")
    capability_required: str = Field(..., description="Required capability to execute this task")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for task execution")
    assigned_agent_id: Optional[str] = Field(None, description="ID of the agent assigned to this task")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task")
    priority: int = Field(default=5, description="Task priority (1-10, higher is more urgent)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    timeout_seconds: Optional[int] = Field(None, description="Task timeout in seconds")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this task depends on")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class Message(BaseModel):
    """Represents a message in the communication protocol."""
    
    message_id: str = Field(..., description="Unique identifier for the message")
    message_type: MessageType = Field(..., description="Type of the message")
    sender_id: str = Field(..., description="ID of the message sender")
    recipient_id: Optional[str] = Field(None, description="ID of the message recipient (None for broadcast)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload data")
    correlation_id: Optional[str] = Field(None, description="ID to correlate request/response messages")


class AgentRegistration(BaseModel):
    """Message payload for agent registration."""
    
    agent: Agent = Field(..., description="Agent information")
    connection_info: Dict[str, Any] = Field(default_factory=dict, description="Connection-specific information")


class TaskAssignment(BaseModel):
    """Message payload for task assignment."""
    
    task: Task = Field(..., description="Task to be assigned")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    additional_instructions: Optional[str] = Field(None, description="Additional instructions for the agent")


class TaskUpdate(BaseModel):
    """Message payload for task status updates."""
    
    task_id: str = Field(..., description="ID of the task being updated")
    status: TaskStatus = Field(..., description="New status of the task")
    progress_percentage: Optional[int] = Field(None, description="Progress percentage (0-100)")
    message: Optional[str] = Field(None, description="Update message")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")


class TaskResult(BaseModel):
    """Message payload for task completion results."""
    
    task_id: str = Field(..., description="ID of the completed task")
    status: TaskStatus = Field(..., description="Final status of the task")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result data")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    execution_time_seconds: Optional[float] = Field(None, description="Task execution time in seconds")
    logs: Optional[List[str]] = Field(None, description="Execution logs")


class Heartbeat(BaseModel):
    """Message payload for agent heartbeat."""
    
    agent_id: str = Field(..., description="ID of the agent sending heartbeat")
    status: AgentStatus = Field(..., description="Current agent status")
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    memory_usage: Optional[float] = Field(None, description="Memory usage percentage")
    active_tasks: List[str] = Field(default_factory=list, description="List of currently active task IDs")
    last_error: Optional[str] = Field(None, description="Last error message, if any")


class SystemStatus(BaseModel):
    """Represents the overall system status."""
    
    total_agents: int = Field(..., description="Total number of registered agents")
    online_agents: int = Field(..., description="Number of online agents")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    active_tasks: int = Field(..., description="Number of active tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")
    system_uptime: float = Field(..., description="System uptime in seconds")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class OrchestratorMetrics(BaseModel):
    """Metrics about the orchestrator's performance."""
    
    messages_processed: int = Field(default=0, description="Total messages processed")
    tasks_assigned: int = Field(default=0, description="Total tasks assigned")
    tasks_completed: int = Field(default=0, description="Total tasks completed")
    tasks_failed: int = Field(default=0, description="Total tasks failed")
    average_task_completion_time: Optional[float] = Field(None, description="Average task completion time in seconds")
    websocket_connections: int = Field(default=0, description="Current WebSocket connections")
    uptime_seconds: float = Field(default=0.0, description="Orchestrator uptime in seconds")


# Type aliases for convenience
AgentDict = Dict[str, Agent]
TaskDict = Dict[str, Task]
MessageDict = Dict[str, Any]
