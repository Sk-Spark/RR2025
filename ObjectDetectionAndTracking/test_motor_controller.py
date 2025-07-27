#!/usr/bin/env python3
"""
Test Motor Controller
Simple test script to verify motor controller functionality
"""

import time
import sys
from motor_controller import MotorController
import config

def test_motors():
    """Test all motor functions"""
    print("=== Motor Controller Test ===")
    
    try:
        # Initialize motor controller
        print("Initializing motor controller...")
        motor_controller = MotorController(
            motor_config=config.MOTOR_CONFIG,
            i2c_address=config.PCA9685_ADDRESS,
            frequency=config.MOTOR_PWM_FREQUENCY
        )
        
        print("Motor controller initialized successfully!")
        print("Motor configuration:")
        for name, motor in config.MOTOR_CONFIG.items():
            print(f"  {name}: Channel {motor['channel']}, IN1={motor['in1']}, IN2={motor['in2']}")
        
        print("\nStarting motor tests...")
        print("Press Ctrl+C to stop at any time")
        
        # Test 1: Individual motor test
        print("\n1. Testing individual motors...")
        for motor_name in config.MOTOR_CONFIG.keys():
            print(f"Testing {motor_name} - forward 2 seconds...")
            motor_controller.set_motor_speed(motor_name, 30, "forward")
            time.sleep(2)
            
            print(f"Testing {motor_name} - backward 2 seconds...")
            motor_controller.set_motor_speed(motor_name, 30, "backward")
            time.sleep(2)
            
            motor_controller.stop_motor(motor_name)
            time.sleep(1)
        
        # Test 2: Basic movements
        print("\n2. Testing basic movements...")
        movements = [
            ("Forward", lambda: motor_controller.move_forward(40)),
            ("Backward", lambda: motor_controller.move_backward(40)),
            ("Turn Left", lambda: motor_controller.turn_left(40)),
            ("Turn Right", lambda: motor_controller.turn_right(40)),
        ]
        
        for name, func in movements:
            print(f"Testing {name} for 3 seconds...")
            func()
            time.sleep(3)
            motor_controller.stop_all_motors()
            time.sleep(1)
        
        # Test 3: Mecanum movements
        print("\n3. Testing mecanum movements...")
        mecanum_movements = [
            ("Strafe Left", lambda: motor_controller.strafe_left(40)),
            ("Strafe Right", lambda: motor_controller.strafe_right(40)),
        ]
        
        for name, func in mecanum_movements:
            print(f"Testing {name} for 3 seconds...")
            func()
            time.sleep(3)
            motor_controller.stop_all_motors()
            time.sleep(1)
        
        # Test 4: Advanced mecanum control
        print("\n4. Testing advanced mecanum control...")
        test_movements = [
            ("Move forward-right", 30, 30, 0),
            ("Move backward-left", -30, -30, 0),
            ("Rotate while moving forward", 0, 30, 20),
            ("Complex movement", 20, 20, 10),
        ]
        
        for name, x, y, rot in test_movements:
            print(f"Testing {name}: X={x}, Y={y}, Rot={rot} for 3 seconds...")
            motor_controller.mecanum_move(x, y, rot)
            time.sleep(3)
            motor_controller.stop_all_motors()
            time.sleep(1)
        
        # Test 5: Ball following simulation
        print("\n5. Testing ball following simulation...")
        print("Simulating ball at different positions...")
        
        # Simulate ball positions (x, y in pixels, frame size 640x640)
        ball_positions = [
            (320, 320, "Center - no movement"),
            (500, 320, "Right - strafe right"),
            (140, 320, "Left - strafe left"),
            (320, 200, "Top - move forward"),
            (320, 440, "Bottom - move backward"),
            (500, 200, "Top-right - diagonal"),
        ]
        
        for ball_x, ball_y, description in ball_positions:
            print(f"Ball position: {description}")
            move_x, move_y = motor_controller.follow_ball(ball_x, ball_y, 640, 640, speed=30)
            print(f"  Robot movement: X={move_x}, Y={move_y}")
            time.sleep(3)
            motor_controller.stop_all_motors()
            time.sleep(1)
        
        print("\nAll tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always stop motors
        if 'motor_controller' in locals():
            print("Stopping all motors...")
            motor_controller.stop_all_motors()
            motor_controller.cleanup()
        print("Motor test completed")

if __name__ == "__main__":
    test_motors()
