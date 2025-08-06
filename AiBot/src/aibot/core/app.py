#!/usr/bin/env python3
"""
LED Control Application
Main application entry point for the Semantic Kernel LED Control with Ollama.
Enhanced with orchestrator communication.
"""

import asyncio
import logging
import sys
import uuid
from typing import Optional

from .config import ConfigManager
from ..agents.ollama_agent import OllamaLEDAgent
from ..communication.orchestrator_client import OrchestratorClient


def setup_logging(config_manager: ConfigManager) -> None:
    """Set up logging configuration."""
    config = config_manager.get_config()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=config.log_format
    )


class LEDControlApp:
    """Main LED control application with orchestrator communication."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize the LED control application."""
        self.config_manager = config_manager or ConfigManager()
        self.agent: Optional[OllamaLEDAgent] = None
        self.orchestrator_client: Optional[OrchestratorClient] = None
        self.logger = logging.getLogger(__name__)
        self.agent_id = f"rpi_led_{uuid.uuid4().hex[:8]}"
        self.is_interactive_mode = True
        
        # Set up logging
        setup_logging(self.config_manager)
        
    async def initialize(self) -> bool:
        """Initialize the application."""
        try:
            # Validate configuration
            if not self.config_manager.validate_config():
                self.logger.error("Configuration validation failed")
                return False
            
            config = self.config_manager.get_config()
            
            # Creating the agent
            self.agent = OllamaLEDAgent(
                model_name=config.model_name,
                base_url=config.base_url,
                enable_movement=config.enable_movement
            )
            
            # Initialize the agent
            if not await self.agent.initialize(led_pin=config.led_pin, motor_config=config.motor_config):
                self.logger.error("Failed to initialize agent")
                return False
            
            # Initialize orchestrator client if URL is provided
            if config.orchestrator_url:
                self.orchestrator_client = OrchestratorClient(
                    orchestrator_url=config.orchestrator_url,
                    agent_id=config.agent_id or self.agent_id,
                    max_reconnect_attempts=config.max_reconnect_attempts,
                    reconnect_delay=config.reconnect_delay
                )
                
                # Register message handlers
                self.setup_orchestrator_handlers()
                
                # Connect to orchestrator
                if await self.orchestrator_client.connect():
                    self.logger.info("Connected to orchestrator")
                    self.is_interactive_mode = False  # Disable interactive mode when connected to orchestrator
                else:
                    self.logger.warning("Failed to connect to orchestrator, running in standalone mode")
            
            self.logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            return False
    
    def print_welcome(self) -> None:
        """Print welcome message and usage instructions."""
        config = self.config_manager.get_config()
        
        if config.enable_movement:
            print("🤖 Semantic Kernel LED & Movement Control Agent")
        else:
            print("🤖 Semantic Kernel LED Control Agent")
        print("=" * 50)
        
        if config.orchestrator_url:
            print(f"🌐 Orchestrator Mode: {config.orchestrator_url}")
            print(f"🆔 Agent ID: {config.agent_id or self.agent_id}")
        else:
            print("💻 Interactive Mode")
            print("Commands you can try:")
            print("💡 LED Commands:")
            print("- 'turn on the LED' or 'switch on the light'")
            print("- 'turn off the LED' or 'switch off the light'")
            print("- 'what's the LED status?' or 'is the LED on?'")
            
            if config.enable_movement:
                print("🚗 Movement Commands:")
                print("- 'move forward' or 'go ahead'")
                print("- 'move backward' or 'go back'")
                print("- 'turn left' or 'turn right'")
                print("- 'strafe left' or 'strafe right'")
                print("- 'stop robot' or 'stop moving'")
                print("- 'movement status' or 'are you moving?'")
            
            print("ℹ️  Other:")
            print("- 'help' for more information")
            print("- 'quit' or 'exit' to stop")
        
        print("=" * 50)
    
    async def run_interactive_loop(self) -> None:
        """Run the interactive command loop."""
        print("✅ Agent initialized successfully!")
        print("\nType your commands below:")
        
        while True:
            try:
                user_input = input("\n🔹 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() in ['help', 'h']:
                    self.print_help()
                    continue
                
                if not user_input:
                    continue
                
                print("🤔 Processing...")
                response = await self.agent.process_command(user_input)
                print(f"🤖 Agent: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive loop: {e}")
                print(f"❌ Error: {e}")
    
    def print_help(self) -> None:
        """Print help information."""
        config = self.config_manager.get_config()
        
        help_text = """
            🔧 LED Control Commands:
            • "turn on the LED" - Turn the LED on
            • "turn off the LED" - Turn the LED off
            • "LED status" - Check current LED status
            • "switch on the light" - Alternative turn on command
            • "switch off the light" - Alternative turn off command
            """
        
        if config.enable_movement:
            help_text += """
            🚗 Movement Commands (1 second duration each):
            • "move forward" or "go ahead" - Move forward
            • "move backward" or "go back" - Move backward  
            • "turn left" - Turn left
            • "turn right" - Turn right
            • "strafe left" - Move sideways left (mecanum wheels)
            • "strafe right" - Move sideways right (mecanum wheels)
            • "stop robot" or "stop moving" - Stop all movement
            • "movement status" - Check if robot is moving
            """
        
        help_text += """
            💬 Other Commands:
            • "help" - Show this help message
            • "quit" or "exit" - Exit the application

            🎯 Tips:
            • Use natural language - the AI understands various phrasings
            • Movement commands automatically stop after 1 second for safety
            • The AI will respond conversationally for other topics
        """
        print(help_text)
    
    async def run(self) -> None:
        """Run the main application."""
        self.print_welcome()
        
        try:
            if not await self.initialize():
                print("❌ Failed to initialize agent. Please check Ollama is running and llama3.2:1b is available.")
                return
            
            # Start periodic status updates if connected to orchestrator
            if self.orchestrator_client and self.orchestrator_client.is_connected:
                asyncio.create_task(self.send_periodic_status())
                print("🌐 Connected to orchestrator - running in orchestrator mode")
                print("   Agent will respond to orchestrator commands")
                
                # In orchestrator mode, just wait for commands
                await self.run_orchestrator_mode()
            else:
                # Run in interactive mode
                await self.run_interactive_loop()
            
        finally:
            await self.cleanup()
    
    async def run_orchestrator_mode(self):
        """Run in orchestrator mode - wait for commands."""
        print("🔄 Agent is running and listening for orchestrator commands...")
        print("   Press Ctrl+C to stop")
        
        try:
            # Keep the application running while connected to orchestrator
            while (self.orchestrator_client and 
                   self.orchestrator_client.is_connected and
                   self.orchestrator_client.should_reconnect):
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down agent...")
        except Exception as e:
            self.logger.error(f"Error in orchestrator mode: {e}")
            print(f"❌ Error in orchestrator mode: {e}")
    
    async def cleanup(self) -> None:
        """Clean up application resources."""
        self.logger.info("Starting application cleanup...")
        
        # Disconnect from orchestrator
        if self.orchestrator_client:
            await self.orchestrator_client.disconnect()
        
        # Clean up agent
        if self.agent:
            self.agent.cleanup()
        
        self.logger.info("Application cleanup completed")
    
    def setup_orchestrator_handlers(self):
        """Setup message handlers for orchestrator communication."""
        if not self.orchestrator_client:
            return
        
        self.orchestrator_client.register_handler("welcome", self.handle_orchestrator_welcome)
        self.orchestrator_client.register_handler("command", self.handle_orchestrator_command)
        self.orchestrator_client.register_handler("query", self.handle_orchestrator_query)
        self.logger.info("Orchestrator message handlers registered")
    
    async def handle_orchestrator_welcome(self, message: dict):
        """Handle welcome message from orchestrator."""
        try:
            self.logger.info(f"Received welcome message: {message}")
            if self.orchestrator_client:
                await self.orchestrator_client.send_status_update("Agent initialized and ready")
        except Exception as e:
            self.logger.error(f"Error handling welcome message: {e}")
    
    async def handle_orchestrator_command(self, data: dict):
        """Handle command from orchestrator."""
        try:
            request_id = data.get("payload", {}).get("request_id")
            command = data.get("payload", {}).get("command")
            
            self.logger.info(f"Received command from orchestrator: {command}")
            
            # Process command through agent
            if self.agent:
                response = await self.agent.process_command(command)
                
                # Get LED status for response data
                led_status = "unknown"
                if hasattr(self.agent, 'led_controller') and self.agent.led_controller:
                    led_status = self.agent.led_controller.get_status()
                
                # Send response back to orchestrator
                if self.orchestrator_client:
                    await self.orchestrator_client.send_command_response(
                        request_id=request_id,
                        success=True,
                        response=response,
                        data={
                            "led_status": led_status,
                            "agent_id": self.agent_id
                        }
                    )
            else:
                if self.orchestrator_client:
                    await self.orchestrator_client.send_command_response(
                        request_id=request_id,
                        success=False,
                        error="Agent not initialized"
                    )
                
        except Exception as e:
            self.logger.error(f"Error handling orchestrator command: {e}")
            if self.orchestrator_client:
                await self.orchestrator_client.send_command_response(
                    request_id=request_id,
                    success=False,
                    error=str(e)
                )
    
    async def handle_orchestrator_query(self, data: dict):
        """Handle query from orchestrator."""
        try:
            request_id = data.get("payload", {}).get("request_id")
            query_type = data.get("payload", {}).get("query_type")
            
            response_data = {}
            
            if query_type == "status":
                # Get LED status
                led_status = "unknown"
                if self.agent and hasattr(self.agent, 'led_controller') and self.agent.led_controller:
                    led_status = self.agent.led_controller.get_status()
                
                response_data = {
                    "led_status": led_status,
                    "agent_status": "active",
                    "capabilities": ["led_control", "status_monitoring", "natural_language_processing"],
                    "agent_id": self.agent_id
                }
            elif query_type == "capabilities":
                response_data = {
                    "capabilities": ["led_control", "status_monitoring", "natural_language_processing"],
                    "agent_type": "rpi_led_controller",
                    "version": "1.0.0"
                }
            elif query_type == "stats":
                stats = self.orchestrator_client.get_stats() if self.orchestrator_client else {}
                response_data = {
                    "connection_stats": stats,
                    "agent_id": self.agent_id
                }
            
            if self.orchestrator_client:
                await self.orchestrator_client.send_command_response(
                    request_id=request_id,
                    success=True,
                    data=response_data
                )
                
        except Exception as e:
            self.logger.error(f"Error handling orchestrator query: {e}")
            if self.orchestrator_client:
                await self.orchestrator_client.send_command_response(
                    request_id=request_id,
                    success=False,
                    error=str(e)
                )
    
    async def send_periodic_status(self):
        """Send periodic status updates to orchestrator."""
        while self.orchestrator_client and self.orchestrator_client.is_connected:
            try:
                led_status = "unknown"
                additional_data = {}
                
                if self.agent and hasattr(self.agent, 'led_controller') and self.agent.led_controller:
                    led_status = self.agent.led_controller.get_status()
                
                # Add system information
                additional_data = {
                    "agent_id": self.agent_id,
                    "mode": "orchestrator" if not self.is_interactive_mode else "interactive",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                await self.orchestrator_client.send_status_update(led_status, additional_data)
                await asyncio.sleep(60)  # Send status every 60 seconds
                
            except Exception as e:
                self.logger.error(f"Error sending periodic status: {e}")
                await asyncio.sleep(60)

async def main() -> None:
    """Main entry point."""
    app = LEDControlApp()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program terminated by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
