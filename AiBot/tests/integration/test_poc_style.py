#!/usr/bin/env python3
"""
Test using the exact same approach as the working POC
"""

import sys
import time
sys.path.append('/home/spark/RR2025/AiBot')

def test_poc_approach():
    try:
        print("🔧 Testing with POC approach...")
        
        # Import our controller
        from pca9685_controller import PCA9685Controller
        
        # Initialize exactly like the POC - with 50Hz frequency
        pca = PCA9685Controller(i2c_address=0x40, frequency=50)
        print("✅ PCA9685 initialized at 50Hz")
        
        # Motor configuration (same as POC)
        motors = {
            "front_right": {"channel": 15, "in1": 14, "in2": 13},
            "front_left": {"channel": 4, "in1": 5, "in2": 6},
            "rear_right": {"channel": 10, "in1": 12, "in2": 11},
            "rear_left": {"channel": 9, "in1": 7, "in2": 8},
        }
        
        def set_motor_speed_poc_style(motor_name, speed, direction="forward"):
            """Set motor exactly like the POC does"""
            motor = motors[motor_name]
            
            # Convert speed percentage to PWM duty cycle (0-65535)
            speed = max(0, min(100, speed))  # Clamp between 0-100
            duty_cycle = int((speed / 100) * 65535)
            
            # Set PWM for motor enable/speed
            pca.set_pwm(motor["channel"], duty_cycle)
            
            # Set direction pins
            if direction == "forward":
                pca.set_pwm(motor["in1"], 65535)  # High
                pca.set_pwm(motor["in2"], 0)      # Low
            elif direction == "backward":
                pca.set_pwm(motor["in1"], 0)      # Low
                pca.set_pwm(motor["in2"], 65535)  # High
            
            print(f"Motor {motor_name}: Speed={speed}%, Direction={direction}")
        
        def stop_motor_poc_style(motor_name):
            """Stop motor exactly like POC does"""
            motor = motors[motor_name]
            pca.set_pwm(motor["channel"], 0)
            pca.set_pwm(motor["in1"], 0)
            pca.set_pwm(motor["in2"], 0)
            print(f"Motor {motor_name} stopped")
        
        print("\n🚗 Testing forward movement (POC style)...")
        
        # Test forward movement exactly like POC
        for motor_name in motors:
            set_motor_speed_poc_style(motor_name, 30, "forward")
        
        print("✅ All motors running forward at 30% for 3 seconds...")
        time.sleep(3)
        
        # Stop all motors
        for motor_name in motors:
            stop_motor_poc_style(motor_name)
        
        print("🛑 All motors stopped")
        
        print("\n🔄 Testing turn left (POC style)...")
        
        # Test turn left exactly like POC
        set_motor_speed_poc_style("rear_right", 30, "forward")
        set_motor_speed_poc_style("front_right", 30, "forward") 
        set_motor_speed_poc_style("rear_left", 30, "backward")
        set_motor_speed_poc_style("front_left", 30, "backward")
        
        print("✅ Turning left at 30% for 2 seconds...")
        time.sleep(2)
        
        # Stop all motors
        for motor_name in motors:
            stop_motor_poc_style(motor_name)
        
        print("🛑 All motors stopped")
        print("✅ POC-style test completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ POC-style test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_poc_approach()
    print(f"\n🏁 Test result: {'PASS' if result else 'FAIL'}")
