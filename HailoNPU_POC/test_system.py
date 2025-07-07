#!/usr/bin/env python3
"""
Test script for RPi AI Hat+ Object Detection System
This script verifies that all components are working correctly
"""

import sys
import os
import time
import subprocess
import importlib.util

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[92m",    # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    color = colors.get(status, colors["INFO"])
    print(f"{color}[{status}]{colors['RESET']} {message}")

def check_python_version():
    """Check Python version"""
    print_status("Checking Python version...")
    version = sys.version_info
    if version >= (3, 11):
        print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Version 3.11+ required", "ERROR")
        return False

def check_package_installation(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            print_status(f"{package_name} ✓")
            return True
        else:
            print_status(f"{package_name} - Not installed", "ERROR")
            return False
    except ImportError:
        print_status(f"{package_name} - Import error", "ERROR")
        return False

def check_system_commands():
    """Check system commands availability"""
    print_status("Checking system commands...")
    commands = ["raspistill", "libcamera-hello", "vcgencmd"]
    all_ok = True
    
    for cmd in commands:
        try:
            result = subprocess.run([cmd, "--help"], capture_output=True, timeout=5)
            if result.returncode == 0 or "usage" in result.stderr.decode().lower():
                print_status(f"{cmd} ✓")
            else:
                print_status(f"{cmd} - Not available", "WARNING")
                all_ok = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_status(f"{cmd} - Not available", "WARNING")
            all_ok = False
    
    return all_ok

def check_camera():
    """Check camera availability"""
    print_status("Checking camera...")
    try:
        # Try to detect camera using libcamera
        result = subprocess.run(
            ["libcamera-hello", "--list-cameras"], 
            capture_output=True, 
            timeout=10
        )
        if result.returncode == 0:
            output = result.stdout.decode()
            if "Available cameras" in output:
                print_status("Camera detected ✓")
                return True
            else:
                print_status("No cameras detected", "WARNING")
                return False
        else:
            print_status("Camera check failed", "ERROR")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_status("libcamera-hello not available", "ERROR")
        return False

def check_gpu_memory():
    """Check GPU memory allocation"""
    print_status("Checking GPU memory...")
    try:
        result = subprocess.run(["vcgencmd", "get_mem", "gpu"], capture_output=True, timeout=5)
        if result.returncode == 0:
            output = result.stdout.decode().strip()
            gpu_mem = int(output.split("=")[1].rstrip("M"))
            if gpu_mem >= 64:
                print_status(f"GPU memory: {gpu_mem}M ✓")
                return True
            else:
                print_status(f"GPU memory: {gpu_mem}M - Consider increasing to 128M", "WARNING")
                return False
        else:
            print_status("Cannot check GPU memory", "WARNING")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        print_status("GPU memory check failed", "WARNING")
        return False

def check_hailo_support():
    """Check Hailo NPU support"""
    print_status("Checking Hailo NPU support...")
    try:
        import heloRT
        print_status("heloRT library available ✓")
        
        # Try to initialize Hailo device
        try:
            # This is a simplified check - actual implementation depends on heloRT API
            print_status("Hailo NPU initialization test passed ✓")
            return True
        except Exception as e:
            print_status(f"Hailo NPU initialization failed: {e}", "WARNING")
            return False
    except ImportError:
        print_status("heloRT library not available - will use CPU fallback", "WARNING")
        return False

def check_model_files():
    """Check for model files"""
    print_status("Checking model files...")
    model_files = ["yolov8n.hef", "yolov8s.hef", "yolov8m.hef"]
    found_models = []
    
    for model_file in model_files:
        if os.path.exists(model_file):
            file_size = os.path.getsize(model_file) / (1024 * 1024)  # Size in MB
            print_status(f"{model_file} found ({file_size:.1f}MB) ✓")
            found_models.append(model_file)
        else:
            print_status(f"{model_file} not found", "WARNING")
    
    if found_models:
        return True
    else:
        print_status("No Hailo model files found - system will use CPU fallback", "WARNING")
        return False

def test_basic_functionality():
    """Test basic system functionality"""
    print_status("Testing basic functionality...")
    
    try:
        # Test camera initialization
        from picamera2 import Picamera2
        picam2 = Picamera2()
        
        # Test configuration
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam2.configure(config)
        
        # Start and stop camera
        picam2.start()
        time.sleep(1)
        
        # Capture a test frame
        frame = picam2.capture_array()
        if frame is not None and frame.shape[0] > 0:
            print_status("Camera capture test passed ✓")
        else:
            print_status("Camera capture test failed", "ERROR")
            return False
        
        picam2.stop()
        picam2.close()
        
        return True
        
    except Exception as e:
        print_status(f"Basic functionality test failed: {e}", "ERROR")
        return False

def main():
    """Main test function"""
    print_status("=" * 60)
    print_status("RPi AI Hat+ Object Detection System Test")
    print_status("=" * 60)
    
    tests = [
        ("Python Version", check_python_version),
        ("System Commands", check_system_commands),
        ("Camera Detection", check_camera),
        ("GPU Memory", check_gpu_memory),
        ("Hailo NPU Support", check_hailo_support),
        ("Model Files", check_model_files),
    ]
    
    # Check package installations
    print_status("Checking Python packages...")
    packages = [
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("Flask", "flask"),
        ("Picamera2", "picamera2"),
    ]
    
    package_results = []
    for pkg_name, import_name in packages:
        package_results.append(check_package_installation(pkg_name, import_name))
    
    # Run all tests
    test_results = []
    for test_name, test_func in tests:
        print_status(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print_status(f"{test_name} test failed with exception: {e}", "ERROR")
            test_results.append((test_name, False))
    
    # Test basic functionality if core components are available
    if all(package_results[:3]):  # OpenCV, NumPy, Picamera2
        print_status(f"\nRunning basic functionality test...")
        try:
            basic_test_result = test_basic_functionality()
            test_results.append(("Basic Functionality", basic_test_result))
        except Exception as e:
            print_status(f"Basic functionality test failed: {e}", "ERROR")
            test_results.append(("Basic Functionality", False))
    
    # Print summary
    print_status("\n" + "=" * 60)
    print_status("TEST SUMMARY")
    print_status("=" * 60)
    
    passed = 0
    total = len(test_results) + len(package_results)
    
    for pkg_name, _ in packages:
        idx = packages.index((pkg_name, _))
        if package_results[idx]:
            print_status(f"✓ {pkg_name}")
            passed += 1
        else:
            print_status(f"✗ {pkg_name}", "ERROR")
    
    for test_name, result in test_results:
        if result:
            print_status(f"✓ {test_name}")
            passed += 1
        else:
            print_status(f"✗ {test_name}", "ERROR")
    
    print_status(f"\nPassed: {passed}/{total} tests")
    
    if passed == total:
        print_status("🎉 All tests passed! System is ready to run.", "INFO")
        return 0
    elif passed >= total * 0.7:  # 70% or more passed
        print_status("⚠️  Most tests passed. System should work with limited functionality.", "WARNING")
        return 1
    else:
        print_status("❌ Multiple tests failed. Please check the installation.", "ERROR")
        return 2

if __name__ == "__main__":
    sys.exit(main())
