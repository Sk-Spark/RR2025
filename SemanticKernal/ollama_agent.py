#!/usr/bin/env python3
"""
Ollama Agent Module
Main agent that uses Ollama and Semantic Kernel for LED control.
"""

import logging
from typing import Optional

import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.functions import KernelArguments

from led_controller import LEDController
from led_plugin import LEDControlPlugin

logger = logging.getLogger(__name__)


class OllamaLEDAgent:
    """Main agent that uses Ollama and Semantic Kernel for LED control."""
    
    def __init__(self, model_name: str = "llama3.2:1b", base_url: str = "http://localhost:11434"):
        """Initialize the Ollama LED agent."""
        self.model_name = model_name
        self.base_url = base_url
        self.kernel: Optional[sk.Kernel] = None
        self.led_controller: Optional[LEDController] = None
        self.led_plugin: Optional[LEDControlPlugin] = None
        
    async def initialize(self, led_pin: int = 18) -> bool:
        """Initialize the agent with LED controller and Semantic Kernel."""
        try:
            # Initialize LED controller
            self.led_controller = LEDController(led_pin)
            
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
            
            logger.info(f"Agent initialized with model {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def process_command(self, user_input: str) -> str:
        """Process user command through Ollama and execute LED control if needed."""
        try:
            # Create a prompt that instructs the LLM to decide which function to call
            prompt_template = """You are an AI assistant that controls an LED on a Raspberry Pi 5. 
You have access to these LED control functions:
- turn_led_on: Turn the LED on
- turn_led_off: Turn the LED off  
- get_led_status: Get the current LED status

Based on the user's request below, decide what action to take and respond with ONLY ONE of these:
- If they want to turn on the LED: respond with exactly "CALL_FUNCTION:turn_led_on"
- If they want to turn off the LED: respond with exactly "CALL_FUNCTION:turn_led_off"
- If they want to check LED status: respond with exactly "CALL_FUNCTION:get_led_status"
- For anything else: respond with a helpful conversational message

User request: {{$user_input}}

Your response:"""

            # Create and invoke the function
            decision_function = self.kernel.add_function(
                plugin_name="decision",
                function_name="decide_action",
                prompt=prompt_template,
                prompt_template_config=PromptTemplateConfig(
                    template=prompt_template,
                    name="decide_action",
                    description="Decide which LED function to call"
                )
            )
            
            # Get the LLM's decision
            arguments = KernelArguments(user_input=user_input)
            decision_result = await self.kernel.invoke(decision_function, arguments)
            decision = str(decision_result).strip()
            
            logger.info(f"LLM decision: {decision}")
            
            # Parse the decision and call the appropriate function
            if "CALL_FUNCTION:turn_led_on" in decision:
                logger.info("LLM decided to turn LED on")
                return self.led_plugin.turn_led_on()
            elif "CALL_FUNCTION:turn_led_off" in decision:
                logger.info("LLM decided to turn LED off")
                return self.led_plugin.turn_led_off()
            elif "CALL_FUNCTION:get_led_status" in decision:
                logger.info("LLM decided to get LED status")
                return self.led_plugin.get_led_status()
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
