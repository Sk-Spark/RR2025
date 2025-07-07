#!/usr/bin/env python3
"""
LED Control Application
Main application entry point for the Semantic Kernel LED Control with Ollama.
"""

import asyncio
import logging
import sys
from typing import Optional

from config import ConfigManager
from ollama_agent import OllamaLEDAgent


def setup_logging(config_manager: ConfigManager) -> None:
    """Set up logging configuration."""
    config = config_manager.get_config()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=config.log_format
    )


class LEDControlApp:
    """Main LED control application."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize the LED control application."""
        self.config_manager = config_manager or ConfigManager()
        self.agent: Optional[OllamaLEDAgent] = None
        self.logger = logging.getLogger(__name__)
        
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
            
            # Initialize the agent
            self.agent = OllamaLEDAgent(
                model_name=config.model_name,
                base_url=config.base_url
            )
            
            # Initialize the agent
            if not await self.agent.initialize(led_pin=config.led_pin):
                self.logger.error("Failed to initialize agent")
                return False
            
            self.logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            return False
    
    def print_welcome(self) -> None:
        """Print welcome message and usage instructions."""
        print("🤖 Semantic Kernel LED Control Agent")
        print("=" * 50)
        print("Commands you can try:")
        print("- 'turn on the LED' or 'switch on the light'")
        print("- 'turn off the LED' or 'switch off the light'")
        print("- 'what's the LED status?' or 'is the LED on?'")
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
        help_text = """
🔧 LED Control Commands:
• "turn on the LED" - Turn the LED on
• "turn off the LED" - Turn the LED off
• "LED status" - Check current LED status
• "switch on the light" - Alternative turn on command
• "switch off the light" - Alternative turn off command

💬 Other Commands:
• "help" - Show this help message
• "quit" or "exit" - Exit the application

🎯 Tips:
• Use natural language - the AI understands various phrasings
• Be specific about LED/light in your commands
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
            
            await self.run_interactive_loop()
            
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up application resources."""
        if self.agent:
            self.agent.cleanup()
        self.logger.info("Application cleanup completed")


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
