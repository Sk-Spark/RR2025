#!/usr/bin/env /home/spark/.venv/bin/python
"""
Main entry point for the Orchestrator Agent.
Initializes and runs the orchestrator with all its components.
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
    """Main function to run the orchestrator."""
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        
        # Create orchestrator
        orchestrator = Orchestrator(config_manager)
        
        # Start orchestrator
        await orchestrator.start()
        
        print("\n" + "="*60)
        print("🤖 ORCHESTRATOR AGENT STARTED SUCCESSFULLY! 🤖")
        print("="*60)
        print(f"📡 WebSocket Server: ws://{config_manager.config.websocket.host}:{config_manager.config.websocket.port}")
        print(f"🧠 Ollama Model: {config_manager.config.ollama.model}")
        print(f"🔗 Ollama URL: {config_manager.config.ollama.base_url}")
        print("="*60)
        print("💡 The orchestrator is ready to accept agent connections and tasks!")
        print("📝 Check the logs/ directory for detailed operation logs.")
        print("🛑 Press Ctrl+C to stop the orchestrator gracefully.")
        print("="*60 + "\n")
        
        # Wait for shutdown signal
        await orchestrator.wait_for_shutdown()
        
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
        
        # Run the main async function
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_orchestrator()