"""
Ollama integration for the Orchestrator Agent.
Provides integration with locally running Ollama API for LLM capabilities.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass

from ..utils import get_logger, retry_with_backoff
from ..core.models import Agent, Task


@dataclass
class OllamaModelInfo:
    """Information about an Ollama model."""
    name: str
    size: int
    digest: str
    modified_at: str


class OllamaClient:
    """
    Client for interacting with Ollama API.
    Provides methods for model management and text generation.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: Base URL for Ollama API
            model: Default model to use for generation
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.logger = get_logger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt for generation
            model: Model to use (defaults to instance model)
            system_prompt: System prompt to set context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Generated text
        """
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        model_name = model or self.model
        
        # Prepare request payload
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            url = f"{self.base_url}/api/generate"
            
            async with self._session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
                
                if stream:
                    # Handle streaming response
                    full_response = ""
                    async for line in response.content:
                        if line:
                            data = json.loads(line)
                            if "response" in data:
                                full_response += data["response"]
                            if data.get("done", False):
                                break
                    return full_response
                else:
                    # Handle non-streaming response
                    data = await response.json()
                    return data.get("response", "")
        
        except Exception as e:
            self.logger.error(f"Error generating text with Ollama: {e}")
            raise
    
    @retry_with_backoff(max_retries=3)
    async def list_models(self) -> List[OllamaModelInfo]:
        """
        List available models in Ollama.
        
        Returns:
            List of available models
        """
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        try:
            url = f"{self.base_url}/api/tags"
            
            async with self._session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
                
                data = await response.json()
                models = []
                
                for model_data in data.get("models", []):
                    model_info = OllamaModelInfo(
                        name=model_data["name"],
                        size=model_data["size"],
                        digest=model_data["digest"],
                        modified_at=model_data["modified_at"]
                    )
                    models.append(model_info)
                
                return models
        
        except Exception as e:
            self.logger.error(f"Error listing Ollama models: {e}")
            raise
    
    async def check_health(self) -> bool:
        """
        Check if Ollama service is healthy.
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            # Create session if not exists
            if not self._session or self._session.closed:
                self._session = aiohttp.ClientSession()
            
            url = f"{self.base_url}/api/version"
            
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
        
        except Exception as e:
            self.logger.warning(f"Ollama health check failed: {e}")
            return False
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model to Ollama.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful, False otherwise
        """
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        try:
            url = f"{self.base_url}/api/pull"
            payload = {"name": model_name}
            
            async with self._session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Failed to pull model {model_name}: {error_text}")
                    return False
                
                # Monitor pull progress
                async for line in response.content:
                    if line:
                        data = json.loads(line)
                        if data.get("status") == "success":
                            self.logger.info(f"Successfully pulled model {model_name}")
                            return True
                        elif "error" in data:
                            self.logger.error(f"Error pulling model {model_name}: {data['error']}")
                            return False
                
                return True
        
        except Exception as e:
            self.logger.error(f"Error pulling model {model_name}: {e}")
            return False


class OllamaIntegration:
    """
    High-level integration with Ollama for the orchestrator.
    Provides semantic analysis and decision-making capabilities.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        """
        Initialize the Ollama integration.
        
        Args:
            base_url: Base URL for Ollama API
            model: Default model to use
        """
        self.client = OllamaClient(base_url, model)
        self.logger = get_logger(__name__)
        self._is_healthy = False
    
    async def initialize(self) -> bool:
        """
        Initialize the Ollama integration and check connectivity.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            async with self.client:
                self._is_healthy = await self.client.check_health()
                
                if self._is_healthy:
                    # Check if the model is available
                    models = await self.client.list_models()
                    model_names = [model.name for model in models]
                    
                    if self.client.model not in model_names:
                        self.logger.warning(f"Model {self.client.model} not found. Available models: {model_names}")
                        # Attempt to pull the model
                        self.logger.info(f"Attempting to pull model {self.client.model}")
                        success = await self.client.pull_model(self.client.model)
                        if not success:
                            self.logger.error(f"Failed to pull model {self.client.model}")
                            return False
                    
                    self.logger.info(f"Ollama integration initialized with model {self.client.model}")
                    return True
                else:
                    self.logger.error("Ollama service is not healthy")
                    return False
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama integration: {e}")
            return False
    
    async def analyze_task_requirements(self, task_description: str, available_agents: List[Agent]) -> Dict[str, Any]:
        """
        Analyze task requirements and suggest the best agent assignment.
        
        Args:
            task_description: Description of the task to analyze
            available_agents: List of available agents
            
        Returns:
            Analysis results with agent recommendations
        """
        try:
            # Build context about available agents
            agent_context = []
            for agent in available_agents:
                capabilities = [cap.name for cap in agent.capabilities]
                agent_context.append(f"Agent {agent.name} ({agent.agent_type}): {', '.join(capabilities)}")
            
            agents_info = "\n".join(agent_context)
            
            system_prompt = """You are an AI orchestrator that analyzes tasks and recommends the best agent assignment. 
