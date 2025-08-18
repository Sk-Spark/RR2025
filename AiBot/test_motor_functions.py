#!/usr/bin/env python3
"""
Test individual motor functions to see where the False is coming from
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.hardware.movement_controller import MovementController

def test_motor_functions():
    """Test motor functions individually"""
    print("🔧 Testing individual motor functions...")
    
    controller = MovementController()
    
    print("🧪 Testing set_motor_speed...")
    result1 = controller.set_motor_speed("front_right", 50, "forward")
    print(f"set_motor_speed('front_right', 50, 'forward') returned: {result1}")
    
    result2 = controller.set_motor_speed("front_left", 50, "forward") 
    print(f"set_motor_speed('front_left', 50, 'forward') returned: {result2}")
    
    print("🧪 Testing _execute_forward...")
    result3 = controller._execute_forward(50)
    print(f"_execute_forward(50) returned: {result3}")
    
    print("🧪 Testing stop_all_motors...")
    result4 = controller.stop_all_motors()
    print(f"stop_all_motors() returned: {result4}")
    
    controller.cleanup()
    print("✅ Test completed")

if __name__ == "__main__":
    test_motor_functions()
