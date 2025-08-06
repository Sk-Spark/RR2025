#!/usr/bin/env python3
"""
AI Bot Agent for Testing with Orchestrator
Dummy implementation for testing communication and task execution
"""

import asyncio
import logging
import signal
import sys
import argparse
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from agents.dummy_bot import DummyAiBot
from config.settings import BotConfig


def setup_logging(terminal_mode=False):
    """Set up logging configuration."""
    level = logging.WARNING if terminal_mode else logging.INFO
    
    handlers = []
    if not terminal_mode:
        handlers.append(logging.FileHandler('logs/bot.log'))
    handlers.append(logging.StreamHandler(sys.stdout))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='DummyAiBot - AI Bot Agent for Testing')
    parser.add_argument(
        '--terminal', '-t',
        action='store_true',
        help='Run in terminal mode (accept commands from console instead of orchestrator)'
    )
    parser.add_argument(
        '--orchestrator-url',
        default='ws://localhost:8765',
        help='Orchestrator WebSocket URL (default: ws://localhost:8765)'
    )
    parser.add_argument(
        '--bot-id',
        default='dummy_ai_bot_001',
        help='Bot ID (default: dummy_ai_bot_001)'
    )
    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama API URL (default: http://localhost:11434)'
    )
    parser.add_argument(
        '--ollama-model',
        default='llama3.2:3b',
        help='Ollama model name (default: llama3.2:3b)'
    )
    
    return parser.parse_args()


async def main():
    """Main function to run the AI Bot Agent."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.terminal)
    logger = logging.getLogger(__name__)
    
    if args.terminal:
        print("** Starting DummyAiBot in TERMINAL MODE **")
    else:
        logger.info("Starting AI Bot Agent in ORCHESTRATOR MODE...")
    
    # Load configuration with command line overrides
    config = BotConfig()
    config.terminal_mode = args.terminal
    config.orchestrator_url = args.orchestrator_url
    config.agent_id = args.bot_id
    config.ollama_base_url = args.ollama_url
    config.ollama_model = args.ollama_model
    
    # Create and initialize the AI bot agent
    bot_agent = DummyAiBot(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        if not args.terminal:
            logger.info(f"Received signal {signum}. Shutting down...")
        asyncio.create_task(bot_agent.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the agent
        await bot_agent.initialize()
        
        # Start the agent
        await bot_agent.start()
        
    except KeyboardInterrupt:
        if not args.terminal:
            logger.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        if args.terminal:
            print(f"❌ Error running bot agent: {e}")
        else:
            logger.error(f"Error running bot agent: {e}", exc_info=True)
    finally:
        await bot_agent.shutdown()
        if not args.terminal:
            logger.info("AI Bot Agent stopped.")


if __name__ == "__main__":
    asyncio.run(main())
