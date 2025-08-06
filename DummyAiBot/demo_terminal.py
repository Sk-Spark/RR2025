#!/usr/bin/env python3
"""Demo terminal session script"""

import subprocess
import sys
import time

def run_demo():
    print("🚀 Starting DummyAiBot Terminal Mode Demo")
    print("This will run a few commands to show terminal mode in action")
    
    # Commands to demo
    commands = [
        "status",
        "help", 
        "move forward 2",
        "camera center",
        "quit"
    ]
    
    # Create input string
    input_string = "\n".join(commands) + "\n"
    
    try:
        # Run the bot with the commands
        process = subprocess.Popen(
            [sys.executable, "main.py", "--terminal", "--bot-id", "demo_bot"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=input_string, timeout=30)
        
        print("=== BOT OUTPUT ===")
        print(stdout)
        if stderr:
            print("=== ERRORS ===")
            print(stderr)
            
    except subprocess.TimeoutExpired:
        print("Demo completed (timeout)")
        process.kill()
    except Exception as e:
        print(f"Demo failed: {e}")

if __name__ == "__main__":
    run_demo()
