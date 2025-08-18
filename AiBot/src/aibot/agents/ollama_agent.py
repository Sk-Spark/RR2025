#!/usr/bin/env python3
"""
Ollama Agent Module
Main agent that uses Ollama and Semantic Kernel for LED and movement control.
"""

import json
import logging
import asyncio
from typing import Optional

import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings

from ..hardware.movement_controller import MovementController
from ..plugins.movement_plugin import MovementControlPlugin

logger = logging.getLogger(__name__)


class OllamaBotAgent:
    """Main agent that uses Ollama and Semantic Kernel for bot control (LED and movement)."""
    
    def __init__(self, model_name: str = "llama3.2:1b", base_url: str = "http://localhost:11434"):
        """Initialize the Ollama bot agent."""
        self.model_name = model_name
        self.base_url = base_url
        self.kernel: Optional[sk.Kernel] = None
        self.agent: Optional[ChatCompletionAgent] = None
        self.chat_history = ChatHistory()
        self.movement_controller: Optional[MovementController] = None
        self.movement_plugin: Optional[MovementControlPlugin] = None
        
    async def initialize(self, motor_config: Optional[dict] = None) -> bool:
        """Initialize the agent with movement controller and Semantic Kernel."""
        try:
            # Initialize movement controller
            self.movement_controller = MovementController(motor_config=motor_config)
            
            # Initialize Semantic Kernel
            self.kernel = sk.Kernel()
            
            # Add Ollama chat completion service
            chat_completion = OllamaChatCompletion(
                ai_model_id=self.model_name,
                service_id="ollama_chat"
            )
            self.kernel.add_service(chat_completion)
            
            # Create movement plugin only
            self.movement_plugin = MovementControlPlugin(self.movement_controller)
            
            # Create the actual ChatCompletionAgent with movement plugin only
            self.agent = ChatCompletionAgent(
                kernel=self.kernel,
                name="RobotControlAgent",
                plugins=[self.movement_plugin],
                instructions="""You are a robot control assistant with access to movement control functions.

Available Movement Functions:
- move_forward: Move robot forward (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- move_backward: Move robot backward (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- turn_left: Turn robot left (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- turn_right: Turn robot right (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- stop_robot: Stop all robot movement immediately
- get_movement_status: Get current movement status

CRITICAL EXECUTION RULES:
1. EXECUTE ONLY ONE MOVEMENT AT A TIME - Each function call includes automatic timing and stopping.
2. For complex patterns think through the sequence step by step.
3. Call ONE function, let it complete (it will auto-stop), then proceed to the next step.
4. Always use the provided functions rather than describing what you would do.
5. Do not ask what to do next.
6. Do not explain your plan, just plan the sequence to complete the task given to you and execute respective functions sequentially one by one.

Speed & Duration Tips:
- Quick movements: 0.2-0.5 seconds duration
- Normal movements: 1-2 seconds duration
- Long movements: 2-5 seconds duration
- Turning: Usually 0.3-0.8 seconds for 90° turns
- Speed: slow=30%, normal=50%, fast=80%

""",
            )
            
            logger.info(f"Agent initialized with model {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def process_command(self, user_input: str) -> str:
        """Process user command through the Semantic Kernel agent."""
        try:
            if not self.agent:
                return "Agent not initialized. Please call initialize() first."
            
            # Add user message to chat history
            self.chat_history.add_user_message(user_input)
            
            response_parts = []
            async for message in self.agent.invoke(self.chat_history, kernel=self.kernel):
                response_parts.append(str(message))
            
            # Combine all response parts
            response = "\n".join(response_parts) if response_parts else "No response received"
            
            # Add agent response to history for context
            self.chat_history.add_assistant_message(response)
            
            # Log the interaction
            logger.info(f"User: {user_input}")
            logger.info(f"Agent: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Sorry, I encountered an error processing your request: {e}"
    
    def cleanup(self):
        """Clean up resources."""
        if self.movement_controller:
            self.movement_controller.cleanup()
