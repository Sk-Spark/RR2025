#!/usr/bin/env python3
"""
Main Robot Control Script
Demonstrates usage of the modular robot controller for 4 BO motors and 2 SG90 servos
"""

import time
import argparse
from robot_controller import RobotController


def main():
    """Main function to demonstrate robot control"""
    
    # Motor configuration as specified
    motors = {
        "rear_left": {"channel": 0, "in1": 1, "in2": 12},
        "rear_right": {"channel": 6, "in1": 7, "in2": 8},
        "front_left": {"channel": 5, "in1": 4, "in2": 13},
        "front_right": {"channel": 11, "in1": 10, "in2": 9},
    }
    
    # Servo configuration as specified
    servos = {
        "camera_tilt": 3,
        "camera_pan": 2,
    }
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Robot Control System")
    parser.add_argument("--mode", choices=["demo", "patrol", "test", "interactive"], 
                       default="demo", help="Operation mode")
    parser.add_argument("--i2c-address", type=lambda x: int(x, 0), default=0x40,
                       help="I2C address of PCA9685 (default: 0x40)")
    args = parser.parse_args()
    
    print("=== Robot Control System ===")
    print(f"Mode: {args.mode}")
    print(f"I2C Address: {hex(args.i2c_address)}")
    print()
    
    try:
        # Initialize robot controller
        robot = RobotController(motors, servos, i2c_address=args.i2c_address)
        
        # Execute based on mode
        if args.mode == "demo":
            robot.demo_mode()
        elif args.mode == "patrol":
            robot.patrol_mode()
        elif args.mode == "test":
            test_mode(robot)
        elif args.mode == "interactive":
            interactive_mode(robot)
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'robot' in locals():
            robot.cleanup()


def test_mode(robot):
    """Test mode - test all components"""
    print("=== Test Mode ===")
    
    # Test motors
    print("\n1. Testing Motors...")
    robot.test_all_motors(speed=30, duration=1)
    
    # Test servos
    print("\n2. Testing Servos...")
    robot.test_all_servos(sweep_delay=0.1)
    
    # Test basic movements
    print("\n3. Testing Basic Movements...")
    movements = [
        ("Forward", lambda: robot.move_forward(30, 2)),
        ("Backward", lambda: robot.move_backward(30, 2)),
        ("Turn Left", lambda: robot.turn_left(30, 1)),
        ("Turn Right", lambda: robot.turn_right(30, 1)),
    ]
    
    for name, func in movements:
        print(f"Testing {name}...")
        func()
        time.sleep(0.5)
    
    # Test camera positions
    print("\n4. Testing Camera Positions...")
    camera_tests = [
        ("Look Up", lambda: robot.look_up(30)),
        ("Look Down", lambda: robot.look_down(30)),
        ("Look Left", lambda: robot.look_left(45)),
        ("Look Right", lambda: robot.look_right(45)),
        ("Center", lambda: robot.center_camera()),
    ]
    
    for name, func in camera_tests:
        print(f"Testing {name}...")
        func()
        time.sleep(1)
    
    print("\nTest mode completed!")


def interactive_mode(robot):
    """Interactive mode - manual control"""
    print("=== Interactive Mode ===")
    print("Commands:")
    print("  w/s - forward/backward")
    print("  a/d - turn left/right")
    print("  q/e - pivot left/right")
    print("  i/k - camera up/down")
    print("  j/l - camera left/right")
    print("  c - center camera")
    print("  x - stop all")
    print("  h - show help")
    print("  ESC or Ctrl+C - exit")
    print()
    
    speed = 50
    
    try:
        while True:
            command = input(f"Enter command (speed={speed}%): ").strip().lower()
            
            if command == 'w':
                robot.move_forward(speed, 0.5)
            elif command == 's':
                robot.move_backward(speed, 0.5)
            elif command == 'a':
                robot.turn_left(speed, 0.5)
            elif command == 'd':
                robot.turn_right(speed, 0.5)
            elif command == 'q':
                robot.pivot_left(speed, 0.5)
            elif command == 'e':
                robot.pivot_right(speed, 0.5)
            elif command == 'i':
                robot.look_up(30)
            elif command == 'k':
                robot.look_down(30)
            elif command == 'j':
                robot.look_left(30)
            elif command == 'l':
                robot.look_right(30)
            elif command == 'c':
                robot.center_camera()
            elif command == 'x':
                robot.stop_movement()
            elif command == 'h':
                print("Commands: w/s/a/d/q/e (movement), i/k/j/l (camera), c (center), x (stop)")
            elif command.startswith('speed='):
                try:
                    new_speed = int(command.split('=')[1])
                    if 0 <= new_speed <= 100:
                        speed = new_speed
                        print(f"Speed set to {speed}%")
                    else:
                        print("Speed must be between 0 and 100")
                except ValueError:
                    print("Invalid speed format. Use: speed=50")
            elif command == 'status':
                status = robot.get_status()
                print(f"Status: {status}")
            elif command in ['exit', 'quit', '\x1b']:  # ESC key
                break
            elif command == '':
                continue
            else:
                print("Unknown command. Type 'h' for help.")
    
    except KeyboardInterrupt:
        print("\nExiting interactive mode...")
    
    robot.stop_movement()


if __name__ == "__main__":
    main()