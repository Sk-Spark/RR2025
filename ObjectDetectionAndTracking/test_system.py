#!/usr/bin/env python3
"""
Test Script for Ping Pong Ball Tracking System
Tests individual components to verify proper installation and functionality
"""

import sys
import os
import time
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Motors_Servo_POC'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
    except ImportError:
        print("✗ OpenCV not available")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
    except ImportError:
        print("✗ NumPy not available")
        return False
    
    try:
        from flask import Flask
        print("✓ Flask available")
    except ImportError:
        print("✗ Flask not available")
        return False
    
    try:
        from picamera2 import Picamera2
        print("✓ picamera2 available")
    except ImportError:
        print("⚠ picamera2 not available (will use OpenCV fallback)")
    
    try:
        import board
        import busio
        from adafruit_pca9685 import PCA9685
        print("✓ PCA9685 libraries available")
    except ImportError:
        print("✗ PCA9685 libraries not available")
        return False
    
    return True


def test_camera():
    """Test camera functionality"""
    print("\nTesting camera...")
    
    try:
        import cv2
        
        # First try to detect available cameras
        available_cameras = []
        for i in range(3):  # Check first 3 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    available_cameras.append(i)
                cap.release()
        
        if not available_cameras:
            print("⚠ No cameras detected via OpenCV")
            print("  This is expected if no USB/CSI camera is connected")
            print("  For RPi Camera, ensure it's enabled: sudo raspi-config")
            return False
        
        # Test with camera manager if cameras are available
        from camera_manager import CameraManager
        camera = CameraManager()
        frame = camera.capture_frame()
        
        if frame is not None:
            height, width = frame.shape[:2]
            print(f"✓ Camera working: {width}x{height}")
            print(f"✓ Available cameras: {available_cameras}")
            camera.cleanup()
            return True
        else:
            print("✗ Camera detected but not producing frames")
            camera.cleanup()
            return False
            
    except Exception as e:
        print(f"⚠ Camera test failed: {e}")
        print("  This is expected if no camera hardware is connected")
        return False


def test_i2c():
    """Test I2C connectivity"""
    print("\nTesting I2C...")
    
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ I2C interface working")
            
            # Check for PCA9685 at address 0x40
            if '40' in result.stdout:
                print("✓ PCA9685 detected at address 0x40")
                return True
            else:
                print("⚠ PCA9685 not detected at address 0x40")
                print("  Make sure PCA9685 is connected and powered")
                return False
        else:
            print("✗ I2C interface not working")
            return False
            
    except FileNotFoundError:
        print("⚠ i2cdetect not found (install i2c-tools)")
        return False
    except Exception as e:
        print(f"✗ I2C test failed: {e}")
        return False


def test_servos():
    """Test servo controller"""
    print("\nTesting servo controller...")
    
    try:
        from servo_controller import BallTrackingServoController
        
        servo_controller = BallTrackingServoController()
        print("✓ Servo controller initialized")
        
        # Test center position
        servo_controller.center_camera()
        print("✓ Camera centered")
        time.sleep(1)
        
        # Test small movements
        servo_controller.servo_controller.set_servo_angle('pan', 100)
        time.sleep(0.5)
        servo_controller.servo_controller.set_servo_angle('pan', 80)
        time.sleep(0.5)
        servo_controller.center_camera()
        
        print("✓ Servo movement test completed")
        servo_controller.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Servo test failed: {e}")
        return False


def test_ball_detection():
    """Test ball detection"""
    print("\nTesting ball detection...")
    
    try:
        from ball_detector import ColorBasedBallDetector
        import cv2
        import numpy as np
        
        detector = ColorBasedBallDetector()
        print("✓ Ball detector initialized")
        
        # Create a test frame with an orange circle
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(test_frame, (320, 240), 30, (0, 165, 255), -1)  # Orange circle
        
        detection = detector.detect(test_frame)
        
        if detection:
            x, y, radius = detection
            print(f"✓ Ball detection working: center=({x},{y}), radius={radius}")
            return True
        else:
            print("⚠ Ball detection not finding test circle")
            print("  This might be due to HSV color range settings")
            return False
            
    except Exception as e:
        print(f"✗ Ball detection test failed: {e}")
        return False


def test_hailo():
    """Test Hailo NPU availability"""
    print("\nTesting Hailo NPU...")
    
    try:
        # Add HailoNPU_POC to path
        hailo_path = os.path.join(os.path.dirname(__file__), '..', 'HailoNPU_POC')
        if hailo_path not in sys.path:
            sys.path.append(hailo_path)
        
        # Import from the HailoNPU_POC main module
        import importlib.util
        spec = importlib.util.spec_from_file_location("hailo_main", os.path.join(hailo_path, "main.py"))
        hailo_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hailo_main)
        
        detector = hailo_main.HailoObjectDetector()
        print("✓ Hailo detector available")
        return True
        
    except Exception as e:
        print(f"⚠ Hailo NPU not available: {e}")
        print("  Color-based detection will be used as fallback")
        return False


def test_web_interface():
    """Test web interface"""
    print("\nTesting web interface...")
    
    try:
        from web_interface import WebServer
        from ball_tracker import BallTracker
        from ball_detector import ColorBasedBallDetector
        
        # Create minimal components for testing (without camera/servo if they fail)
        try:
            from camera_manager import CameraManager
            camera = CameraManager()
        except:
            print("⚠ Camera not available for web test")
            camera = None
        
        try:
            from servo_controller import BallTrackingServoController
            servo = BallTrackingServoController()
        except:
            print("⚠ Servo controller not available for web test") 
            servo = None
        
        detector = ColorBasedBallDetector()
        
        # Only test web server if we have the basic components
        if camera is None or servo is None:
            print("⚠ Web interface test skipped (missing hardware)")
            return False
        
        tracker = BallTracker(camera, servo, detector)
        web_server = WebServer(tracker)
        print("✓ Web server initialized")
        
        # Cleanup
        tracker.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Web interface test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("PING PONG BALL TRACKING SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Camera", test_camera),
        ("I2C", test_i2c),
        ("Servos", test_servos),
        ("Ball Detection", test_ball_detection),
        ("Hailo NPU", test_hailo),
        ("Web Interface", test_web_interface)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 20}")
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            break
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
    elif passed >= total - 1:
        print("\n⚠ Most tests passed. System should work with minor issues.")
    else:
        print("\n❌ Multiple tests failed. Check hardware and installation.")
    
    print("\nNext steps:")
    print("1. Fix any failed tests")
    print("2. Run: ./start_tracking.sh")
    print("3. Open: http://localhost:5000")


if __name__ == "__main__":
    main()
