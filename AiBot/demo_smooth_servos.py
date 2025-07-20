#!/usr/bin/env python3
"""
Smooth Servo Movement Demo for AI Bot
Demonstrates the smooth camera pan/tilt movements
"""

import sys
import time
import signal

# Add paths for other modules
sys.path.append('/home/spark/RR2025/Motors_Servo_POC')

from robot_controller import RobotController

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\nShutting down demo...')
    if 'robot' in globals():
        robot.cleanup()
    sys.exit(0)

def main():
    print("🤖 AI Bot Smooth Servo Movement Demo")
    print("=====================================")
    print("This demo will show smooth camera movements")
    print("Press Ctrl+C to stop\n")
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Motor configuration
        motors = {
            "front_right": {"channel": 15, "in1": 14, "in2": 13},
            "front_left": {"channel": 4, "in1": 5, "in2": 6},
            "rear_right": {"channel": 10, "in1": 12, "in2": 11},
            "rear_left": {"channel": 9, "in1": 7, "in2": 8},
        }
        
        # Servo configuration
        servos = {
            "camera_tilt": 3,
            "camera_pan": 2,
        }
        
        # Initialize robot controller
        robot = RobotController(motors, servos, i2c_address=0x40)
        
        print("✅ Robot controller initialized")
        print("🎬 Starting camera movement demo...\n")
        
        # Demo sequence
        movements = [
            {"name": "Pan Left", "pan": 0, "tilt": 90, "duration": 2.0},
            {"name": "Pan Right", "pan": 180, "tilt": 90, "duration": 3.0},
            {"name": "Center", "pan": 90, "tilt": 90, "duration": 2.0},
            {"name": "Look Up", "pan": 90, "tilt": 45, "duration": 1.5},
            {"name": "Look Down", "pan": 90, "tilt": 135, "duration": 1.5},
            {"name": "Center", "pan": 90, "tilt": 90, "duration": 1.0},
            {"name": "Sweep Motion", "sequence": [
                (45, 60, 1.0), (135, 60, 2.0), (135, 120, 1.0), 
                (45, 120, 2.0), (90, 90, 1.5)
            ]},
        ]
        
        for i, movement in enumerate(movements, 1):
            print(f"🎯 Movement {i}: {movement['name']}")
            
            if 'sequence' in movement:
                # Complex sequence
                for pan, tilt, duration in movement['sequence']:
                    print(f"   → Moving to Pan={pan}°, Tilt={tilt}° over {duration}s")
                    robot.servo_controller.smooth_set_camera_position(
                        tilt, pan, duration, "ease_in_out"
                    )
                    time.sleep(0.1)  # Small delay between movements
            else:
                # Single movement
                pan = movement['pan']
                tilt = movement['tilt']
                duration = movement['duration']
                
                print(f"   → Moving to Pan={pan}°, Tilt={tilt}° over {duration}s")
                robot.servo_controller.smooth_set_camera_position(
                    tilt, pan, duration, "ease_in_out"
                )
            
            time.sleep(0.5)  # Pause between movements
            print()
        
        print("🎉 Demo completed!")
        print("📝 Available easing types:")
        print("   • linear - Constant speed")
        print("   • ease_in - Slow start, fast end")
        print("   • ease_out - Fast start, slow end")  
        print("   • ease_in_out - Slow start and end, fast middle")
        
        print("\n🌐 Start the web interface to control manually:")
        print("   ./start.sh")
        print("   Then open: http://192.168.137.243:5000")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'robot' in locals():
            robot.cleanup()

if __name__ == "__main__":
    main()
