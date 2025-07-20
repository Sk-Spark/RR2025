#!/usr/bin/env python3
"""
AI Bot Controller Test Script
Tests individual components and system integration
"""

import sys
import time
import importlib
from datetime import datetime

def print_test_header(test_name):
    print(f"\n{'='*50}")
    print(f"Testing: {test_name}")
    print(f"{'='*50}")

def test_imports():
    """Test if all required packages can be imported"""
    print_test_header("Package Imports")
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_socketio', 'Flask-SocketIO'),
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('threading', 'Threading'),
        ('json', 'JSON'),
        ('logging', 'Logging'),
    ]
    
    optional_packages = [
        ('picamera2', 'PiCamera2'),
        ('adafruit_pca9685', 'Adafruit PCA9685'),
        ('smbus2', 'SMBus2'),
    ]
    
    print("Required packages:")
    for package, name in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name} - {e}")
            return False
    
    print("\nOptional packages:")
    for package, name in optional_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"⚠ {name} - {e}")
    
    return True

def test_hailo_npu():
    """Test Hailo NPU availability"""
    print_test_header("Hailo NPU")
    
    try:
        from picamera2.devices import Hailo
        print("✓ Hailo NPU drivers available")
        return True
    except ImportError as e:
        print(f"⚠ Hailo NPU not available: {e}")
        return False

def test_camera():
    """Test camera functionality"""
    print_test_header("Camera System")
    
    try:
        from picamera2 import Picamera2
        camera = Picamera2()
        print("✓ Camera initialization successful")
        
        # Test camera configuration
        config = camera.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        camera.configure(config)
        print("✓ Camera configuration successful")
        
        camera.start()
        print("✓ Camera start successful")
        
        # Capture a test frame
        frame = camera.capture_array()
        print(f"✓ Frame capture successful - Shape: {frame.shape}")
        
        camera.stop()
        print("✓ Camera stop successful")
        return True
        
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_i2c():
    """Test I2C bus functionality"""
    print_test_header("I2C Communication")
    
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ I2C bus accessible")
            print("I2C scan results:")
            print(result.stdout)
            
            # Check for common devices
            output = result.stdout
            if '40' in output:
                print("✓ PCA9685 detected at 0x40")
            else:
                print("⚠ PCA9685 not detected at 0x40")
                
            if '68' in output:
                print("✓ MPU6050 detected at 0x68")
            else:
                print("⚠ MPU6050 not detected at 0x68")
                
            return True
        else:
            print(f"✗ I2C scan failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("✗ i2cdetect command not found - install i2c-tools")
        return False
    except Exception as e:
        print(f"✗ I2C test failed: {e}")
        return False

def test_gpio():
    """Test GPIO functionality"""
    print_test_header("GPIO System")
    
    try:
        import RPi.GPIO as GPIO
        print("✓ RPi.GPIO available")
        
        # Test GPIO mode setting
        GPIO.setmode(GPIO.BCM)
        print("✓ GPIO mode set to BCM")
        
        GPIO.cleanup()
        print("✓ GPIO cleanup successful")
        return True
        
    except Exception as e:
        print(f"✗ GPIO test failed: {e}")
        return False

def test_web_server():
    """Test Flask web server"""
    print_test_header("Web Server")
    
    try:
        from flask import Flask
        from flask_socketio import SocketIO
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test_key'
        socketio = SocketIO(app)
        
        @app.route('/')
        def test_route():
            return "Test successful"
        
        print("✓ Flask application created")
        print("✓ SocketIO initialized")
        print("✓ Test route configured")
        
        # Note: We don't actually start the server in test mode
        return True
        
    except Exception as e:
        print(f"✗ Web server test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print_test_header("File Structure")
    
    import os
    
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'README.md',
        'templates/index.html'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} missing")
            return False
    
    return True

def run_all_tests():
    """Run all tests and provide summary"""
    print("AI Bot Controller - System Test")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Package Imports", test_imports),
        ("GPIO System", test_gpio),
        ("I2C Communication", test_i2c),
        ("Camera System", test_camera),
        ("Hailo NPU", test_hailo_npu),
        ("Web Server", test_web_server),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} - Unexpected error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_test_header("Test Summary")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
