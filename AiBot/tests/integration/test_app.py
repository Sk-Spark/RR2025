#!/usr/bin/env python3
"""
Simple test script to diagnose the issue.
"""

import asyncio
import sys
sys.path.append('/home/spark/RR2025/AiBot/src')

async def test_app():
    try:
        print("Testing app initialization...")
        from aibot.core.app import BotControlApp
        print("App imported successfully")
        
        app = BotControlApp()
        print("App instance created")
        
        # Try to initialize
        if await app.initialize():
            print("App initialized successfully")
            print("Available commands:")
            print("- 'turn on LED' or 'LED on'")
            print("- 'turn off LED' or 'LED off'") 
            print("- 'move forward'")
            print("- 'turn left'")
            print("- 'turn right'")
            print("- 'strafe left'")
            print("- 'strafe right'")
            print("- 'stop robot'")
            print("- 'quit' to exit")
            return True
        else:
            print("Failed to initialize app")
            return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_app())
    print(f"Test result: {result}")
