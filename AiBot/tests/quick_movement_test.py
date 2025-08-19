#!/usr/bin/env python3
"""
Quick Movement Test for AiBot
A simple test to verify basic movement functionality
"""

import sys
import os
import time
import asyncio
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aibot.hardware.movement_controller import MovementController

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def quick_test():
    """Run a quick movement test"""
    print("🤖 AiBot Quick Movement Test")
    print("=============================")
    print("⚠️  This will move the robot motors briefly!")
    
    response = input("Continue? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("Test cancelled.")
        return False
    
    try:
        print("\n🔧 Initializing movement controller...")
        controller = MovementController()
        print("✅ Movement controller initialized")
        
        print("\n🧪 Testing individual motors...")
        motors = ["front_right", "front_left", "rear_right", "rear_left"]
        
        for motor in motors:
            print(f"  Testing {motor}...")
            controller.set_motor_speed(motor, 30, "forward")
            time.sleep(0.5)
            controller.stop_motor(motor)
            time.sleep(0.2)
        
        print("✅ Individual motor test completed")
        
        print("\n🧪 Testing emergency stop...")
        # Start all motors
        for motor in motors:
            controller.set_motor_speed(motor, 40, "forward")
        
        time.sleep(0.5)
        
        # Emergency stop
        controller.stop_all_motors()
        print("✅ Emergency stop test completed")
        
        print("\n🧹 Cleaning up...")
        controller.cleanup()
        
        print("\n🎉 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def quick_movement_test():
    """Run a quick movement pattern test"""
    print("\n🧪 Testing movement patterns...")
    
    try:
        controller = MovementController()
        
        # Test basic movements with short duration
        movements = [
            ("forward", controller.move_forward),
            ("backward", controller.move_backward),
            ("left turn", controller.turn_left),
            ("right turn", controller.turn_right)
        ]
        
        for name, move_func in movements:
            print(f"  Testing {name}...")
            await move_func(speed=30, duration=0.5)
            await asyncio.sleep(0.5)
        
        # Test strafe if available
        if hasattr(controller, 'strafe_left'):
            print("  Testing strafe left...")
            await controller.strafe_left(speed=30, duration=0.5)
            await asyncio.sleep(0.5)
        
        if hasattr(controller, 'strafe_right'):
            print("  Testing strafe right...")
            await controller.strafe_right(speed=30, duration=0.5)
            await asyncio.sleep(0.5)
        
        controller.cleanup()
        print("✅ Movement pattern test completed")
        return True
        
    except Exception as e:
        print(f"❌ Movement pattern test failed: {e}")
        return False


def main():
    """Main function"""
    try:
        # Run basic test
        if not quick_test():
            return False
        
        # Ask if user wants to test movement patterns
        response = input("\nTest movement patterns? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            success = asyncio.run(quick_movement_test())
            return success
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
