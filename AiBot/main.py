#!/usr/bin/env python3
"""
Main Entry Point for AiBot
This file provides the main entry point for the AiBot application.
"""

import argparse
import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aibot import BotControlApp, Config


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AiBot - Intelligent Robot Control System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Interactive mode (default)
  python main.py -m i                         # Interactive mode (short)
  python main.py --mode interactive           # Interactive mode (explicit)
  python main.py -m o                         # Orchestrator mode (short)
  python main.py --mode orchestrator          # Orchestrator mode (explicit)
        """
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['interactive', 'orchestrator', 'i', 'o'],
        default='interactive',
        help='Operation mode: interactive/i (terminal input) or orchestrator/o (WebSocket commands)'
    )
    
    parser.add_argument(
        '--agent-id', '-a',
        type=str,
        help='Custom agent ID for orchestrator mode'
    )
    
    return parser.parse_args()


def create_config_from_args(args):
    """Create configuration object from command-line arguments."""
    config_manager = Config()
    config = config_manager.get_config()
    
    # Normalize mode (handle short forms)
    mode = args.mode
    if mode == 'i':
        mode = 'interactive'
    elif mode == 'o':
        mode = 'orchestrator'
    
    # Set orchestrator configuration based on mode
    if mode == 'orchestrator':
        # Check if orchestrator URL is configured
        if not config.orchestrator_url:
            print("❌ Error: Orchestrator mode requires orchestrator_url to be configured")
            print("   Please set ORCHESTRATOR_URL in config/aibot_config.py")
            print("   Example: ORCHESTRATOR_URL = 'ws://localhost:8080'")
            sys.exit(1)
        
        if args.agent_id:
            config.agent_id = args.agent_id
        print(f"🌐 Orchestrator mode: {config.orchestrator_url}")
    else:
        # Disable orchestrator for interactive mode
        config.orchestrator_url = None
        print("💻 Interactive mode")
    
    return config_manager, mode


async def main():
    """Main entry point for the AiBot application."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create configuration from arguments
    config_manager, mode = create_config_from_args(args)
    config = config_manager.get_config()
    
    # Print startup information
    print("🤖 AiBot - Intelligent Robot Control System")
    print("=" * 50)
    print(f"Mode: {mode}")
    if mode == 'orchestrator':
        print(f"Orchestrator URL: {config.orchestrator_url}")
        if config.agent_id:
            print(f"Agent ID: {config.agent_id}")
    print("=" * 50)
    
    # Create and run application
    app = BotControlApp(config_manager)
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program terminated by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)