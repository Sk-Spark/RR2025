#!/usr/bin/env python3
"""
Quick start script for DummyAiBot in terminal mode
"""

import subprocess
import sys

def main():
    """Start the bot in terminal mode with preset configuration"""
    print("🚀 Starting DummyAiBot in Terminal Mode...")
    print("This will allow you to control the bot directly from the console.")
    print("=" * 60)
    
    # Run the main script with terminal mode flag
    try:
        subprocess.run([
            sys.executable, "main.py", 
            "--terminal",
            "--bot-id", "terminal_bot_001"
        ])
    except KeyboardInterrupt:
        print("\n👋 Terminal mode stopped.")

if __name__ == "__main__":
    main()
