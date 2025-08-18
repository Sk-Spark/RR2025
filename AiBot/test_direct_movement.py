#!/usr/bin/env python3
"""
Quick diagnosis test - Test movement controller directly without plugin wrapper
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.hardware.movement_controller import MovementController

async def test_direct_movement():
    """Test movement controller directly"""
    print("🔧 Testing movement controller directly...")
    
    # Initialize movement controller
    controller = MovementController()
    
    print("🧪 Testing move_forward directly...")
    result = await controller.move_forward(speed=50, duration=0.5)
    print(f"move_forward returned: {result}")
    
    print("🧪 Testing turn_right directly...")
    result = await controller.turn_right(speed=50, duration=0.3)
    print(f"turn_right returned: {result}")
    
    print("🧪 Testing stop_all_motors...")
    result = controller.stop_all_motors()
    print(f"stop_all_motors returned: {result}")
    
    controller.cleanup()
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_direct_movement())
