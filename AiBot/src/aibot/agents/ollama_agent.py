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
from ..hardware.camera_controller import CameraPanTiltController
from ..plugins.movement_plugin import MovementControlPlugin
from ..plugins.camera_plugin import CameraControlPlugin

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
        self.camera_controller: Optional[CameraPanTiltController] = None
        self.camera_plugin: Optional[CameraControlPlugin] = None
        
    async def initialize(self, motor_config: Optional[dict] = None) -> bool:
        """Initialize the agent with movement controller and Semantic Kernel."""
        try:
            # Initialize movement controller
            self.movement_controller = MovementController(motor_config=motor_config)
            
            # Initialize camera controller
            self.camera_controller = CameraPanTiltController()
            
            # Initialize Semantic Kernel
            self.kernel = sk.Kernel()
            
            # Add Ollama chat completion service
            chat_completion = OllamaChatCompletion(
                ai_model_id=self.model_name,
                service_id="ollama_chat"
            )
            self.kernel.add_service(chat_completion)
            
            # Create movement and camera plugins
            self.movement_plugin = MovementControlPlugin(self.movement_controller)
            self.camera_plugin = CameraControlPlugin(self.camera_controller)
            
            # Create the actual ChatCompletionAgent with movement and camera plugins
            self.agent = ChatCompletionAgent(
                kernel=self.kernel,
                name="RobotControlAgent",
                plugins=[self.movement_plugin, self.camera_plugin],
                instructions="""You are a robot control assistant with access to movement and camera control functions.

Available Movement Functions:
- move_forward: Move robot forward (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- move_backward: Move robot backward (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- turn_left: Turn robot left (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- turn_right: Turn robot right (speed: 0-100%, duration: 0.1-10.0 seconds, defaults: 50%, 1.0s)
- stop_robot: Stop all robot movement immediately
- get_movement_status: Get current movement status

Available Camera Functions:
- pan_to_angle: Pan camera to specific angle (0-180 degrees)
- tilt_to_angle: Tilt camera to specific angle (0-180 degrees)
- pan_relative: Pan camera relatively (positive=right, negative=left)
- tilt_relative: Tilt camera relatively (positive=up, negative=down)
- set_camera_position: Set both pan and tilt angles simultaneously
- center_camera: Center camera to default position (90°, 90°)
- pan_sweep: Perform smooth pan sweep between angles
- tilt_sweep: Perform smooth tilt sweep between angles
- security_scan: Perform security scan pattern (360° sweep)
- get_camera_position: Get current camera position
- track_target: Track target smoothly with adjustable speed

CRITICAL EXECUTION RULES:
1. Only call the functions present in the available functions list.
2. EXECUTE ONLY ONE MOVEMENT AT A TIME. Wait for currently running movement to finish before starting the next movement.
3. Camera operations can run independently of movement operations.
4. Do not process any tool call in parallel. Always process tool calls one after the other.
5. When user asks for camera control, use appropriate camera functions.
6. Combine movement and camera operations for patrol, surveillance, and tracking tasks.
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
        if self.camera_controller:
            self.camera_controller.cleanup()
