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
        "front_right": {"channel": 15, "in1": 14, "in2": 13},
        "front_left": {"channel": 4, "in1": 5, "in2": 6},
        "rear_right": {"channel": 10, "in1": 12, "in2": 11},
        "rear_left": {"channel": 9, "in1": 7, "in2": 8},
    }
    
    # Servo configuration as specified
    servos = {
        "camera_tilt": 3,
        "camera_pan": 2,
    }
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Robot Control System")
    parser.add_argument("--mode", choices=["demo", "patrol", "test", "camera", "interactive"], 
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
        elif args.mode == "camera":
            camera_test(robot)
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
    
    # Test mecanum movements
    print("\n4. Testing Mecanum Movements...")
    mecanum_movements = [
        ("Strafe Left", lambda: robot.strafe_left(30, 2)),
        ("Strafe Right", lambda: robot.strafe_right(30, 2)),
        ("Diagonal Forward-Left", lambda: robot.move_diagonal_forward_left(30, 1.5)),
        ("Diagonal Forward-Right", lambda: robot.move_diagonal_forward_right(30, 1.5)),
        ("Rotate Clockwise", lambda: robot.rotate_clockwise(30, 1)),
        ("Rotate Counter-clockwise", lambda: robot.rotate_counterclockwise(30, 1)),
    ]
    
    for name, func in mecanum_movements:
        print(f"Testing {name}...")
        func()
        time.sleep(0.5)
    
    # Test camera positions with smooth movements
    print("\n5. Testing Camera Positions (Smooth Movements)...")
    camera_tests = [
        ("Look Up (Smooth)", lambda: robot.camera_look_up(30, smooth=True)),
        ("Look Down (Smooth)", lambda: robot.camera_look_down(30, smooth=True)),
        ("Look Left (Smooth)", lambda: robot.camera_look_left(45, smooth=True)),
        ("Look Right (Smooth)", lambda: robot.camera_look_right(45, smooth=True)),
        ("Center (Smooth)", lambda: robot.camera_center(smooth=True)),
    ]
    
    for name, func in camera_tests:
        print(f"Testing {name}...")
        func()
        time.sleep(1.5)  # Longer wait for smooth movements
    
    # Quick comparison test
    print("\n6. Smooth vs Jerky Movement Comparison...")
    print("   - Jerky movement (old style)...")
    robot.servo_controller.set_servo_angle("camera_pan", 45)
    time.sleep(0.2)
    robot.servo_controller.set_servo_angle("camera_pan", 135)
    time.sleep(0.2)
    robot.servo_controller.set_servo_angle("camera_pan", 90)
    time.sleep(1)
    
    print("   - Smooth movement (new style)...")
    robot.servo_controller.smooth_move_servo("camera_pan", 45, 0.8, "ease_in_out")
    time.sleep(1)
    robot.servo_controller.smooth_move_servo("camera_pan", 135, 0.8, "ease_in_out")
    time.sleep(1)
    robot.servo_controller.smooth_move_servo("camera_pan", 90, 0.8, "ease_in_out")
    time.sleep(1)
    
    print("\nTest mode completed!")


def interactive_mode(robot):
    """Interactive mode - manual control"""
    print("=== Interactive Mode ===")
    print("Basic Controls:")
    print("  w/s - forward/backward")
    print("  a/d - turn left/right")
    print("  q/e - pivot left/right")
    print("Mecanum Controls:")
    print("  z/x - strafe left/right")
    print("  u/o - diagonal forward-left/right")
    print("  m/. - diagonal backward-left/right")
    print("  r/t - rotate counter-clockwise/clockwise")
    print("Camera Controls:")
    print("  i/k - camera up/down")
    print("  j/l - camera left/right")
    print("  c - center camera")
    print("System:")
    print("  n - stop all")
    print("  h - show help")
    print("  ESC or Ctrl+C - exit")
    print()
    
    speed = 50
    
    try:
        while True:
            command = input(f"Enter command (speed={speed}%): ").strip().lower()
            
            # Basic movement
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
            
            # Mecanum movement
            elif command == 'z':
                robot.strafe_left(speed, 0.5)
            elif command == 'x':
                robot.strafe_right(speed, 0.5)
            elif command == 'u':
                robot.move_diagonal_forward_left(speed, 0.5)
            elif command == 'o':
                robot.move_diagonal_forward_right(speed, 0.5)
            elif command == 'm':
                robot.move_diagonal_backward_left(speed, 0.5)
            elif command == '.':
                robot.move_diagonal_backward_right(speed, 0.5)
            elif command == 'r':
                robot.rotate_counterclockwise(speed, 0.5)
            elif command == 't':
                robot.rotate_clockwise(speed, 0.5)
            
            # Camera control (smooth by default)
            elif command == 'i':
                robot.camera_look_up(30, smooth=True)
            elif command == 'k':
                robot.camera_look_down(30, smooth=True)
            elif command == 'j':
                robot.camera_look_left(30, smooth=True)
            elif command == 'l':
                robot.camera_look_right(30, smooth=True)
            elif command == 'c':
                robot.camera_center(smooth=True)
            
            # Camera control (instant movement - hold shift)
            elif command == 'I':
                robot.camera_look_up(30, smooth=False)
            elif command == 'K':
                robot.camera_look_down(30, smooth=False)
            elif command == 'J':
                robot.camera_look_left(30, smooth=False)
            elif command == 'L':
                robot.camera_look_right(30, smooth=False)
            elif command == 'C':
                robot.camera_center(smooth=False)
            
            # System control
            elif command == 'n':
                robot.stop_movement()
            elif command == 'h':
                print("=== Robot Control Commands ===")
                print("Basic Movement: w/s/a/d/q/e")
                print("Mecanum: z/x/u/o/m/./r/t")
                print("Camera (Smooth): i/k/j/l/c")
                print("Camera (Instant): I/K/J/L/C")
                print("System: n(stop) | speed=<0-100> | h(help)")
                print("Advanced: mecanum <x> <y> <rot>")
                print("Exit: exit/quit/Ctrl+C")
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
            elif command.startswith('mecanum '):
                # Advanced mecanum control: mecanum x y rot
                try:
                    parts = command.split()
                    if len(parts) == 4:
                        x_speed = int(parts[1])
                        y_speed = int(parts[2])
                        rot_speed = int(parts[3])
                        robot.mecanum_move(x_speed, y_speed, rot_speed, 1.0)
                    else:
                        print("Usage: mecanum <x_speed> <y_speed> <rotation_speed>")
                        print("Example: mecanum 50 30 -20 (move forward-right while rotating left)")
                except ValueError:
                    print("Invalid mecanum command format")
            elif command in ['exit', 'quit', '\x1b']:  # ESC key
                break
            elif command == '':
                continue
            else:
                print("Unknown command. Type 'h' for help.")
    
    except KeyboardInterrupt:
        print("\nExiting interactive mode...")
    
    robot.stop_movement()


def camera_test(robot):
    """Test camera movements with smooth animations"""
    print("=== Camera Test Mode ===")
    print("Testing smooth servo movements...")
    
    try:
        # Test smooth movements with different easing functions
        print("\n1. Testing ease-in-out movements...")
        robot.servo_controller.smooth_set_camera_position(90, 90, 1.0, "ease_in_out")  # Center
        time.sleep(1)
        
        print("2. Looking up smoothly...")
        robot.servo_controller.smooth_move_servo("camera_tilt", 45, 1.5, "ease_in_out")
        time.sleep(2)
        
        print("3. Looking down smoothly...")
        robot.servo_controller.smooth_move_servo("camera_tilt", 135, 1.5, "ease_in_out")
        time.sleep(2)
        
        print("4. Looking left smoothly...")
        robot.servo_controller.smooth_move_servo("camera_pan", 135, 1.5, "ease_in_out")
        time.sleep(2)
        
        print("5. Looking right smoothly...")
        robot.servo_controller.smooth_move_servo("camera_pan", 45, 1.5, "ease_in_out")
        time.sleep(2)
        
        print("6. Returning to center with both servos...")
        robot.servo_controller.smooth_set_camera_position(90, 90, 2.0, "ease_in_out")
        time.sleep(3)
        
        print("\n7. Testing different easing functions...")
        
        # Test ease-in
        print("   - Ease-in movement...")
        robot.servo_controller.smooth_move_servo("camera_tilt", 60, 1.0, "ease_in")
        time.sleep(1.5)
        
        # Test ease-out  
        print("   - Ease-out movement...")
        robot.servo_controller.smooth_move_servo("camera_tilt", 120, 1.0, "ease_out")
        time.sleep(1.5)
        
        # Test linear
        print("   - Linear movement...")
        robot.servo_controller.smooth_move_servo("camera_tilt", 90, 1.0, "linear")
        time.sleep(1.5)
        
        print("\n8. Quick comparison: Jerky vs Smooth")
        
        # Jerky movement
        print("   - Jerky movements (old style)...")
        robot.servo_controller.set_servo_angle("camera_pan", 45)
        time.sleep(0.1)
        robot.servo_controller.set_servo_angle("camera_pan", 90)
        time.sleep(0.1)
        robot.servo_controller.set_servo_angle("camera_pan", 135)
        time.sleep(0.1)
        robot.servo_controller.set_servo_angle("camera_pan", 90)
        time.sleep(1)
        
        # Smooth movement
        print("   - Smooth movements (new style)...")
        robot.servo_controller.smooth_move_servo("camera_pan", 45, 0.8, "ease_in_out")
        time.sleep(0.9)
        robot.servo_controller.smooth_move_servo("camera_pan", 135, 0.8, "ease_in_out")
        time.sleep(0.9)
        robot.servo_controller.smooth_move_servo("camera_pan", 90, 0.8, "ease_in_out")
        time.sleep(1)
        
        print("\nCamera test complete! Much smoother, right?")
        
    except KeyboardInterrupt:
        print("\nCamera test interrupted")
    finally:
        # Return to center
        robot.servo_controller.smooth_set_camera_position(90, 90, 1.0)


if __name__ == "__main__":
    main()