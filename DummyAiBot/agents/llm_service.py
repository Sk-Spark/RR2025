#!/usr/bin/env python3
"""
LLM Service for DummyAiBot - Testing Ollama Integration
"""

import asyncio
import logging
import aiohttp
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LLMService:
    """Simple service for interacting with Ollama LLM"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the LLM service"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)  # Default 30 seconds
            )
            
            # Test connection
            if await self.test_connection():
                logger.info(f"LLM service initialized with model {self.model}")
                return True
            else:
                logger.error("Failed to connect to Ollama service")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing LLM service: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup LLM service resources"""
        if self.session:
            await self.session.close()
            logger.info("LLM service cleaned up")
    
    async def test_connection(self) -> bool:
        """Test connection to Ollama service"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model['name'] for model in data.get('models', [])]
                    logger.info(f"Available models: {models}")
                    return self.model in models
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def generate_response(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate response from LLM"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            request_data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.config.llm_temperature,
                    "num_predict": self.config.llm_max_tokens
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=request_data
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data.get('message', {}).get('content', '')
                else:
                    logger.error(f"LLM request failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return None
    
    async def analyze_task(self, task_description: str, capabilities: list) -> Dict[str, Any]:
        """Analyze task using LLM to determine execution plan"""
        system_prompt = f"""
        You are a robot AI assistant with the following capabilities: {', '.join(capabilities)}.
        Your job is to analyze tasks and create execution plans.
        
        If asked about your capabilities or what you can do, respond with a helpful description.
        
        For the given task, respond with a JSON object containing:
        1. "feasible" - boolean indicating if the task can be completed
        2. "required_capabilities" - list of capabilities needed
        3. "execution_steps" - list of steps to complete the task
        4. "estimated_duration" - estimated time in seconds
        5. "confidence" - confidence level (0.0 to 1.0)
        6. "response" - direct response to user (especially for questions about capabilities)
        
        Keep responses concise and practical for a testing robot.
        """
        
        prompt = f"Analyze this task: {task_description}"
        
        # Special handling for capability questions
        if any(word in task_description.lower() for word in ['what can you do', 'capabilities', 'what are you', 'abilities']):
            return {
                "feasible": True,
                "required_capabilities": ["status_reporting"],
                "execution_steps": ["List capabilities", "Describe functions"],
                "estimated_duration": 5,
                "confidence": 1.0,
                "response": f"I am a DummyAiBot with these capabilities: {', '.join(capabilities)}. I can simulate movement, camera control, execute tasks, reason with LLM, and provide status reports. I'm designed for testing and development purposes."
            }
        
        try:
            response = await self.generate_response(prompt, system_prompt)
            if response:
                # Try to parse JSON response
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # Fallback to simple analysis
                    return {
                        "feasible": True,
                        "required_capabilities": ["task_execution"],
                        "execution_steps": ["Analyze task", "Execute task", "Report completion"],
                        "estimated_duration": 30,
                        "confidence": 0.7,
                        "llm_response": response
                    }
            else:
                return self._default_task_analysis(task_description)
                
        except Exception as e:
            logger.error(f"Error analyzing task with LLM: {e}")
            return self._default_task_analysis(task_description)
    
    async def generate_action_plan(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """Generate action plan for task execution"""
        system_prompt = """
        You are a robot AI that creates action plans. Be specific and practical.
        Focus on actual robot actions like movement, camera control, and reporting.
        Keep plans simple and executable for testing purposes.
        """
        
        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context)}"
        
        prompt = f"Create an action plan for: {task_description}{context_str}"
        
        try:
            response = await self.generate_response(prompt, system_prompt)
            return response or "Execute task using available capabilities and report completion."
            
        except Exception as e:
            logger.error(f"Error generating action plan: {e}")
            return "Execute task using available capabilities and report completion."
    
    def _default_task_analysis(self, task_description: str) -> Dict[str, Any]:
        """Default task analysis when LLM is unavailable"""
        return {
            "feasible": True,
            "required_capabilities": ["task_execution"],
            "execution_steps": [
                "Receive task",
                "Process task description", 
                "Execute task simulation",
                "Report completion"
            ],
            "estimated_duration": 10,
            "confidence": 0.5,
            "note": "Default analysis - LLM unavailable"
        }
