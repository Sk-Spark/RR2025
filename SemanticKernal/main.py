#!/usr/bin/env python3
"""
Semantic Kernel LED Control with Ollama
A Python script that uses Semantic Kernel and Ollama to control an LED on Raspberry Pi 5
via natural language commands through the terminal.
"""

import asyncio
import logging
import sys
from typing import Annotated

try:
    from gpiozero import LED
except ImportError:
    print("Warning: gpiozero not available. LED control will be simulated.")
    LED = None

import semantic_kernel as sk
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.functions import KernelArguments

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LEDController:
    """Handles LED hardware control with error handling."""
    
    def __init__(self, pin: int = 18):
        """Initialize LED controller with specified GPIO pin."""
        self.pin = pin
        self.led = None
        self.is_simulated = LED is None
        
        try:
            if not self.is_simulated:
                self.led = LED(pin)
                logger.info(f"LED controller initialized on GPIO pin {pin}")
            else:
                logger.warning("Running in simulation mode - no actual GPIO control")
        except Exception as e:
            logger.error(f"Failed to initialize LED on pin {pin}: {e}")
            self.is_simulated = True
    
    def turn_on(self) -> bool:
        """Turn on the LED."""
        try:
            if not self.is_simulated and self.led:
                self.led.on()
                logger.info("LED turned ON")
            else:
                logger.info("LED turned ON (simulated)")
            return True
        except Exception as e:
            logger.error(f"Failed to turn on LED: {e}")
            return False
    
    def turn_off(self) -> bool:
        """Turn off the LED."""
        try:
            if not self.is_simulated and self.led:
                self.led.off()
                logger.info("LED turned OFF")
            else:
                logger.info("LED turned OFF (simulated)")
            return True
        except Exception as e:
            logger.error(f"Failed to turn off LED: {e}")
            return False
    
    def get_status(self) -> str:
        """Get current LED status."""
        try:
            if not self.is_simulated and self.led:
                status = "ON" if self.led.is_lit else "OFF"
            else:
                status = "UNKNOWN (simulated)"
            return status
        except Exception as e:
            logger.error(f"Failed to get LED status: {e}")
            return "ERROR"
    
    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            if not self.is_simulated and self.led:
                self.led.close()
                logger.info("LED GPIO resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

class LEDControlPlugin:
    """Semantic Kernel plugin for LED control."""
    
    def __init__(self, led_controller: LEDController):
        self.led_controller = led_controller
    
    @kernel_function(
        description="Turn the LED on",
        name="turn_led_on"
    )
    def turn_led_on(self) -> Annotated[str, "Result of turning LED on"]:
        """Turn the LED on."""
        success = self.led_controller.turn_on()
        return "LED has been turned on successfully" if success else "Failed to turn on LED"
    
    @kernel_function(
        description="Turn the LED off",
        name="turn_led_off"
    )
    def turn_led_off(self) -> Annotated[str, "Result of turning LED off"]:
        """Turn the LED off."""
        success = self.led_controller.turn_off()
        return "LED has been turned off successfully" if success else "Failed to turn off LED"
    
    @kernel_function(
        description="Get the current status of the LED",
        name="get_led_status"
    )
    def get_led_status(self) -> Annotated[str, "Current LED status"]:
        """Get the current LED status."""
        status = self.led_controller.get_status()
        return f"LED is currently {status}"

class OllamaLEDAgent:
    """Main agent that uses Ollama and Semantic Kernel for LED control."""
    
    def __init__(self, model_name: str = "llama3.2:1b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.kernel = None
        self.led_controller = None
        self.led_plugin = None
        
    async def initialize(self, led_pin: int = 18):
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
            # Create a prompt that instructs the LLM to use the LED control functions
            prompt_template = """
You are an AI assistant that controls an LED on a Raspberry Pi. You have access to the following functions:
- turn_led_on: Turn the LED on
- turn_led_off: Turn the LED off  
- get_led_status: Get the current LED status

Analyze the user's request and call the appropriate function if they want to control the LED.
If the user wants to turn on the LED (phrases like "turn on", "switch on", "light up", "activate"), call turn_led_on.
If the user wants to turn off the LED (phrases like "turn off", "switch off", "turn it off", "deactivate"), call turn_led_off.
If the user wants to know the status, call get_led_status.
For any other requests, respond conversationally without calling functions.

User request: {{$user_input}}
"""
            
            # Create function with template
            led_function = self.kernel.add_function(
                plugin_name="main",
                function_name="led_control_handler",
                prompt=prompt_template,
                prompt_template_config=PromptTemplateConfig(
                    template=prompt_template,
                    name="led_control_handler",
                    description="Handle LED control commands"
                )
            )
            
            # Execute the function
            arguments = KernelArguments(user_input=user_input)
            result = await self.kernel.invoke(led_function, arguments)
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Sorry, I encountered an error processing your request: {e}"
    
    def cleanup(self):
        """Clean up resources."""
        if self.led_controller:
            self.led_controller.cleanup()

async def main():
    """Main function to run the LED control agent."""
    print("🤖 Semantic Kernel LED Control Agent")
    print("=" * 50)
    print("Commands you can try:")
    print("- 'turn on the LED' or 'switch on the light'")
    print("- 'turn off the LED' or 'switch off the light'")
    print("- 'what's the LED status?' or 'is the LED on?'")
    print("- 'quit' or 'exit' to stop")
    print("=" * 50)
    
    # Initialize agent
    agent = OllamaLEDAgent()
    
    try:
        # Initialize the agent
        if not await agent.initialize():
            print("❌ Failed to initialize agent. Please check Ollama is running and llama3.2:1b is available.")
            return
        
        print("✅ Agent initialized successfully!")
        print("\nType your commands below:")
        
        # Main interaction loop
        while True:
            try:
                user_input = input("\n🔹 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 Processing...")
                response = await agent.process_command(user_input)
                print(f"🤖 Agent: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print(f"❌ Error: {e}")
    
    finally:
        # Cleanup
        agent.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)