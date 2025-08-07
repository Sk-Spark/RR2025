#!/usr/bin/env /home/spark/.venv/bin/python
"""
Main entry point for the Orchestrator Agent.
Runs exclusively in interactive mode for scenario management.
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


async def main():
    """Main function to run the orchestrator in interactive mode only."""
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        
        # Create orchestrator
        orchestrator = Orchestrator(config_manager)
        
        print("\n" + "="*80)
        print("🤖 ORCHESTRATOR AGENT - INTERACTIVE MODE")
        print("="*80)
        print("🚀 Starting orchestrator with terminal interface...")
        print("💡 Orchestrator will maintain connections to all AI bot agents")
        print("🎯 Ready to receive scenarios and break them into tasks")
        print("="*80)
        
        # Start orchestrator with terminal interface (interactive mode only)
        await orchestrator.start_with_terminal_interface()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested by user...")
    except Exception as e:
        print(f"\n❌ Error starting orchestrator: {e}")
        sys.exit(1)
    finally:
        if 'orchestrator' in locals():
            await orchestrator.stop()
        print("✅ Orchestrator stopped gracefully. Goodbye! 👋")


def run_orchestrator():
    """Entry point function for running the orchestrator."""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            sys.exit(1)
        
        # Show usage information if help requested
        if "--help" in sys.argv or "-h" in sys.argv:
            print("\n🤖 ORCHESTRATOR AGENT")
            print("="*50)
            print("Usage:")
            print("  python main.py                    - Run in interactive mode")
            print("  python main_interactive.py        - Direct interactive mode")
            print("\nThe Orchestrator Agent now runs exclusively in interactive mode.")
            print("It maintains connections to all AI bot agents and waits for")
            print("scenarios from users to break down into tasks and assign to agents.")
            print("="*50)
            return
        
        # Run the main async function
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_orchestrator()