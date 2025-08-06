"""
Semantic Kernel planner integration for intelligent task routing.
Uses Microsoft Semantic Kernel to plan and route tasks to appropriate agents.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json

# Semantic Kernel imports
import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.core_plugins import ConversationSummaryPlugin
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.contents import ChatHistory
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.functions import kernel_function

from ..core.models import Agent, Task, AgentCapability, TaskStatus
from ..integrations import OllamaIntegration
from ..utils import get_logger, log_semantic_kernel_event, format_error_message


@dataclass
class PlanStep:
    """Represents a single step in an execution plan."""
    step_number: int
    action: str
    expected_outcome: str
    agent_id: Optional[str] = None
    estimated_duration: Optional[int] = None
    dependencies: Optional[List[str]] = None


@dataclass
class ExecutionPlan:
    """Represents a complete execution plan for a task."""
    task_id: str
    plan_id: str
    created_at: str
    recommended_agent: Optional[str]
    agent_name: Optional[str]
    estimated_duration: Optional[int]
    priority_adjustment: int
    dependencies: List[str]
    plan_reasoning: str
    plan_steps: List[PlanStep]


class OrchestrationMode(Enum):
    """Orchestration execution modes."""
    SEQUENTIAL = "sequential"
    CONCURRENT = "concurrent"
    HYBRID = "hybrid"


@dataclass
class ConcurrentTask:
    """Represents a task in concurrent orchestration."""
    task_id: str
    agent_id: str
    action: str
    dependencies: List[str]
    estimated_duration: int
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class OrchestrationPlan:
    """Complete orchestration plan with concurrent execution support."""
    plan_id: str
    mode: OrchestrationMode
    tasks: List[ConcurrentTask]
    coordination_strategy: str
    success_criteria: List[str]
    failure_handling: str
    estimated_total_duration: int


class TaskPlannerPlugin:
    """
    Semantic Kernel plugin for task planning and agent routing.
    Provides functions that the planner can use to understand agent capabilities.
    """
    
    def __init__(self, agent_manager, task_manager):
        self.agent_manager = agent_manager
        self.task_manager = task_manager
        self.logger = get_logger(__name__)
    
    @kernel_function(
        description="Get list of all available agent capabilities",
        name="get_agent_capabilities"
    )
    def get_agent_capabilities(self) -> str:
        """Get a formatted list of all agent capabilities."""
        try:
            agents = self.agent_manager.get_online_agents()
            capabilities_info = []
            
            for agent in agents:
                agent_info = f"Agent: {agent.name} (ID: {agent.agent_id})"
                capabilities_info.append(agent_info)
                
                for capability in agent.capabilities:
                    cap_info = f"  - {capability.name}: {capability.description}"
                    if capability.category:
                        cap_info += f" [Category: {capability.category}]"
                    if capability.estimated_duration:
                        cap_info += f" [Duration: ~{capability.estimated_duration}s]"
                    capabilities_info.append(cap_info)
                
                capabilities_info.append("")  # Empty line between agents
            
            return "\n".join(capabilities_info)
        
        except Exception as e:
            self.logger.error(f"Error getting agent capabilities: {e}")
            return "Error retrieving agent capabilities"
    
    @kernel_function(
        description="Get agents that can perform a specific capability",
        name="find_agents_for_capability"
    )
    def find_agents_for_capability(self, capability_name: str) -> str:
        """Find agents that can perform a specific capability."""
        try:
            agents = self.agent_manager.get_agents_by_capability(capability_name)
            
            if not agents:
                return f"No agents found with capability '{capability_name}'"
            
            agent_info = []
            for agent in agents:
                status_info = f"Status: {agent.status.value}"
                if agent.metadata.get('cpu_usage'):
                    status_info += f", CPU: {agent.metadata['cpu_usage']}%"
                if agent.metadata.get('active_tasks'):
                    status_info += f", Active tasks: {len(agent.metadata['active_tasks'])}"
                
                agent_info.append(f"- {agent.name} (ID: {agent.agent_id}) - {status_info}")
            
            return f"Agents with capability '{capability_name}':\n" + "\n".join(agent_info)
        
        except Exception as e:
            self.logger.error(f"Error finding agents for capability: {e}")
            return f"Error finding agents for capability '{capability_name}'"
    
    @kernel_function(
        description="Get current system status and agent availability",
        name="get_system_status"
    )
    def get_system_status(self) -> str:
        """Get current system status."""
        try:
            stats = self.agent_manager.get_system_statistics()
            task_stats = self.task_manager.get_statistics()
            
            status_info = [
                f"System Status:",
                f"- Total Agents: {stats['total_agents']}",
                f"- Online Agents: {stats['online_agents']}",
                f"- Total Capabilities: {stats['total_capabilities']}",
                f"- Pending Tasks: {task_stats['pending_tasks']}",
                f"- Total Tasks: {task_stats['total_tasks']}"
            ]
            
            return "\n".join(status_info)
        
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return "Error retrieving system status"


class SemanticKernelPlanner:
    """
    Semantic Kernel-based planner with Concurrent Orchestration Pattern support.
    Enables intelligent task routing, concurrent execution planning, and agent coordination.
    """
    
    def __init__(
        self,
        agent_manager,
        task_manager,
        ollama_client: OllamaIntegration,
        service_id: str = "orchestrator_sk"
    ):
        """
        Initialize the Semantic Kernel planner.
        
        Args:
            agent_manager: Agent manager instance
            task_manager: Task manager instance
            ollama_client: Ollama integration for LLM access
            service_id: Service ID for Semantic Kernel
        """
        self.agent_manager = agent_manager
        self.task_manager = task_manager
        self.ollama_client = ollama_client
        self.service_id = service_id
        self.logger = get_logger(__name__)
        
        # Semantic Kernel components
        self.kernel: Optional[sk.Kernel] = None
        self.agent: Optional[ChatCompletionAgent] = None
        self.chat_history: Optional[ChatHistory] = None
        
        # Concurrent orchestration components
        self._active_orchestrations: Dict[str, OrchestrationPlan] = {}
        self._execution_semaphore = asyncio.Semaphore(10)  # Limit concurrent tasks
        self._coordination_lock = asyncio.Lock()
        
        # Planning context
        self._planning_context = {}
        self._execution_history: List[Dict[str, Any]] = []
        
        self.logger.info("SemanticKernelPlanner initialized with Concurrent Orchestration Pattern")
    
    async def initialize(self) -> bool:
        """
        Initialize the Semantic Kernel components.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Create kernel
            self.kernel = sk.Kernel()
            
            # Add Ollama chat completion service
            chat_service = OllamaChatCompletion(
                ai_model_id=self.ollama_client.client.model,
                base_url=self.ollama_client.client.base_url,
                service_id=self.service_id
            )
            
            self.kernel.add_service(chat_service)
            
            # Add core plugins
            self.kernel.add_plugin(ConversationSummaryPlugin(kernel=self.kernel), "conversation")
            
            # Add custom task planner plugin
            task_plugin = TaskPlannerPlugin(self.agent_manager, self.task_manager)
            self.kernel.add_plugin(task_plugin, "task_planner")
            
            # Initialize chat completion agent
            self.agent = ChatCompletionAgent(
                service_id=self.service_id,
                kernel=self.kernel,
                name="OrchestratorPlanner",
                instructions="""You are an AI orchestrator responsible for planning and routing tasks to appropriate agents.
                
Available agents and their capabilities will be provided to you. Your job is to:
1. Analyze incoming tasks and requirements
2. Determine which agent(s) can best handle each task
3. Create execution plans with proper sequencing
4. Consider dependencies and resource constraints
5. Provide clear routing decisions with reasoning

Always respond with structured JSON containing your routing decisions."""
            )
            
            # Initialize chat history
            self.chat_history = ChatHistory()
            
            # Store agent capabilities for context
            await self._index_agent_capabilities()
            
            log_semantic_kernel_event("INITIALIZED", f"Service ID: {self.service_id}")
            self.logger.info("Semantic Kernel planner initialized successfully")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Semantic Kernel planner: {format_error_message(e)}")
            return False
    
    async def plan_task_execution(self, task: Task) -> Optional[Dict[str, Any]]:
        """
        Create an execution plan for a task using Semantic Kernel.
        
        Args:
            task: Task to plan execution for
            
        Returns:
            Execution plan dictionary or None if planning failed
        """
        try:
            if not self.kernel or not self.agent:
                self.logger.error("Semantic Kernel not initialized")
                return None
            
            # Create planning prompt
            planning_prompt = self._create_planning_prompt(task)
            
            # Add the planning request to chat history
            self.chat_history.add_user_message(planning_prompt)
            
            # Get planning response from agent
            response = await self.agent.invoke(self.kernel, self.chat_history)
            
            # Add agent response to history
            if response and hasattr(response, 'content'):
                self.chat_history.add_assistant_message(response.content)
                plan_content = response.content
            else:
                plan_content = str(response)
            
            # Extract plan details
            execution_plan = {
                'task_id': task.task_id,
                'plan_id': f"plan_{task.task_id}",
                'created_at': datetime.utcnow().isoformat(),
                'plan_steps': [],
                'recommended_agent': None,
                'estimated_duration': None,
                'priority_adjustment': 0,
                'dependencies': task.dependencies.copy() if task.dependencies else [],
                'plan_reasoning': plan_content
            }
            
            # Parse agent response to extract planning information
            try:
                import json
                # Try to parse as JSON first
                if '{' in plan_content and '}' in plan_content:
                    start = plan_content.find('{')
                    end = plan_content.rfind('}') + 1
                    json_content = plan_content[start:end]
                    parsed_plan = json.loads(json_content)
                    
                    if 'recommended_agent' in parsed_plan:
                        execution_plan['recommended_agent'] = parsed_plan['recommended_agent']
                    if 'agent_name' in parsed_plan:
                        execution_plan['agent_name'] = parsed_plan['agent_name']
                    if 'estimated_duration' in parsed_plan:
                        execution_plan['estimated_duration'] = parsed_plan['estimated_duration']
                    if 'priority_adjustment' in parsed_plan:
                        execution_plan['priority_adjustment'] = parsed_plan['priority_adjustment']
                    if 'plan_steps' in parsed_plan:
                        execution_plan['plan_steps'] = parsed_plan['plan_steps']
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, use text-based analysis
                pass
            
            # Find best agent for the task if not specified in plan
            if not execution_plan.get('recommended_agent'):
                best_agent = await self._find_best_agent_for_task(task)
                if best_agent:
                    execution_plan['recommended_agent'] = best_agent.agent_id
                    execution_plan['agent_name'] = best_agent.name
            
            # Store plan in context
            self._planning_context[task.task_id] = execution_plan
            
            log_semantic_kernel_event("PLAN_CREATED", f"Task: {task.task_id}, Steps: {len(execution_plan['plan_steps'])}")
            self.logger.info(f"Created execution plan for task {task.task_id}")
            
            return execution_plan
        
        except Exception as e:
            self.logger.error(f"Error creating execution plan for task {task.task_id}: {format_error_message(e)}")
            return None
    
    async def analyze_task_requirements(self, task_description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze task requirements and suggest optimal execution strategy.
        
        Args:
            task_description: Description of the task
            parameters: Task parameters
            
        Returns:
            Analysis results with recommendations
        """
        try:
            if not self.kernel:
                return {'error': 'Semantic Kernel not initialized'}
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following task and provide recommendations for execution:
            
            Task Description: {task_description}
            Parameters: {parameters}
            
            Please analyze:
            1. What type of capability is required?
            2. What are the key requirements?
            3. What is the estimated complexity?
            4. Are there any dependencies or prerequisites?
            5. What could go wrong and how to mitigate risks?
            
            Provide your analysis in a structured format.
            """
            
            # Use Semantic Kernel to analyze
            response = await self.kernel.invoke_prompt(analysis_prompt)
            
            # Parse and structure the response
            analysis = {
                'task_description': task_description,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'llm_analysis': str(response),
                'recommended_capability': self._extract_capability_from_analysis(str(response)),
                'complexity_estimate': self._extract_complexity_from_analysis(str(response)),
                'risk_factors': self._extract_risks_from_analysis(str(response))
            }
            
            log_semantic_kernel_event("TASK_ANALYZED", f"Capability: {analysis['recommended_capability']}")
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Error analyzing task requirements: {format_error_message(e)}")
            return {'error': f'Analysis failed: {e}'}
    
    async def optimize_task_assignment(self, pending_tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Optimize assignment of multiple pending tasks to available agents.
        
        Args:
            pending_tasks: List of pending tasks
            
        Returns:
            List of assignment recommendations
        """
        try:
            if not pending_tasks:
                return []
            
            # Get current system state
            available_agents = self.agent_manager.get_online_agents()
            
            # Create optimization prompt
            optimization_prompt = self._create_optimization_prompt(pending_tasks, available_agents)
            
            # Use Semantic Kernel for optimization
            if self.kernel:
                response = await self.kernel.invoke_prompt(optimization_prompt)
                
                # Parse optimization results
                assignments = self._parse_optimization_response(str(response), pending_tasks, available_agents)
                
                log_semantic_kernel_event("OPTIMIZATION_COMPLETED", f"Tasks: {len(pending_tasks)}, Assignments: {len(assignments)}")
                
                return assignments
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error optimizing task assignment: {format_error_message(e)}")
            return []
    
    def get_planning_context(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get planning context for a specific task."""
        return self._planning_context.get(task_id)
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history for analysis."""
        return self._execution_history.copy()
    
    async def create_concurrent_orchestration_plan(
        self, 
        tasks: List[Task], 
        coordination_strategy: str = "dependency_aware"
    ) -> Optional[OrchestrationPlan]:
        """
        Create a concurrent orchestration plan for multiple tasks.
        
        Args:
            tasks: List of tasks to orchestrate
            coordination_strategy: Strategy for coordinating concurrent execution
            
        Returns:
            OrchestrationPlan or None if planning failed
        """
        try:
            if not self.kernel or not self.agent:
                self.logger.error("Semantic Kernel not initialized")
                return None
            
            # Create orchestration prompt
            orchestration_prompt = self._create_orchestration_prompt(tasks, coordination_strategy)
            
            # Add the orchestration request to chat history
            self.chat_history.add_user_message(orchestration_prompt)
            
            # Get orchestration response from agent
            response = await self.agent.invoke(self.kernel, self.chat_history)
            
            if response and hasattr(response, 'content'):
                plan_content = response.content
            else:
                plan_content = str(response)
            
            # Parse the orchestration plan
            orchestration_plan = await self._parse_orchestration_plan(plan_content, tasks)
            
            if orchestration_plan:
                self._active_orchestrations[orchestration_plan.plan_id] = orchestration_plan
                log_semantic_kernel_event("ORCHESTRATION_PLANNED", 
                                         f"Plan: {orchestration_plan.plan_id}, Tasks: {len(orchestration_plan.tasks)}")
            
            return orchestration_plan
        
        except Exception as e:
            self.logger.error(f"Error creating concurrent orchestration plan: {format_error_message(e)}")
            return None
    
    async def execute_concurrent_orchestration(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute a concurrent orchestration plan.
        
        Args:
            plan_id: ID of the orchestration plan to execute
            
        Returns:
            Execution results
        """
        try:
            plan = self._active_orchestrations.get(plan_id)
            if not plan:
                return {'error': f'Plan {plan_id} not found'}
            
            self.logger.info(f"Starting concurrent orchestration execution: {plan_id}")
            
            # Execute tasks based on orchestration mode
            if plan.mode == OrchestrationMode.CONCURRENT:
                results = await self._execute_concurrent_tasks(plan)
            elif plan.mode == OrchestrationMode.SEQUENTIAL:
                results = await self._execute_sequential_tasks(plan)
            else:  # HYBRID
                results = await self._execute_hybrid_tasks(plan)
            
            # Record execution in history
            execution_record = {
                'plan_id': plan_id,
                'mode': plan.mode.value,
                'task_count': len(plan.tasks),
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            self._execution_history.append(execution_record)
            
            log_semantic_kernel_event("ORCHESTRATION_COMPLETED", 
                                     f"Plan: {plan_id}, Success: {results.get('success', False)}")
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error executing concurrent orchestration: {format_error_message(e)}")
            return {'error': str(e)}
    
    async def _execute_concurrent_tasks(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks concurrently with dependency management."""
        completed_tasks = set()
        task_results = {}
        errors = []
        
        async def execute_task(task: ConcurrentTask):
            async with self._execution_semaphore:
                try:
                    # Wait for dependencies
                    await self._wait_for_dependencies(task, completed_tasks)
                    
                    # Execute the task
                    self.logger.info(f"Executing concurrent task: {task.task_id}")
                    result = await self._execute_single_task(task)
                    
                    async with self._coordination_lock:
                        task_results[task.task_id] = result
                        completed_tasks.add(task.task_id)
                        task.status = "completed"
                        task.result = result
                    
                    self.logger.info(f"Completed task: {task.task_id}")
                    
                except Exception as e:
                    async with self._coordination_lock:
                        errors.append(f"Task {task.task_id}: {str(e)}")
                        task.status = "failed"
                        task.error = str(e)
                    
                    self.logger.error(f"Task {task.task_id} failed: {e}")
        
        # Start all tasks concurrently
        task_coroutines = [execute_task(task) for task in plan.tasks]
        await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        success_count = len([t for t in plan.tasks if t.status == "completed"])
        
        return {
            'success': len(errors) == 0,
            'completed_tasks': success_count,
            'total_tasks': len(plan.tasks),
            'results': task_results,
            'errors': errors
        }
    
    async def _execute_sequential_tasks(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks sequentially."""
        task_results = {}
        errors = []
        
        for task in plan.tasks:
            try:
                self.logger.info(f"Executing sequential task: {task.task_id}")
                result = await self._execute_single_task(task)
                task_results[task.task_id] = result
                task.status = "completed"
                task.result = result
                
            except Exception as e:
                errors.append(f"Task {task.task_id}: {str(e)}")
                task.status = "failed"
                task.error = str(e)
                
                # Stop on first error in sequential mode
                if plan.failure_handling == "stop_on_error":
                    break
        
        success_count = len([t for t in plan.tasks if t.status == "completed"])
        
        return {
            'success': len(errors) == 0,
            'completed_tasks': success_count,
            'total_tasks': len(plan.tasks),
            'results': task_results,
            'errors': errors
        }
    
    async def _execute_hybrid_tasks(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute tasks with hybrid approach (concurrent where possible, sequential when needed)."""
        # Group tasks by dependency levels
        dependency_levels = self._analyze_dependency_levels(plan.tasks)
        
        task_results = {}
        errors = []
        
        for level_tasks in dependency_levels:
            # Execute all tasks at this level concurrently
            level_coroutines = []
            
            for task in level_tasks:
                async def execute_level_task(t):
                    try:
                        result = await self._execute_single_task(t)
                        async with self._coordination_lock:
                            task_results[t.task_id] = result
                            t.status = "completed"
                            t.result = result
                    except Exception as e:
                        async with self._coordination_lock:
                            errors.append(f"Task {t.task_id}: {str(e)}")
                            t.status = "failed"
                            t.error = str(e)
                
                level_coroutines.append(execute_level_task(task))
            
            # Wait for all tasks at this level to complete
            await asyncio.gather(*level_coroutines, return_exceptions=True)
        
        success_count = len([t for t in plan.tasks if t.status == "completed"])
        
        return {
            'success': len(errors) == 0,
            'completed_tasks': success_count,
            'total_tasks': len(plan.tasks),
            'results': task_results,
            'errors': errors
        }
    
    async def _wait_for_dependencies(self, task: ConcurrentTask, completed_tasks: set):
        """Wait for task dependencies to complete."""
        while not all(dep in completed_tasks for dep in task.dependencies):
            await asyncio.sleep(0.1)  # Check every 100ms
    
    async def _execute_single_task(self, task: ConcurrentTask) -> Any:
        """Execute a single task through an agent."""
        # Find the agent for this task
        agent = self.agent_manager.get_agent_by_id(task.agent_id)
        if not agent:
            raise ValueError(f"Agent {task.agent_id} not found")
        
        # Create task execution message
        execution_message = {
            'type': 'task_execution',
            'task_id': task.task_id,
            'action': task.action,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send task to agent (simplified - would use actual agent communication)
        # For now, simulate task execution
        await asyncio.sleep(min(task.estimated_duration, 5))  # Simulate work
        
        return {
            'status': 'completed',
            'result': f'Task {task.task_id} executed successfully',
            'duration': task.estimated_duration
        }
    
    def _analyze_dependency_levels(self, tasks: List[ConcurrentTask]) -> List[List[ConcurrentTask]]:
        """Analyze task dependencies and group into execution levels."""
        levels = []
        remaining_tasks = tasks.copy()
        completed_task_ids = set()
        
        while remaining_tasks:
            # Find tasks with no unmet dependencies
            level_tasks = [
                task for task in remaining_tasks 
                if all(dep in completed_task_ids for dep in task.dependencies)
            ]
            
            if not level_tasks:
                # Circular dependency or error - add remaining tasks to final level
                levels.append(remaining_tasks)
                break
            
            levels.append(level_tasks)
            completed_task_ids.update(task.task_id for task in level_tasks)
            remaining_tasks = [task for task in remaining_tasks if task not in level_tasks]
        
        return levels
    
    async def _index_agent_capabilities(self) -> None:
        """Index agent capabilities for context building."""
        try:
            agents = self.agent_manager.get_all_agents()
            
            # Build a capabilities summary for use in prompts
            capabilities_summary = []
            
            for agent in agents:
                agent_info = {
                    'name': agent.name,
                    'agent_id': agent.agent_id,
                    'status': agent.status.value,
                    'capabilities': []
                }
                
                for capability in agent.capabilities:
                    cap_info = {
                        'name': capability.name,
                        'description': capability.description,
                        'category': capability.category,
                        'requirements': capability.requirements or []
                    }
                    agent_info['capabilities'].append(cap_info)
                
                capabilities_summary.append(agent_info)
            
            # Store the summary for use in planning prompts
            self._planning_context['agent_capabilities'] = capabilities_summary
            
            self.logger.debug(f"Indexed capabilities for {len(agents)} agents")
        
        except Exception as e:
            self.logger.error(f"Error indexing agent capabilities: {e}")
    
    def _create_planning_prompt(self, task: Task) -> str:
        """Create a planning prompt for Semantic Kernel."""
        # Get available agent capabilities
        capabilities_info = ""
        if 'agent_capabilities' in self._planning_context:
            capabilities_info = "\n\nAvailable Agents and Capabilities:\n"
            for agent in self._planning_context['agent_capabilities']:
                capabilities_info += f"\nAgent: {agent['name']} (ID: {agent['agent_id']}, Status: {agent['status']})\n"
                for cap in agent['capabilities']:
                    capabilities_info += f"  - {cap['name']}: {cap['description']}\n"
        
        return f"""
        Create an execution plan for the following task:
        
        Task Name: {task.name}
        Description: {task.description}
        Required Capability: {task.capability_required}
        Parameters: {task.parameters}
        Priority: {task.priority}
        Dependencies: {task.dependencies}
        {capabilities_info}
        
        Please analyze and provide a JSON response with:
        {{
            "recommended_agent": "agent_id_of_best_match",
            "agent_name": "human_readable_agent_name",
            "estimated_duration": "estimated_time_in_seconds",
            "priority_adjustment": 0,
            "plan_steps": [
                {{"step": 1, "action": "description_of_action", "expected_outcome": "what_should_happen"}}
            ],
            "reasoning": "explanation_of_why_this_agent_and_approach"
        }}
        
        Consider:
        1. Available agent capabilities and current status
        2. Task complexity and requirements
        3. Optimal execution approach
        4. Risk mitigation strategies
        """
    
    def _create_orchestration_prompt(self, tasks: List[Task], coordination_strategy: str) -> str:
        """Create a prompt for concurrent orchestration planning."""
        task_info = []
        for i, task in enumerate(tasks):
            task_info.append(f"""
        Task {i+1}:
        - ID: {task.task_id}
        - Name: {task.name}
        - Description: {task.description}
        - Required Capability: {task.capability_required}
        - Dependencies: {task.dependencies}
        - Priority: {task.priority}
            """.strip())
        
        # Get available agents
        agents_info = ""
        if 'agent_capabilities' in self._planning_context:
            agents_info = "\n\nAvailable Agents:\n"
            for agent in self._planning_context['agent_capabilities']:
                agents_info += f"\nAgent: {agent['name']} (ID: {agent['agent_id']})\n"
                agents_info += f"Status: {agent['status']}\n"
                agents_info += "Capabilities:\n"
                for cap in agent['capabilities']:
                    agents_info += f"  - {cap['name']}: {cap['description']}\n"
        
        return f"""
        Create a concurrent orchestration plan for the following tasks using the {coordination_strategy} strategy:
        
        Tasks to Orchestrate:
        {chr(10).join(task_info)}
        {agents_info}
        
        Please provide a JSON response with an orchestration plan:
        {{
            "mode": "concurrent|sequential|hybrid",
            "coordination_strategy": "{coordination_strategy}",
            "tasks": [
                {{
                    "task_id": "task_id",
                    "agent_id": "best_agent_id",
                    "action": "specific_action_to_take",
                    "dependencies": ["dependency_task_ids"],
                    "estimated_duration": 30
                }}
            ],
            "success_criteria": ["criteria_for_success"],
            "failure_handling": "stop_on_error|continue_on_error",
            "coordination_notes": "explanation_of_coordination_approach"
        }}
        
        Consider:
        1. Task dependencies and ordering requirements
        2. Agent availability and capabilities
        3. Optimal concurrency vs sequential execution
        4. Resource conflicts and coordination needs
        5. Error handling and recovery strategies
        """
    
    async def _parse_orchestration_plan(self, plan_content: str, tasks: List[Task]) -> Optional[OrchestrationPlan]:
        """Parse the LLM response into an OrchestrationPlan."""
        try:
            # Try to extract JSON from the response
            if '{' in plan_content and '}' in plan_content:
                start = plan_content.find('{')
                end = plan_content.rfind('}') + 1
                json_content = plan_content[start:end]
                parsed_plan = json.loads(json_content)
                
                # Convert to OrchestrationPlan
                plan_id = f"orch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                mode = OrchestrationMode(parsed_plan.get('mode', 'concurrent'))
                
                concurrent_tasks = []
                for task_info in parsed_plan.get('tasks', []):
                    concurrent_task = ConcurrentTask(
                        task_id=task_info['task_id'],
                        agent_id=task_info['agent_id'],
                        action=task_info['action'],
                        dependencies=task_info.get('dependencies', []),
                        estimated_duration=task_info.get('estimated_duration', 30)
                    )
                    concurrent_tasks.append(concurrent_task)
                
                return OrchestrationPlan(
                    plan_id=plan_id,
                    mode=mode,
                    tasks=concurrent_tasks,
                    coordination_strategy=parsed_plan.get('coordination_strategy', 'dependency_aware'),
                    success_criteria=parsed_plan.get('success_criteria', []),
                    failure_handling=parsed_plan.get('failure_handling', 'continue_on_error'),
                    estimated_total_duration=sum(t.estimated_duration for t in concurrent_tasks)
                )
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(f"Failed to parse orchestration plan JSON: {e}")
            
            # Fallback: create a simple sequential plan
            return self._create_fallback_orchestration_plan(tasks)
        
        return None
    
    def _create_fallback_orchestration_plan(self, tasks: List[Task]) -> OrchestrationPlan:
        """Create a fallback orchestration plan when parsing fails."""
        plan_id = f"fallback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        concurrent_tasks = []
        for task in tasks:
            # Find best agent for each task
            best_agent = self.agent_manager.find_best_agent_for_capability(task.capability_required)
            agent_id = best_agent.agent_id if best_agent else "default_agent"
            
            concurrent_task = ConcurrentTask(
                task_id=task.task_id,
                agent_id=agent_id,
                action=f"Execute {task.name}",
                dependencies=task.dependencies or [],
                estimated_duration=60  # Default duration
            )
            concurrent_tasks.append(concurrent_task)
        
        return OrchestrationPlan(
            plan_id=plan_id,
            mode=OrchestrationMode.SEQUENTIAL,
            tasks=concurrent_tasks,
            coordination_strategy="fallback",
            success_criteria=["all_tasks_completed"],
            failure_handling="continue_on_error",
            estimated_total_duration=sum(60 for _ in tasks)
        )
    
    def get_active_orchestrations(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active orchestrations."""
        status = {}
        for plan_id, plan in self._active_orchestrations.items():
            status[plan_id] = {
                'mode': plan.mode.value,
                'total_tasks': len(plan.tasks),
                'completed_tasks': len([t for t in plan.tasks if t.status == "completed"]),
                'failed_tasks': len([t for t in plan.tasks if t.status == "failed"]),
                'pending_tasks': len([t for t in plan.tasks if t.status == "pending"]),
                'coordination_strategy': plan.coordination_strategy,
                'estimated_total_duration': plan.estimated_total_duration
            }
        return status
    
    def get_orchestration_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific orchestration."""
        plan = self._active_orchestrations.get(plan_id)
        if not plan:
            return None
        
        return {
            'plan_id': plan.plan_id,
            'mode': plan.mode.value,
            'coordination_strategy': plan.coordination_strategy,
            'success_criteria': plan.success_criteria,
            'failure_handling': plan.failure_handling,
            'estimated_total_duration': plan.estimated_total_duration,
            'tasks': [
                {
                    'task_id': task.task_id,
                    'agent_id': task.agent_id,
                    'action': task.action,
                    'dependencies': task.dependencies,
                    'estimated_duration': task.estimated_duration,
                    'status': task.status,
                    'result': task.result,
                    'error': task.error
                }
                for task in plan.tasks
            ]
        }
    
    async def _find_best_agent_for_task(self, task: Task) -> Optional[Agent]:
        """Find the best agent for executing a task."""
        return self.agent_manager.find_best_agent_for_capability(
            task.capability_required,
            exclude_busy=True
        )
    
    def _create_optimization_prompt(self, tasks: List[Task], agents: List[Agent]) -> str:
        """Create optimization prompt for task assignment."""
        task_info = []
        for task in tasks:
            task_info.append(f"- {task.name}: {task.capability_required} (Priority: {task.priority})")
        
        agent_info = []
        for agent in agents:
            capabilities = [cap.name for cap in agent.capabilities]
            agent_info.append(f"- {agent.name}: {', '.join(capabilities)} (Status: {agent.status.value})")
        
        return f"""
        Optimize the assignment of these tasks to available agents:
        
        Tasks:
        {chr(10).join(task_info)}
        
        Available Agents:
        {chr(10).join(agent_info)}
        
        Consider load balancing, capability matching, and priority optimization.
        Provide specific task-to-agent assignments with reasoning.
        """
    
    def _parse_optimization_response(self, response: str, tasks: List[Task], agents: List[Agent]) -> List[Dict[str, Any]]:
        """Parse the optimization response into assignment recommendations."""
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        assignments = []
        
        # Simple heuristic-based assignment as fallback
        for task in tasks:
            best_agent = self.agent_manager.find_best_agent_for_capability(task.capability_required)
            if best_agent:
                assignments.append({
                    'task_id': task.task_id,
                    'agent_id': best_agent.agent_id,
                    'confidence': 0.8,
                    'reasoning': f"Best available agent for {task.capability_required}"
                })
        
        return assignments
    
    def _extract_capability_from_analysis(self, analysis: str) -> str:
        """Extract required capability from analysis text."""
        # Simple extraction - would be more sophisticated in production
        if 'movement' in analysis.lower():
            return 'movement_control'
        elif 'camera' in analysis.lower() or 'vision' in analysis.lower():
            return 'camera_capture'
        elif 'sensor' in analysis.lower():
            return 'sensor_reading'
        else:
            return 'general'
    
    def _extract_complexity_from_analysis(self, analysis: str) -> str:
        """Extract complexity estimate from analysis text."""
        if 'simple' in analysis.lower() or 'basic' in analysis.lower():
            return 'low'
        elif 'complex' in analysis.lower() or 'advanced' in analysis.lower():
            return 'high'
        else:
            return 'medium'
    
    def _extract_risks_from_analysis(self, analysis: str) -> List[str]:
        """Extract risk factors from analysis text."""
        risks = []
        if 'timeout' in analysis.lower():
            risks.append('timeout_risk')
        if 'connection' in analysis.lower():
            risks.append('connection_risk')
        if 'hardware' in analysis.lower():
            risks.append('hardware_risk')
        return risks
