#!/usr/bin/env python3
"""
Ollama Agent Module
Main agent that uses Ollama and Semantic Kernel for LED and movement control.
"""

import logging
from typing import Optional

import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.functions import KernelArguments

from led_controller import LEDController
from led_plugin import LEDControlPlugin
from movement_controller import MovementController
from movement_plugin import MovementControlPlugin

logger = logging.getLogger(__name__)


class OllamaLEDAgent:
    """Main agent that uses Ollama and Semantic Kernel for LED and movement control."""
    
    def __init__(self, model_name: str = "llama3.2:1b", base_url: str = "http://localhost:11434", enable_movement: bool = True):
        """Initialize the Ollama LED agent."""
        self.model_name = model_name
        self.base_url = base_url
        self.enable_movement = enable_movement
        self.kernel: Optional[sk.Kernel] = None
        self.led_controller: Optional[LEDController] = None
        self.led_plugin: Optional[LEDControlPlugin] = None
        self.movement_controller: Optional[MovementController] = None
        self.movement_plugin: Optional[MovementControlPlugin] = None
        
    async def initialize(self, led_pin: int = 18, motor_config: Optional[dict] = None) -> bool:
        """Initialize the agent with LED controller, movement controller, and Semantic Kernel."""
        try:
            # Initialize LED controller
            self.led_controller = LEDController(led_pin)
            
            # Initialize movement controller if enabled
            if self.enable_movement:
                self.movement_controller = MovementController(motor_config=motor_config)
            
            # Initialize Semantic Kernel
            self.kernel = sk.Kernel()
            
            # Add Ollama chat completion service
            chat_completion = OllamaChatCompletion(
                ai_model_id=self.model_name
            )
            self.kernel.add_service(chat_completion)
            
            # Create and add LED control plugin
            self.led_plugin = LEDControlPlugin(self.led_controller)
            self.kernel.add_plugin(self.led_plugin, plugin_name="led_control")
            
            # Create and add movement control plugin if enabled
            if self.enable_movement and self.movement_controller:
                self.movement_plugin = MovementControlPlugin(self.movement_controller)
                self.kernel.add_plugin(self.movement_plugin, plugin_name="movement_control")
            
            logger.info(f"Agent initialized with model {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def process_command(self, user_input: str) -> str:
        """Process user command through Ollama and execute control functions if needed."""
        try:
            # Build the prompt with movement functions if enabled
            movement_section = ""
            movement_commands = ""
            
            if self.enable_movement:
                movement_section = """
                You also have access to these movement control functions:
                - move_forward: Move the robot forward for 1 second
                - move_backward: Move the robot backward for 1 second
                - turn_left: Turn the robot left for 1 second
                - turn_right: Turn the robot right for 1 second
                - strafe_left: Move the robot sideways left for 1 second
                - strafe_right: Move the robot sideways right for 1 second
                - stop_robot: Stop all robot movement immediately
                - get_movement_status: Get the current movement status"""
                
                movement_commands = """
- CALL_FUNCTION:move_forward
- CALL_FUNCTION:move_backward  
- CALL_FUNCTION:turn_left
- CALL_FUNCTION:turn_right
- CALL_FUNCTION:strafe_left
- CALL_FUNCTION:strafe_right
- CALL_FUNCTION:stop_robot
- CALL_FUNCTION:get_movement_status"""
            
            # Create the prompt with template variable
            prompt_template = f"""You are a robot control assistant. You must respond with EXACTLY one of these commands - nothing more, nothing less:

LED Commands:
- CALL_FUNCTION:turn_led_on
- CALL_FUNCTION:turn_led_off  
- CALL_FUNCTION:get_led_status{movement_section}

Movement Commands (if enabled):{movement_commands if self.enable_movement else ""}

For any other request, give a brief helpful response.

User: {{{{$user_input}}}}

Response (EXACT format only):"""

            # Create and invoke the function
            decision_function = self.kernel.add_function(
                plugin_name="decision",
                function_name="decide_action",
                prompt=prompt_template,
                prompt_template_config=PromptTemplateConfig(
                    template=prompt_template,
                    name="decide_action",
                    description="Decide which function to call based on user input"
                )
            )
            
            # Get the LLM's decision
            arguments = KernelArguments(user_input=user_input)
            decision_result = await self.kernel.invoke(decision_function, arguments)
            decision = str(decision_result).strip()
            
            logger.info(f"LLM decision: {decision}")
            
            # Parse the decision and call the appropriate function
            if "turn_led_on" in decision or "CALL_FUNCTION:turn_led_on" in decision:
                logger.info("LLM decided to turn LED on")
                return self.led_plugin.turn_led_on()
            elif "turn_led_off" in decision or "CALL_FUNCTION:turn_led_off" in decision:
                logger.info("LLM decided to turn LED off")
                return self.led_plugin.turn_led_off()
            elif "get_led_status" in decision or "CALL_FUNCTION:get_led_status" in decision:
                logger.info("LLM decided to get LED status")
                return self.led_plugin.get_led_status()
            elif self.enable_movement and ("move_forward" in decision or "CALL_FUNCTION:move_forward" in decision):
                logger.info("LLM decided to move forward")
                return await self.movement_plugin.move_forward()
            elif self.enable_movement and ("move_backward" in decision or "CALL_FUNCTION:move_backward" in decision):
                logger.info("LLM decided to move backward")
                return await self.movement_plugin.move_backward()
            elif self.enable_movement and ("turn_left" in decision or "CALL_FUNCTION:turn_left" in decision):
                logger.info("LLM decided to turn left")
                return await self.movement_plugin.turn_left()
            elif self.enable_movement and ("turn_right" in decision or "CALL_FUNCTION:turn_right" in decision):
                logger.info("LLM decided to turn right")
                return await self.movement_plugin.turn_right()
            elif self.enable_movement and ("strafe_left" in decision or "CALL_FUNCTION:strafe_left" in decision):
                logger.info("LLM decided to strafe left")
                return await self.movement_plugin.strafe_left()
            elif self.enable_movement and ("strafe_right" in decision or "CALL_FUNCTION:strafe_right" in decision):
                logger.info("LLM decided to strafe right")
                return await self.movement_plugin.strafe_right()
            elif self.enable_movement and ("stop_robot" in decision or "CALL_FUNCTION:stop_robot" in decision):
                logger.info("LLM decided to stop robot")
                return self.movement_plugin.stop_robot()
            elif self.enable_movement and ("get_movement_status" in decision or "CALL_FUNCTION:get_movement_status" in decision):
                logger.info("LLM decided to get movement status")
                return self.movement_plugin.get_movement_status()
            else:
                # Return the conversational response from the LLM
                return decision
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Sorry, I encountered an error processing your request: {e}"
    
    def cleanup(self):
        """Clean up resources."""
        if self.led_controller:
            self.led_controller.cleanup()
        if self.movement_controller:
            self.movement_controller.cleanup()