You should respond with a JSON object containing:
- "recommended_agent": the best agent name for the task
- "confidence": confidence level (0-1)
- "reasoning": explanation of why this agent was chosen
- "required_capabilities": list of capabilities needed
- "estimated_complexity": complexity level (1-5)
- "dependencies": any task dependencies identified"""

            prompt = f"""
Task Description: {task_description}

Available Agents:
{agents_info}

Analyze this task and recommend the best agent assignment. Consider the agent capabilities, task complexity, and requirements.
"""

            async with self.client:
                response = await self.client.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,  # Lower temperature for more consistent analysis
                    max_tokens=500
                )
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.strip())
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "recommended_agent": available_agents[0].name if available_agents else None,
                    "confidence": 0.5,
                    "reasoning": "JSON parsing failed, using fallback recommendation",
                    "required_capabilities": [],
                    "estimated_complexity": 3,
                    "dependencies": [],
                    "raw_response": response
                }
        
        except Exception as e:
            self.logger.error(f"Error analyzing task requirements: {e}")
            return {
                "recommended_agent": None,
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
                "required_capabilities": [],
                "estimated_complexity": 1,
                "dependencies": []
            }
    
    async def generate_task_plan(self, goal: str, available_capabilities: List[str]) -> Dict[str, Any]:
        """
        Generate a detailed task plan to achieve a goal.
        
        Args:
            goal: The goal to achieve
            available_capabilities: List of available capabilities across all agents
            
        Returns:
            Generated task plan
        """
        try:
            capabilities_list = ", ".join(available_capabilities)
            
            system_prompt = """You are an AI task planner that breaks down goals into executable tasks.
Respond with a JSON object containing:
- "tasks": array of task objects with "name", "description", "capability_required", "priority", and "dependencies"
- "execution_order": recommended order of task execution
- "estimated_duration": total estimated duration in seconds
- "success_criteria": how to measure success"""

            prompt = f"""
Goal: {goal}

Available Capabilities: {capabilities_list}

Create a detailed plan to achieve this goal using the available capabilities. Break it down into specific, executable tasks.
"""

            async with self.client:
                response = await self.client.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.4,
                    max_tokens=800
                )
            
            try:
                plan = json.loads(response.strip())
                return plan
            except json.JSONDecodeError:
                return {
                    "tasks": [],
                    "execution_order": [],
                    "estimated_duration": 0,
                    "success_criteria": [],
                    "error": "Failed to parse plan response",
                    "raw_response": response
                }
        
        except Exception as e:
            self.logger.error(f"Error generating task plan: {e}")
            return {
                "tasks": [],
                "execution_order": [],
                "estimated_duration": 0,
                "success_criteria": [],
                "error": str(e)
            }
    
    async def analyze_system_status(self, agents: List[Agent], recent_tasks: List[Task]) -> str:
        """
        Analyze overall system status and provide insights.
        
        Args:
            agents: List of all agents
            recent_tasks: List of recent tasks
            
        Returns:
            System status analysis
        """
        try:
            # Build status summary
            total_agents = len(agents)
            online_agents = len([a for a in agents if a.status.value == "online"])
            
            task_statuses = {}
            for task in recent_tasks[-10:]:  # Last 10 tasks
                status = task.status.value
                task_statuses[status] = task_statuses.get(status, 0) + 1
            
            system_prompt = """You are a system analyst. Provide a concise status report and recommendations based on the system metrics provided."""

            prompt = f"""
System Metrics:
- Total Agents: {total_agents}
- Online Agents: {online_agents}
- Recent Task Status: {task_statuses}

Provide a brief analysis of system health and any recommendations for optimization.
"""

            async with self.client:
                response = await self.client.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.5,
                    max_tokens=300
                )
            
            return response.strip()
        
        except Exception as e:
            self.logger.error(f"Error analyzing system status: {e}")
            return f"System analysis unavailable: {str(e)}"
    
    @property
    def is_healthy(self) -> bool:
        """Check if Ollama integration is healthy."""
        return self._is_healthy
