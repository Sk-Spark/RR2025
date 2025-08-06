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
        # Check for interactive mode flag
        interactive_mode = "--interactive" in sys.argv or "-i" in sys.argv
        
        # Initialize configuration
        config_manager = ConfigManager()
        
        # Create orchestrator
        orchestrator = Orchestrator(config_manager)
        
        if interactive_mode:
            print("\n" + "="*80)
            print("🤖 ORCHESTRATOR AGENT - INTERACTIVE MODE")
            print("="*80)
            print("🚀 Starting orchestrator with terminal interface...")
            
            # Start orchestrator with terminal interface
            await orchestrator.start_with_terminal_interface()
        else:
            # Start orchestrator normally
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
            print("💻 Run with --interactive flag for terminal interface.")
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
        
        # Show usage information if help requested
        if "--help" in sys.argv or "-h" in sys.argv:
            print("\n🤖 ORCHESTRATOR AGENT")
            print("="*50)
            print("Usage:")
            print("  python main.py                    - Run in daemon mode")
            print("  python main.py --interactive      - Run with terminal interface")
            print("  python main.py -i                 - Run with terminal interface (short)")
            print("  python main_interactive.py        - Direct interactive mode")
            print("\nModes:")
            print("  Daemon Mode:       Background operation, WebSocket API only")
            print("  Interactive Mode:  Terminal interface for direct commands")
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