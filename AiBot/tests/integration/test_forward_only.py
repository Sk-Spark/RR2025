#!/usr/bin/env python3
"""
Quick test for move forward command.
"""

import asyncio
import sys
sys.path.append('/home/spark/RR2025/AiBot')

async def test_move_forward():
    try:
        print("Testing move forward command...")
        from aibot.core.app import BotControlApp
        
        app = BotControlApp()
        
        # Initialize
        if await app.initialize():
            print("App initialized successfully")
            
            # Test just move forward
            print("\n🤖 Testing 'move forward' command...")
            response = await app.agent.process_command("move forward")
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
    result = asyncio.run(test_move_forward())
    print(f"Test complete: {result}")
