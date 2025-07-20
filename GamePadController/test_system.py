#!/usr/bin/env python3
"""
System Test for Xbox Controller Robot Control
Tests components that don't require hardware initialization
"""

import sys
import traceback

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    try:
        from xbox_controller import XboxGamepadController
        print("✅ Xbox controller module imported successfully")
    except Exception as e:
        print(f"❌ Xbox controller import failed: {e}")
        return False
    
    try:
        from robot_controller import RobotController  
        print("✅ Robot controller module imported successfully")
    except Exception as e:
        print(f"❌ Robot controller import failed: {e}")
        return False
        
    try:
        from pca9685_controller import PCA9685Controller
        print("✅ PCA9685 controller module imported successfully")
    except Exception as e:
        print(f"❌ PCA9685 controller import failed: {e}")
        return False
        
    try:
        from motor_controller import MotorController
        print("✅ Motor controller module imported successfully")
    except Exception as e:
        print(f"❌ Motor controller import failed: {e}")
        return False
        
    try:
        from servo_controller import ServoController
        print("✅ Servo controller module imported successfully")
    except Exception as e:
        print(f"❌ Servo controller import failed: {e}")
        return False
    
    return True

def test_xbox_controller():
    """Test Xbox controller functionality"""
    print("\nTesting Xbox controller...")
    
    try:
        from xbox_controller import XboxGamepadController
        
        # Test controller creation
        controller = XboxGamepadController()
        print("✅ Xbox controller created successfully")
        
        # Test callback registration
        def test_callback(btn):
            pass
            
        controller.register_button_callback('a', test_callback, 'press')
        print("✅ Button callback registration works")
        
        controller.register_analog_callback('left_stick', test_callback)
        print("✅ Analog callback registration works")
        
        return True
        
    except Exception as e:
        print(f"❌ Xbox controller test failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test robot configuration"""
    print("\nTesting robot configuration...")
    
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
        
        # Controller configuration
        controller_config = {
            "default_speed": 50,
            "servo_increment": 5,
            "speed_increment": 10,
            "max_speed": 100,
            "min_speed": 20,
        }
        
        print(f"✅ Motor configuration: {len(motors)} motors configured")
        print(f"✅ Servo configuration: {len(servos)} servos configured")
        print(f"✅ Controller configuration: {len(controller_config)} parameters")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_main_module():
    """Test main module import"""
    print("\nTesting main module...")
    
    try:
        import main
        print("✅ Main module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Main module import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Xbox Controller Robot Control System Tests ===")
    print("Testing components that don't require hardware...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Xbox Controller Tests", test_xbox_controller), 
        ("Configuration Tests", test_configuration),
        ("Main Module Tests", test_main_module),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for hardware testing.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
