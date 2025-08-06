#!/usr/bin/env python3
"""
Hardware diagnostic script
Tests different levels of the motor control system
"""

import sys
import time
sys.path.append('/home/spark/RR2025/AiBot')

def hardware_diagnostic():
    try:
        print("🔧 HARDWARE DIAGNOSTIC STARTING...")
        print("=" * 50)
        
        from pca9685_controller import PCA9685Controller
        
        # Initialize PCA9685
        pca = PCA9685Controller(i2c_address=0x40, frequency=50)
        print("✅ PCA9685 initialized successfully")
        
        # Test each motor individually with increasing intensity
        motors = {
            "front_right": {"channel": 15, "in1": 14, "in2": 13},
            "front_left": {"channel": 4, "in1": 5, "in2": 6},
            "rear_right": {"channel": 10, "in1": 12, "in2": 11},
            "rear_left": {"channel": 9, "in1": 7, "in2": 8},
        }
        
        print(f"\n🚗 INDIVIDUAL MOTOR TESTS")
        print("Watch/listen for ANY motor movement or sound...")
        
        for motor_name, motor_config in motors.items():
            print(f"\n🔧 Testing {motor_name}:")
            print(f"   Channels: PWM={motor_config['channel']}, IN1={motor_config['in1']}, IN2={motor_config['in2']}")
            
            # Test at different speeds
            for speed in [10, 30, 50, 80, 100]:
                print(f"   💨 Speed {speed}% forward... ", end="", flush=True)
                
                # Set motor at this speed
                duty_cycle = int((speed / 100) * 65535)
                pca.set_pwm(motor_config["channel"], duty_cycle)
                pca.set_pwm(motor_config["in1"], 65535)  # Forward
                pca.set_pwm(motor_config["in2"], 0)
                
                time.sleep(1)  # Run for 1 second
                
                # Stop motor
                pca.set_pwm(motor_config["channel"], 0)
                pca.set_pwm(motor_config["in1"], 0)
                pca.set_pwm(motor_config["in2"], 0)
                
                print("stopped")
                time.sleep(0.5)
            
            # Test backward
            print(f"   ⬅️ Speed 50% backward... ", end="", flush=True)
            duty_cycle = int(0.5 * 65535)
            pca.set_pwm(motor_config["channel"], duty_cycle)
            pca.set_pwm(motor_config["in1"], 0)      # Backward
            pca.set_pwm(motor_config["in2"], 65535)
            
            time.sleep(2)
            
            # Stop motor
            pca.set_pwm(motor_config["channel"], 0)
            pca.set_pwm(motor_config["in1"], 0)
            pca.set_pwm(motor_config["in2"], 0)
            print("stopped")
            
            input(f"   Did you see/hear ANY movement from {motor_name}? Press Enter to continue...")
        
        print(f"\n🎯 FULL ROBOT TESTS")
        print("All motors together...")
        
        # Test all motors at maximum safe speed
        print("🚀 ALL MOTORS 100% FORWARD for 3 seconds...")
        for motor_name, motor_config in motors.items():
            pca.set_pwm(motor_config["channel"], 65535)  # 100% speed
            pca.set_pwm(motor_config["in1"], 65535)      # Forward
            pca.set_pwm(motor_config["in2"], 0)
        
        time.sleep(3)
        
        # Stop all
        for motor_name, motor_config in motors.items():
            pca.set_pwm(motor_config["channel"], 0)
            pca.set_pwm(motor_config["in1"], 0)
            pca.set_pwm(motor_config["in2"], 0)
        
        print("🛑 All motors stopped")
        
        print("\n" + "=" * 50)
        print("🔍 DIAGNOSTIC QUESTIONS:")
        print("1. Did you see ANY motor movement during individual tests?")
        print("2. Did you hear ANY motor sounds (humming, clicking)?")
        print("3. Are there any LEDs on your motor driver board?")
        print("4. Is the motor driver board getting external power (6-12V)?")
        print("5. Are motor wires securely connected?")
        print("\nIf no movement was observed, the issue is likely:")
        print("- Power supply to motor driver board")
        print("- Loose connections")
        print("- Faulty motor driver board")
        print("- Motors not connected or damaged")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = hardware_diagnostic()
    print(f"\n🏁 Diagnostic complete: {'PASS' if result else 'FAIL'}")
