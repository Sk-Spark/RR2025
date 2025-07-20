#!/usr/bin/env python3
"""
Xbox Controller Robot Control System
Integrates Xbox controller with motor and servo control for robot operation
"""

import sys
import argparse
from robot_controller import RobotController


def main():
    """Main function for Xbox controller robot control"""
    
    print("=== Xbox Controller Robot Control System ===")
    print("Modular robot control using Xbox gamepad")
    print()
    
    # Robot hardware configuration
    # Motor configuration (4 BO motors with PCA9685)
    motors = {
        "front_right": {"channel": 15, "in1": 14, "in2": 13},
        "front_left": {"channel": 4, "in1": 5, "in2": 6},
        "rear_right": {"channel": 10, "in1": 12, "in2": 11},
        "rear_left": {"channel": 9, "in1": 7, "in2": 8},
    }
    
    # Servo configuration (2 SG90 servos for camera pan/tilt)
    servos = {
        "camera_tilt": 3,
        "camera_pan": 2,
    }
    
    # Controller configuration
    controller_config = {
        "default_speed": 50,      # Default motor speed (%)
        "servo_increment": 5,     # Servo adjustment increment (degrees)
        "speed_increment": 10,    # Speed change increment (%)
        "max_speed": 100,         # Maximum motor speed (%)
        "min_speed": 20,          # Minimum motor speed (%)
    }
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Xbox Controller Robot Control System")
    parser.add_argument("--mode", choices=["control", "test-motors", "test-servos", "test-all"], 
                       default="control", help="Operation mode")
    parser.add_argument("--i2c-address", type=lambda x: int(x, 0), default=0x40,
                       help="I2C address of PCA9685 (default: 0x40)")
    parser.add_argument("--speed", type=int, default=50,
                       help="Default motor speed percentage (default: 50)")
    args = parser.parse_args()
    
    # Update controller config with command line arguments
    controller_config["default_speed"] = args.speed
    
    print(f"Mode: {args.mode}")
    print(f"I2C Address: {hex(args.i2c_address)}")
    print(f"Default Speed: {args.speed}%")
    print()
    
    try:
        # Initialize robot controller
        robot = RobotController(
            motor_config=motors,
            servo_config=servos,
            i2c_address=args.i2c_address,
            controller_config=controller_config
        )
        
        # Execute based on mode
        if args.mode == "control":
            # Start Xbox controller control
            success = robot.start()
            if not success:
                print("❌ Failed to start controller mode")
                return 1
        
        elif args.mode == "test-motors":
            print("🧪 Testing motors only...")
            robot.test_movement()
        
        elif args.mode == "test-servos":
            print("🧪 Testing servos only...")
            robot.test_servos()
        
        elif args.mode == "test-all":
            print("🧪 Testing all components...")
            robot.test_movement()
            robot.test_servos()
        
        return 0
        
    except KeyboardInterrupt:
        print("\\n⚠️  Program interrupted by user")
        return 0
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed in the virtual environment")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        if 'robot' in locals():
            robot.cleanup()


if __name__ == "__main__":
    sys.exit(main())