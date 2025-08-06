#!/usr/bin/env python3
"""
Direct hardware test for motor movement
"""

import sys
import time
sys.path.append('/home/spark/RR2025/AiBot')

def test_hardware():
    try:
        print("🔧 Direct hardware test starting...")
        
        from pca9685_controller import PCA9685Controller
        
        # Initialize PCA9685
        pca = PCA9685Controller()
        print("✅ PCA9685 initialized")
        
        # Test motor configuration from movement controller
        motors = {
            "front_right": {"channel": 15, "in1": 14, "in2": 13},
            "front_left": {"channel": 4, "in1": 5, "in2": 6},
            "rear_right": {"channel": 10, "in1": 12, "in2": 11},
            "rear_left": {"channel": 9, "in1": 7, "in2": 8},
        }
        
        print(f"🚗 Testing {len(motors)} motors...")
        
        # Test each motor individually
        for motor_name, motor_config in motors.items():
            print(f"\n🔄 Testing {motor_name} motor...")
            
            # Set speed to 50% on channel, forward direction
            pca.set_pwm(motor_config["channel"], int(65535 * 0.5))  # 50% speed
            pca.set_pwm(motor_config["in1"], 65535)  # High for forward
            pca.set_pwm(motor_config["in2"], 0)      # Low for forward
            
            print(f"   ✅ {motor_name}: Channel {motor_config['channel']} at 50%, IN1={motor_config['in1']} HIGH, IN2={motor_config['in2']} LOW")
            
            # Run for 2 seconds
            time.sleep(2)
            
            # Stop motor
            pca.set_pwm(motor_config["channel"], 0)
            pca.set_pwm(motor_config["in1"], 0)
            pca.set_pwm(motor_config["in2"], 0)
            
            print(f"   🛑 {motor_name} stopped")
            time.sleep(1)
        
        print("\n🎯 Testing all motors together (forward)...")
        
        # Test all motors forward
        for motor_name, motor_config in motors.items():
            pca.set_pwm(motor_config["channel"], int(65535 * 0.3))  # 30% speed
            pca.set_pwm(motor_config["in1"], 65535)  # High for forward
            pca.set_pwm(motor_config["in2"], 0)      # Low for forward
        
        print("✅ All motors running forward at 30% for 3 seconds...")
        time.sleep(3)
        
        # Stop all motors
        for motor_name, motor_config in motors.items():
            pca.set_pwm(motor_config["channel"], 0)
            pca.set_pwm(motor_config["in1"], 0)
            pca.set_pwm(motor_config["in2"], 0)
        
        print("🛑 All motors stopped")
        print("✅ Hardware test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Hardware test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_hardware()
    print(f"\n🏁 Test result: {'PASS' if result else 'FAIL'}")
