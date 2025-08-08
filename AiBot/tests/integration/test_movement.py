#!/usr/bin/env python3
"""
Test movement command script.
"""

import asyncio
import sys
sys.path.append('/home/spark/RR2025/AiBot')

async def test_movement():
    try:
        print("Testing movement command...")
        from aibot.core.app import BotControlApp
        
        app = BotControlApp()
        
        # Initialize
        if await app.initialize():
            print("App initialized successfully")
            
            # Test a movement command
            print("\n🤖 Testing 'move forward' command...")
            response = await app.agent.process_command("move forward")
            print(f"Response: {response}")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Test another command
            print("\n🤖 Testing 'turn left' command...")
            response = await app.agent.process_command("turn left")
            print(f"Response: {response}")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Test stop command
            print("\n🤖 Testing 'stop robot' command...")
            response = await app.agent.process_command("stop robot")
            print(f"Response: {response}")
            
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
    result = asyncio.run(test_movement())
    print(f"Test complete: {result}")
