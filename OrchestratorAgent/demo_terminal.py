#!/usr/bin/env /home/spark/.venv/bin/python
"""
Demo script for testing the Orchestrator Agent Terminal Interface.
Shows how to use various commands and features.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Add config directory to Python path  
config_path = Path(__file__).parent / "config"
sys.path.insert(0, str(config_path))

from src.orchestrator import Orchestrator
from config import ConfigManager


async def run_demo():
    """Run a demo of the terminal interface."""
    print("\n🤖 ORCHESTRATOR AGENT - TERMINAL INTERFACE DEMO")
    print("="*60)
    print("This demo will start the orchestrator with terminal interface.")
    print("You can then use commands like:")
    print("  • help                        - Show all commands")
    print("  • status                      - Show system status")
    print("  • create Move robot forward   - Create a movement task")
    print("  • agents                      - List all agents")
    print("  • tasks                       - List all tasks")
    print("  • orchestrate Scan room       - Create complex orchestration")
    print("  • exit                        - Exit the interface")
    print("="*60)
    
    # Initialize and start
    config_manager = ConfigManager()
    orchestrator = Orchestrator(config_manager)
    
    print("\\n🚀 Starting orchestrator with terminal interface...")
    await orchestrator.start_with_terminal_interface()


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        sys.exit(1)
