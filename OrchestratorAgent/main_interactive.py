#!/usr/bin/env /home/spark/.venv/bin/python
"""
Interactive main entry point for the Orchestrator Agent with Terminal Interface.
Provides an interactive command-line interface for controlling the orchestrator.
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
    """Main function to run the orchestrator with terminal interface."""
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        
        # Create orchestrator
        orchestrator = Orchestrator(config_manager)
        
        print("\n" + "="*80)
        print("🤖 ORCHESTRATOR AGENT - INTERACTIVE MODE")
        print("="*80)
        print("🚀 Starting orchestrator components...")
        
        # Start orchestrator with terminal interface
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


def run_interactive_orchestrator():
    """Entry point function for running the interactive orchestrator."""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            sys.exit(1)
        
        # Run the main async function
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_interactive_orchestrator()
