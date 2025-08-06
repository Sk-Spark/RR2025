"""
Task manager for handling task lifecycle, assignment, and execution tracking.
Manages the queue of tasks and their distribution to appropriate agents.
"""

import asyncio
from typing import Dict, List, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque

from ..core.models import (
    Task, TaskStatus, Agent, AgentStatus,
    TaskAssignment, TaskUpdate, TaskResult
)
from ..utils import get_logger, log_task_execution, generate_unique_id


@dataclass
class TaskExecution:
    """Represents a task execution context."""
    task: Task
    assigned_agent_id: Optional[str] = None
    assignment_time: Optional[datetime] = None
    execution_start: Optional[datetime] = None
    last_update: Optional[datetime] = None
    timeout_task: Optional[asyncio.Task] = None


class TaskManager:
    """
    Manages task lifecycle, assignment, and execution tracking.
    Handles task queuing, agent assignment, and progress monitoring.
    """
    
    def __init__(self, default_timeout: int = 300):
        """
        Initialize the task manager.
        
        Args:
            default_timeout: Default task timeout in seconds
        """
        self.logger = get_logger(__name__)
        self.default_timeout = default_timeout
        
        # Task storage
        self._tasks: Dict[str, Task] = {}
        self._task_executions: Dict[str, TaskExecution] = {}
        
        # Task queues
        self._pending_tasks: deque = deque()
        self._priority_tasks: deque = deque()
        
        # Dependency tracking
        self._task_dependencies: Dict[str, Set[str]] = {}
        self._dependent_tasks: Dict[str, Set[str]] = {}
        
        # Execution tracking
        self._agent_tasks: Dict[str, Set[str]] = {}  # agent_id -> set of task_ids
        self._completed_tasks: List[str] = []
        
        # Callbacks
        self._task_completion_callbacks: List[Callable[[Task], None]] = []
        self._task_failure_callbacks: List[Callable[[Task, str], None]] = []
        
        # Background tasks
        self._task_processor: Optional[asyncio.Task] = None
        self._timeout_monitor: Optional[asyncio.Task] = None
        self._is_running = False
        
        self.logger.info("TaskManager initialized")
    
    async def start(self) -> None:
        """Start the task manager and its background tasks."""
        if self._is_running:
            self.logger.warning("TaskManager is already running")
            return
        
        self._is_running = True
        self._task_processor = asyncio.create_task(self._process_tasks())
        self._timeout_monitor = asyncio.create_task(self._monitor_timeouts())
        self.logger.info("TaskManager started")
    
    async def stop(self) -> None:
        """Stop the task manager and cleanup background tasks."""
        self._is_running = False
        
        # Cancel background tasks
        if self._task_processor:
            self._task_processor.cancel()
        if self._timeout_monitor:
            self._timeout_monitor.cancel()
        
        # Cancel all timeout tasks
        for execution in self._task_executions.values():
            if execution.timeout_task:
                execution.timeout_task.cancel()
        
        # Wait for tasks to complete
        tasks_to_wait = []
        if self._task_processor:
            tasks_to_wait.append(self._task_processor)
        if self._timeout_monitor:
            tasks_to_wait.append(self._timeout_monitor)
        
        if tasks_to_wait:
            try:
                await asyncio.gather(*tasks_to_wait, return_exceptions=True)
            except Exception as e:
                self.logger.error(f"Error stopping task manager: {e}")
        
        self.logger.info("TaskManager stopped")
    
    def create_task(
        self,
        name: str,
        description: str,
        capability_required: str,
        parameters: Optional[Dict] = None,
        priority: int = 5,
        timeout_seconds: Optional[int] = None,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """
        Create a new task.
        
        Args:
            name: Task name
            description: Task description
            capability_required: Required capability to execute the task
            parameters: Task parameters
            priority: Task priority (1-10, higher is more urgent)
            timeout_seconds: Task timeout in seconds
            dependencies: List of task IDs this task depends on
            
        Returns:
            Created task ID
        """
        task_id = generate_unique_id("task")
        
        task = Task(
            task_id=task_id,
            name=name,
            description=description,
            capability_required=capability_required,
            parameters=parameters or {},
            priority=priority,
            timeout_seconds=timeout_seconds or self.default_timeout,
            dependencies=dependencies or []
        )
        
        self._tasks[task_id] = task
        self._task_executions[task_id] = TaskExecution(task=task)
        
        # Set up dependencies
        if dependencies:
            self._task_dependencies[task_id] = set(dependencies)
            for dep_id in dependencies:
                if dep_id not in self._dependent_tasks:
                    self._dependent_tasks[dep_id] = set()
                self._dependent_tasks[dep_id].add(task_id)
        
        # Add to appropriate queue
        if self._can_execute_task(task_id):
            if priority >= 8:
                self._priority_tasks.append(task_id)
            else:
                self._pending_tasks.append(task_id)
        
        log_task_execution(task_id, "", "CREATED", f"Priority: {priority}, Capability: {capability_required}")
        self.logger.info(f"Created task {task_id}: {name}")
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object or None if not found
        """
        return self._tasks.get(task_id)
    
    def get_agent_tasks(self, agent_id: str) -> List[Task]:
        """
        Get all tasks assigned to an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of tasks assigned to the agent
        """
        task_ids = self._agent_tasks.get(agent_id, set())
        return [self._tasks[task_id] for task_id in task_ids if task_id in self._tasks]
    
    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending tasks.
        
        Returns:
            List of pending tasks
        """
        return [
            self._tasks[task_id] 
            for task_id in list(self._pending_tasks) + list(self._priority_tasks)
            if task_id in self._tasks
        ]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: Task status to filter by
            
        Returns:
            List of tasks with the specified status
        """
        return [task for task in self._tasks.values() if task.status == status]
    
    async def assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        """
        Assign a task to a specific agent.
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            
        Returns:
            True if assignment was successful, False otherwise
        """
        try:
            if task_id not in self._tasks:
                self.logger.error(f"Task {task_id} not found")
                return False
            
            task = self._tasks[task_id]
            
            if task.status != TaskStatus.PENDING:
                self.logger.error(f"Task {task_id} is not in pending status")
                return False
            
            # Update task
            task.assigned_agent_id = agent_id
            task.status = TaskStatus.ASSIGNED
            
            # Update execution tracking
            execution = self._task_executions[task_id]
            execution.assigned_agent_id = agent_id
            execution.assignment_time = datetime.utcnow()
            
            # Track agent tasks
            if agent_id not in self._agent_tasks:
                self._agent_tasks[agent_id] = set()
            self._agent_tasks[agent_id].add(task_id)
            
            # Remove from queues
            self._remove_from_queues(task_id)
            
            # Set up timeout
            if task.timeout_seconds:
                execution.timeout_task = asyncio.create_task(
                    self._handle_task_timeout(task_id, task.timeout_seconds)
                )
            
            log_task_execution(task_id, agent_id, "ASSIGNED")
            self.logger.info(f"Task {task_id} assigned to agent {agent_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign task {task_id} to agent {agent_id}: {e}")
            return False
    
    async def start_task_execution(self, task_id: str) -> bool:
        """
        Mark a task as started.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            
            if task.status != TaskStatus.ASSIGNED:
                self.logger.warning(f"Task {task_id} is not in assigned status")
                return False
            
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            
            execution = self._task_executions[task_id]
            execution.execution_start = datetime.utcnow()
            execution.last_update = datetime.utcnow()
            
            log_task_execution(task_id, task.assigned_agent_id or "", "STARTED")
            self.logger.info(f"Task {task_id} execution started")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start task {task_id}: {e}")
            return False
    
    async def update_task_progress(self, task_update: TaskUpdate) -> bool:
        """
        Update task progress.
        
        Args:
            task_update: Task update information
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            task_id = task_update.task_id
            
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            execution = self._task_executions[task_id]
            
            # Update task status if provided
            if task_update.status:
                task.status = task_update.status
            
            # Update metadata
            if task_update.progress_percentage is not None:
                task.metadata['progress_percentage'] = task_update.progress_percentage
            
            if task_update.message:
                task.metadata['last_update_message'] = task_update.message
            
            if task_update.estimated_completion_time:
                task.metadata['estimated_completion_time'] = task_update.estimated_completion_time
            
            execution.last_update = datetime.utcnow()
            
            log_task_execution(
                task_id, 
                task.assigned_agent_id or "", 
                "UPDATED", 
                task_update.message or ""
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update task {task_update.task_id}: {e}")
            return False
    
    async def complete_task(self, task_result: TaskResult) -> bool:
        """
        Complete a task with results.
        
        Args:
            task_result: Task completion result
            
        Returns:
            True if completion was successful, False otherwise
        """
        try:
            task_id = task_result.task_id
            
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            execution = self._task_executions[task_id]
            
            # Update task
            task.status = task_result.status
            task.completed_at = datetime.utcnow()
            task.result = task_result.result
            
            if task_result.error_message:
                task.error_message = task_result.error_message
            
            # Calculate execution time
            if execution.execution_start:
                execution_time = (datetime.utcnow() - execution.execution_start).total_seconds()
                task.metadata['execution_time_seconds'] = execution_time
            
            # Cancel timeout task
            if execution.timeout_task:
                execution.timeout_task.cancel()
                execution.timeout_task = None
            
            # Remove from agent tasks
            if task.assigned_agent_id and task.assigned_agent_id in self._agent_tasks:
                self._agent_tasks[task.assigned_agent_id].discard(task_id)
            
            # Add to completed tasks
            if task_id not in self._completed_tasks:
                self._completed_tasks.append(task_id)
            
            # Check for dependent tasks
            await self._process_task_dependencies(task_id)
            
            # Call completion callbacks
            try:
                if task.status == TaskStatus.COMPLETED:
                    for callback in self._task_completion_callbacks:
                        callback(task)
                elif task.status == TaskStatus.FAILED:
                    for callback in self._task_failure_callbacks:
                        callback(task, task.error_message or "Unknown error")
            except Exception as e:
                self.logger.error(f"Error in task completion callback: {e}")
            
            log_task_execution(
                task_id, 
                task.assigned_agent_id or "", 
                task.status.value.upper(),
                task_result.error_message or "Success"
            )
            
            self.logger.info(f"Task {task_id} completed with status {task.status.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete task {task_result.task_id}: {e}")
            return False
    
    async def cancel_task(self, task_id: str, reason: str = "") -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID
            reason: Cancellation reason
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        try:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            execution = self._task_executions[task_id]
            
            # Update task
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            task.error_message = reason or "Task cancelled"
            
            # Cancel timeout task
            if execution.timeout_task:
                execution.timeout_task.cancel()
                execution.timeout_task = None
            
            # Remove from queues and agent tasks
            self._remove_from_queues(task_id)
            if task.assigned_agent_id and task.assigned_agent_id in self._agent_tasks:
                self._agent_tasks[task.assigned_agent_id].discard(task_id)
            
            log_task_execution(task_id, task.assigned_agent_id or "", "CANCELLED", reason)
            self.logger.info(f"Task {task_id} cancelled: {reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def add_completion_callback(self, callback: Callable[[Task], None]) -> None:
        """Add a callback for task completion events."""
        self._task_completion_callbacks.append(callback)
    
    def add_failure_callback(self, callback: Callable[[Task, str], None]) -> None:
        """Add a callback for task failure events."""
        self._task_failure_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get task management statistics.
        
        Returns:
            Dictionary containing task statistics
        """
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len(self.get_tasks_by_status(status))
        
        return {
            'total_tasks': len(self._tasks),
            'pending_tasks': len(self._pending_tasks) + len(self._priority_tasks),
            'status_distribution': status_counts,
            'completed_tasks': len(self._completed_tasks),
            'agent_task_distribution': {
                agent_id: len(task_ids) 
                for agent_id, task_ids in self._agent_tasks.items()
            }
        }
    
    def _can_execute_task(self, task_id: str) -> bool:
        """Check if a task can be executed (all dependencies met)."""
        if task_id not in self._task_dependencies:
            return True
        
        dependencies = self._task_dependencies[task_id]
        for dep_id in dependencies:
            if dep_id not in self._tasks:
                continue
            dep_task = self._tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _remove_from_queues(self, task_id: str) -> None:
        """Remove a task from all queues."""
        try:
            self._pending_tasks.remove(task_id)
        except ValueError:
            pass
        
        try:
            self._priority_tasks.remove(task_id)
        except ValueError:
            pass
    
    async def _process_task_dependencies(self, completed_task_id: str) -> None:
        """Process tasks that depend on a completed task."""
        if completed_task_id not in self._dependent_tasks:
            return
        
        dependent_task_ids = self._dependent_tasks[completed_task_id].copy()
        
        for task_id in dependent_task_ids:
            if self._can_execute_task(task_id) and task_id in self._tasks:
                task = self._tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    # Add to appropriate queue
                    if task.priority >= 8:
                        self._priority_tasks.append(task_id)
                    else:
                        self._pending_tasks.append(task_id)
                    
                    self.logger.info(f"Task {task_id} is now ready for execution")
    
    async def _process_tasks(self) -> None:
        """Background task processor."""
        while self._is_running:
            try:
                # This is a placeholder for task processing logic
                # In a real implementation, you would integrate with the agent manager
                # to find suitable agents and assign tasks
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_timeouts(self) -> None:
        """Monitor task timeouts."""
        while self._is_running:
            try:
                current_time = datetime.utcnow()
                
                for task_id, execution in self._task_executions.items():
                    task = execution.task
                    if (task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS] and
                        execution.assignment_time and
                        task.timeout_seconds):
                        
                        elapsed = (current_time - execution.assignment_time).total_seconds()
                        if elapsed > task.timeout_seconds:
                            await self.cancel_task(task_id, "Task timeout")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in timeout monitor: {e}")
                await asyncio.sleep(5)
    
    async def _handle_task_timeout(self, task_id: str, timeout_seconds: int) -> None:
        """Handle individual task timeout."""
        try:
            await asyncio.sleep(timeout_seconds)
            await self.cancel_task(task_id, "Task timeout")
        except asyncio.CancelledError:
            pass  # Task completed before timeout
