"""
Core orchestrator that coordinates all components and manages the overall system.
This is the main class that brings together all the different modules.
"""

import asyncio
import signal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .core.models import (
    Message, MessageType, Task, Agent, TaskStatus, AgentStatus,
    TaskAssignment, SystemStatus, OrchestratorMetrics
)
from .agents import AgentManager, TaskManager
from .communication import WebSocketServer, MessageRouter
from .integrations import OllamaIntegration
from .planner import SemanticKernelPlanner
from .interfaces import TerminalInterface
from .utils import (
    get_logger, initialize_logging, log_semantic_kernel_event,
    generate_unique_id, get_current_timestamp
)
from config import ConfigManager


class Orchestrator:
    """
    Main orchestrator class that coordinates all components of the AI agent system.
    Manages agent registration, task distribution, and intelligent planning.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager.config
        self.logger = get_logger(__name__)
        
        # Initialize logging
        initialize_logging(
            log_level=self.config.log_level,
            log_dir="logs"
        )
        
        # Core components
        self.agent_manager: Optional[AgentManager] = None
        self.task_manager: Optional[TaskManager] = None
        self.websocket_server: Optional[WebSocketServer] = None
        self.message_router: Optional[MessageRouter] = None
        self.ollama_client: Optional[OllamaIntegration] = None
        self.planner: Optional[SemanticKernelPlanner] = None
        self.terminal_interface: Optional[TerminalInterface] = None
        
        # System state
        self._is_running = False
        self._start_time: Optional[datetime] = None
        self._shutdown_event = asyncio.Event()
        
        # Metrics
        self._metrics = OrchestratorMetrics()
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        
        self.logger.info("Orchestrator initialized")
    
    async def start_with_terminal_interface(self) -> None:
        """Start the orchestrator with terminal interface for interactive use."""
        if self._is_running:
            self.logger.warning("Orchestrator is already running")
            return
        
        try:
            # Start the main orchestrator
            await self.start()
            
            # Start terminal interface
            if self.terminal_interface:
                await self.terminal_interface.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start orchestrator with terminal interface: {e}")
            await self.stop()
            raise
    
    async def start(self) -> None:
        """Start the orchestrator and all its components."""
        if self._is_running:
            self.logger.warning("Orchestrator is already running")
            return
        
        try:
            self._start_time = datetime.utcnow()
            self.logger.info("Starting orchestrator...")
            
            # Initialize components in order
            await self._initialize_components()
            
            # Start components
            await self._start_components()
            
            # Setup message routing
            self._setup_message_routing()
            
            # Start background tasks
            self._start_background_tasks()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            self._is_running = True
            
            self.logger.info("Orchestrator started successfully")
            log_semantic_kernel_event("ORCHESTRATOR_STARTED", "All components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to start orchestrator: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the orchestrator and cleanup all resources."""
        if not self._is_running:
            return
        
        self.logger.info("Stopping orchestrator...")
        self._is_running = False
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop background tasks
        await self._stop_background_tasks()
        
        # Stop components in reverse order
        await self._stop_components()
        
        # Stop terminal interface
        if self.terminal_interface:
            await self.terminal_interface.stop()
        
        self.logger.info("Orchestrator stopped")
        log_semantic_kernel_event("ORCHESTRATOR_STOPPED", "Graceful shutdown completed")
    
    async def create_task_from_user_input(
        self,
        user_input: str,
        priority: int = 5,
        timeout_seconds: Optional[int] = None
    ) -> Optional[str]:
        """
        Create a task from user input using intelligent analysis.
        
        Args:
            user_input: Natural language description of what the user wants
            priority: Task priority (1-10)
            timeout_seconds: Task timeout
            
        Returns:
            Created task ID or None if creation failed
        """
        try:
            if not self.planner or not self.task_manager:
                self.logger.error("Components not initialized")
                return None
            
            # Analyze the user input to determine requirements
            analysis = await self.planner.analyze_task_requirements(
                task_description=user_input,
                parameters={}
            )
            
            if 'error' in analysis:
                self.logger.error(f"Task analysis failed: {analysis['error']}")
                return None
            
            # Extract capability from analysis
            required_capability = analysis.get('recommended_capability', 'general')
            
            # Check if we have agents with this capability
            suitable_agents = self.agent_manager.get_agents_by_capability(required_capability)
            if not suitable_agents:
                self.logger.warning(f"No agents available with capability '{required_capability}'")
                # Try to find any available agent as fallback
                all_capabilities = self.agent_manager.get_all_capabilities()
                if all_capabilities:
                    required_capability = list(all_capabilities)[0]  # Use first available capability
                    suitable_agents = self.agent_manager.get_agents_by_capability(required_capability)
                
                if not suitable_agents:
                    self.logger.error("No suitable agents available for any capability")
                    return None
            
            # Create task
            task_id = self.task_manager.create_task(
                name=f"User Request: {user_input[:50]}...",
                description=user_input,
                capability_required=required_capability,
                parameters={'user_input': user_input, 'analysis': analysis},
                priority=priority,
                timeout_seconds=timeout_seconds
            )
            
            # Create execution plan
            task = self.task_manager.get_task(task_id)
            if task:
                execution_plan = await self.planner.plan_task_execution(task)
                if execution_plan:
                    self.logger.info(f"Created task {task_id} with execution plan")
                    
                    # Try to assign immediately if we have a recommended agent
                    recommended_agent_id = execution_plan.get('recommended_agent')
                    if recommended_agent_id:
                        await self._assign_task_to_agent(task_id, recommended_agent_id)
                else:
                    self.logger.warning(f"Failed to create execution plan for task {task_id}")
            
            self.logger.info(f"Created task {task_id} from user input: {user_input}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error creating task from user input: {e}")
            return None
    
    async def process_scenario(self, scenario_description: str) -> List[str]:
        """
        Process a user scenario by breaking it down into multiple tasks.
        
        Args:
            scenario_description: Natural language description of the scenario
            
        Returns:
            List of created task IDs
        """
        try:
            if not self.planner or not self.task_manager or not self.agent_manager:
                self.logger.error("Components not initialized")
                return []
            
            self.logger.info(f"Processing scenario: {scenario_description}")
            
            # Get available agents
            available_agents = self.agent_manager.get_all_agents()
            if not available_agents:
                self.logger.warning("No agents available to execute scenario tasks")
                return []
            
            # Use planner to break down scenario into tasks
            task_breakdown = await self._analyze_scenario_breakdown(scenario_description)
            
            if not task_breakdown:
                self.logger.warning("Failed to break down scenario into tasks")
                return []
            
            created_task_ids = []
            
            # Create tasks from breakdown
            for task_info in task_breakdown:
                task_id = self.task_manager.create_task(
                    name=task_info['name'],
                    description=task_info['description'],
                    capability_required=task_info.get('capability', 'general'),
                    parameters=task_info.get('parameters', {}),
                    priority=task_info.get('priority', 5),
                    dependencies=task_info.get('dependencies', [])
                )
                
                created_task_ids.append(task_id)
                self.logger.info(f"Created scenario task {task_id}: {task_info['name']}")
            
            self.logger.info(f"Scenario processed: created {len(created_task_ids)} tasks")
            return created_task_ids
            
        except Exception as e:
            self.logger.error(f"Error processing scenario: {e}")
            return []
    
    async def _analyze_scenario_breakdown(self, scenario_description: str) -> List[Dict[str, Any]]:
        """
        Analyze a scenario and break it down into constituent tasks.
        
        Args:
            scenario_description: The scenario to break down
            
        Returns:
            List of task information dictionaries
        """
        try:
            # Use the planner for intelligent breakdown
            analysis = await self.planner.analyze_task_requirements(
                task_description=f"Break down this complex scenario into sequential tasks: {scenario_description}",
                parameters={'mode': 'scenario_breakdown', 'scenario': scenario_description}
            )
            
            if 'error' in analysis:
                self.logger.error(f"Scenario analysis failed: {analysis['error']}")
                return []
            
            # Extract complexity and create appropriate breakdown
            complexity = analysis.get('complexity', 'medium')
            
            # Simple rule-based breakdown for now - can be enhanced with more AI
            task_breakdown = []
            
            # Split scenario into logical steps
            import re
            
            # Look for action words and break accordingly
            action_patterns = [
                (r'\b(navigate|move|go)\s+to\s+([^,\.]+)', 'movement'),
                (r'\b(pick|grab|take)\s+([^,\.]+)', 'manipulation'),
                (r'\b(bring|carry|transport)\s+([^,\.]+)', 'manipulation'),
                (r'\b(place|put|drop)\s+([^,\.]+)', 'manipulation'),
                (r'\b(scan|look|find|search)\s+([^,\.]+)', 'vision'),
                (r'\b(detect|identify|recognize)\s+([^,\.]+)', 'vision')
            ]
            
            # Split by common delimiters
            steps = re.split(r'[,;]|\s+and\s+|\s+then\s+', scenario_description)
            steps = [step.strip() for step in steps if step.strip()]
            
            if len(steps) < 2:
                # Single action scenario
                steps = [scenario_description]
            
            task_counter = 1
            previous_task_id = None
            
            for step in steps:
                if len(step) < 5:  # Skip very short fragments
                    continue
                
                # Determine capability
                capability = 'general'
                for pattern, cap in action_patterns:
                    if re.search(pattern, step, re.IGNORECASE):
                        capability = cap
                        break
                
                task_name = f"Step {task_counter}: {step[:50]}..."
                
                task_info = {
                    'name': task_name,
                    'description': step,
                    'capability': capability,
                    'parameters': {
                        'scenario': scenario_description,
                        'step_number': task_counter,
                        'original_step': step
                    },
                    'priority': 5,
                    'dependencies': [previous_task_id] if previous_task_id else []
                }
                
                task_breakdown.append(task_info)
                previous_task_id = task_name
                task_counter += 1
            
            # If no breakdown was possible, create a single comprehensive task
            if not task_breakdown:
                task_breakdown.append({
                    'name': f"Execute Scenario: {scenario_description[:50]}...",
                    'description': scenario_description,
                    'capability': 'general',
                    'parameters': {'scenario': scenario_description},
                    'priority': 5,
                    'dependencies': []
                })
            
            self.logger.info(f"Broke down scenario into {len(task_breakdown)} tasks")
            return task_breakdown
            
        except Exception as e:
            self.logger.error(f"Error analyzing scenario breakdown: {e}")
            return []
    
    async def get_system_status(self) -> SystemStatus:
        """
        Get current system status.
        
        Returns:
            SystemStatus object with current metrics
        """
        agent_stats = self.agent_manager.get_system_statistics() if self.agent_manager else {}
        task_stats = self.task_manager.get_statistics() if self.task_manager else {}
        
        uptime = (datetime.utcnow() - self._start_time).total_seconds() if self._start_time else 0
        
        return SystemStatus(
            total_agents=agent_stats.get('total_agents', 0),
            online_agents=agent_stats.get('online_agents', 0),
            pending_tasks=task_stats.get('pending_tasks', 0),
            active_tasks=task_stats.get('active_tasks', 0),
            completed_tasks=task_stats.get('completed_tasks', 0),
            failed_tasks=task_stats.get('failed_tasks', 0),
            system_uptime=uptime
        )
    
    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()
    
    async def _initialize_components(self) -> None:
        """Initialize all components."""
        # Initialize agent manager
        self.agent_manager = AgentManager(
            heartbeat_timeout=self.config.agent_heartbeat_interval * 3
        )
        
        # Initialize task manager
        self.task_manager = TaskManager(
            default_timeout=self.config.task_execution_timeout
        )
        
        # Initialize Ollama client
        self.ollama_client = OllamaIntegration(
            base_url=self.config.ollama.base_url,
            model=self.config.ollama.model
        )
        
        # Initialize WebSocket server
        self.websocket_server = WebSocketServer(
            host=self.config.websocket.host,
            port=self.config.websocket.port,
            max_connections=self.config.websocket.max_connections
        )
        
        # Initialize message router
        self.message_router = MessageRouter(
            agent_manager=self.agent_manager,
            task_manager=self.task_manager
        )
        
        # Initialize Semantic Kernel planner
        self.planner = SemanticKernelPlanner(
            agent_manager=self.agent_manager,
            task_manager=self.task_manager,
            ollama_client=self.ollama_client,
            service_id=self.config.semantic_kernel.service_id
        )
        
        # Initialize terminal interface
        self.terminal_interface = TerminalInterface(self)
        
        self.logger.info("All components initialized")
    
    async def _start_components(self) -> None:
        """Start all components."""
        # Initialize Ollama client
        await self.ollama_client.initialize()
        
        # Start agent manager
        await self.agent_manager.start()
        
        # Start task manager
        await self.task_manager.start()
        
        # Initialize Semantic Kernel planner
        await self.planner.initialize()
        
        # Start WebSocket server
        await self.websocket_server.start()
        
        self.logger.info("All components started")
    
    async def _stop_components(self) -> None:
        """Stop all components."""
        if self.websocket_server:
            await self.websocket_server.stop()
        
        if self.task_manager:
            await self.task_manager.stop()
        
        if self.agent_manager:
            await self.agent_manager.stop()
        
        if self.ollama_client:
            await self.ollama_client.stop()
        
        self.logger.info("All components stopped")
    
    def _setup_message_routing(self) -> None:
        """Setup message routing between WebSocket server and message router."""
        if not self.websocket_server or not self.message_router:
            return
        
        # Register message handlers
        async def handle_message(message: Message, connection_id: str) -> None:
            response = await self.message_router.route_message(message, connection_id)
            if response:
                await self.websocket_server._send_message_to_connection(connection_id, response)
        
        # Register handlers for all message types
        for message_type in MessageType:
            self.websocket_server.register_message_handler(message_type, handle_message)
        
        self.logger.info("Message routing configured")
    
    def _start_background_tasks(self) -> None:
        """Start background tasks."""
        # Task assignment task
        task = asyncio.create_task(self._task_assignment_loop())
        self._background_tasks.append(task)
        
        # Metrics collection task
        task = asyncio.create_task(self._metrics_collection_loop())
        self._background_tasks.append(task)
        
        # System monitoring task
        task = asyncio.create_task(self._system_monitoring_loop())
        self._background_tasks.append(task)
        
        self.logger.info("Background tasks started")
    
    async def _stop_background_tasks(self) -> None:
        """Stop all background tasks."""
        for task in self._background_tasks:
            task.cancel()
        
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        self._background_tasks.clear()
        self.logger.info("Background tasks stopped")
    
    async def _task_assignment_loop(self) -> None:
        """Background task for automatic task assignment."""
        while self._is_running:
            try:
                if self.task_manager and self.agent_manager and self.planner:
                    # Get pending tasks
                    pending_tasks = self.task_manager.get_pending_tasks()
                    
                    if pending_tasks:
                        # Use planner to optimize assignments
                        assignments = await self.planner.optimize_task_assignment(pending_tasks)
                        
                        # Apply assignments
                        for assignment in assignments:
                            task_id = assignment.get('task_id')
                            agent_id = assignment.get('agent_id')
                            
                            if task_id and agent_id:
                                await self._assign_task_to_agent(task_id, agent_id)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in task assignment loop: {e}")
                await asyncio.sleep(10)
    
    async def _assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent and send assignment message."""
        try:
            # Assign task
            success = await self.task_manager.assign_task_to_agent(task_id, agent_id)
            if not success:
                return False
            
            # Get task details
            task = self.task_manager.get_task(task_id)
            if not task:
                return False
            
            # Create assignment message
            assignment = TaskAssignment(
                task=task,
                deadline=None,  # Could be calculated based on timeout
                additional_instructions=None
            )
            
            message = Message(
                message_id=generate_unique_id("msg"),
                message_type=MessageType.TASK_ASSIGNMENT,
                sender_id="orchestrator",
                recipient_id=agent_id,
                payload=assignment.dict()
            )
            
            # Send to agent
            if self.websocket_server:
                await self.websocket_server.send_message_to_agent(agent_id, message)
            
            # Start task execution
            await self.task_manager.start_task_execution(task_id)
            
            self.logger.info(f"Assigned and started task {task_id} on agent {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error assigning task {task_id} to agent {agent_id}: {e}")
            return False
    
    async def _metrics_collection_loop(self) -> None:
        """Background task for collecting metrics."""
        while self._is_running:
            try:
                # Update metrics
                if self._start_time:
                    self._metrics.uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
                
                if self.websocket_server:
                    stats = self.websocket_server.get_server_stats()
                    self._metrics.websocket_connections = stats.get('active_connections', 0)
                
                if self.task_manager:
                    task_stats = self.task_manager.get_statistics()
                    self._metrics.tasks_assigned = task_stats.get('total_tasks', 0)
                    self._metrics.tasks_completed = task_stats.get('completed_tasks', 0)
                    failed_tasks = task_stats.get('status_distribution', {}).get('failed', [])
                    self._metrics.tasks_failed = len(failed_tasks) if isinstance(failed_tasks, list) else failed_tasks
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)
    
    async def _system_monitoring_loop(self) -> None:
        """Background task for system monitoring and health checks."""
        while self._is_running:
            try:
                # Check Ollama health
                if self.ollama_client:
                    health = await self.ollama_client.client.check_health()
                    if not health:
                        self.logger.warning("Ollama service is unhealthy")
                
                # Log system status periodically
                status = await self.get_system_status()
                self.logger.info(
                    f"System Status - Agents: {status.online_agents}/{status.total_agents}, "
                    f"Tasks: {status.pending_tasks} pending, {status.active_tasks} active"
                )
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(60)
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())
        
        # Setup signal handlers (Unix systems)
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except AttributeError:
            # On Windows, only SIGINT is available
            signal.signal(signal.SIGINT, signal_handler)
