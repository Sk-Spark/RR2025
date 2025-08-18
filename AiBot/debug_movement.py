#!/usr/bin/env python3
"""
Debug the movement_with_timeout function step by step
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.hardware.movement_controller import MovementController

async def debug_movement_timeout():
    """Debug the _movement_with_timeout function"""
    print("🔧 Debugging _movement_with_timeout...")
    
    controller = MovementController()
    
    # Test the _movement_with_timeout function directly
    print("🧪 Testing _movement_with_timeout directly...")
    try:
        result = await controller._movement_with_timeout(controller._execute_forward, 50, 0.5)
        print(f"_movement_with_timeout returned: {result}")
    except Exception as e:
        print(f"_movement_with_timeout raised exception: {e}")
    
    controller.cleanup()
    print("✅ Debug completed")

if __name__ == "__main__":
    asyncio.run(debug_movement_timeout())
