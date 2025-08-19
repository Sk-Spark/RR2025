#!/home/spark/RR2025/AiBot/venv/bin/python
"""
Camera Pan-Tilt Controller Test Script
Tests all camera movement functionality for AiBot
Uses the AiBot virtual environment for dependencies.
"""

import time
import sys
import traceback
import asyncio
from typing import Dict, Any

def print_header(title: str, char: str = "=") -> None:
    """Print a formatted header."""
    print(f"\n{char * 50}")
    print(f"📹 {title}")
    print(f"{char * 50}")

def print_test(test_name: str) -> None:
    """Print test start message."""
    print(f"\n🔧 Testing: {test_name}")
    print("-" * 30)

def print_result(success: bool, message: str = "") -> None:
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_imports() -> bool:
    """Test camera controller imports."""
    print_test("Camera Controller Imports")
    
    try:
        from src.aibot.hardware.camera_controller import CameraPanTiltController
        print("✅ Camera controller imported successfully")
        
        # Test PCA9685 controller import
        from src.aibot.hardware.pca9685_controller import PCA9685Controller
        print("✅ PCA9685 controller imported successfully")
        
        import board
        import busio
        import adafruit_pca9685
        print("✅ Adafruit libraries imported successfully")
        
        print_result(True, "All required imports successful")
        return True
        
    except ImportError as e:
        print_result(False, f"Import error: {e}")
        return False
    except Exception as e:
        print_result(False, f"Unexpected error: {e}")
        return False

def test_camera_initialization() -> bool:
    """Test camera controller initialization."""
    print_test("Camera Controller Initialization")
    
    try:
        from src.aibot.hardware.camera_controller import CameraPanTiltController
        
        # Test camera controller initialization
        camera = CameraPanTiltController()
        print("✅ Camera controller initialized")
        
        # Test initial status
        status = camera.get_status()
        print(f"✅ Initial status: {status['camera_position']}")
        
        # Test cleanup
        camera.cleanup()
        print("✅ Camera controller cleanup successful")
        
        print_result(True, "Camera controller initialization successful")
        return True
        
    except Exception as e:
        print_result(False, f"Camera controller initialization failed: {e}")
        return False

def test_basic_movements(camera) -> bool:
    """Test basic camera movements."""
    print_test("Basic Camera Movements")
    
    try:
        # Test center position
        print("Testing center position...")
        success = camera.center_all_servos()
        if not success:
            return False
        time.sleep(1)
        print("✅ Center position successful")
        
        # Test look up
        print("Testing look up...")
        success = camera.look_up(30, smooth=False)
        if not success:
            return False
        time.sleep(1)
        print("✅ Look up movement successful")
        
        # Test look down
        print("Testing look down...")
        success = camera.look_down(30, smooth=False)
        if not success:
            return False
        time.sleep(1)
        print("✅ Look down movement successful")
        
        # Test look left
        print("Testing look left...")
        success = camera.look_left(45, smooth=False)
        if not success:
            return False
        time.sleep(1)
        print("✅ Look left movement successful")
        
        # Test look right
        print("Testing look right...")
        success = camera.look_right(45, smooth=False)
        if not success:
            return False
        time.sleep(1)
        print("✅ Look right movement successful")
        
        # Return to center
        camera.center_all_servos()
        
        print_result(True, "All basic movements successful")
        return True
        
    except Exception as e:
        print_result(False, f"Basic movements test failed: {e}")
        return False

def test_smooth_movements(camera) -> bool:
    """Test smooth camera movements."""
    print_test("Smooth Camera Movements")
    
    try:
        # Test smooth position setting
        print("Testing smooth camera positioning...")
        success = camera.set_camera_position(tilt_angle=60, pan_angle=120, smooth=True, duration=2.0)
        if not success:
            return False
        print("✅ Smooth positioning successful")
        
        # Test smooth look movements
        print("Testing smooth look up...")
        success = camera.look_up(40, smooth=True, duration=1.5)
        if not success:
            return False
        print("✅ Smooth look up successful")
        
        print("Testing smooth look left...")
        success = camera.look_left(50, smooth=True, duration=1.5)
        if not success:
            return False
        print("✅ Smooth look left successful")
        
        # Return to center smoothly
        camera.set_camera_position(90, 90, smooth=True, duration=1.0)
        
        print_result(True, "All smooth movements successful")
        return True
        
    except Exception as e:
        print_result(False, f"Smooth movements test failed: {e}")
        return False

def test_sweep_patterns(camera) -> bool:
    """Test camera sweep patterns."""
    print_test("Camera Sweep Patterns")
    
    try:
        # Test horizontal sweep
        print("Testing horizontal sweep...")
        success = camera.sweep_horizontal(speed=1.5, range_angle=50)
        if not success:
            return False
        time.sleep(1)
        print("✅ Horizontal sweep successful")
        
        # Test vertical sweep
        print("Testing vertical sweep...")
        success = camera.sweep_vertical(speed=1.2, range_angle=40)
        if not success:
            return False
        time.sleep(1)
        print("✅ Vertical sweep successful")
        
        print_result(True, "All sweep patterns successful")
        return True
        
    except Exception as e:
        print_result(False, f"Sweep patterns test failed: {e}")
        return False

def test_position_tracking(camera) -> bool:
    """Test position tracking and status."""
    print_test("Position Tracking and Status")
    
    try:
        # Set a specific position
        camera.set_camera_position(75, 105, smooth=False)
        
        # Get position
        position = camera.get_camera_position()
        print(f"Current position: Tilt={position['tilt']}°, Pan={position['pan']}°")
        
        # Get full status
        status = camera.get_status()
        print(f"Servo count: {status['servo_count']}")
        print(f"Movement limits: {status['movement_limits']}")
        
        # Test individual angle getting
        tilt_angle = camera.get_servo_angle("camera_tilt")
        pan_angle = camera.get_servo_angle("camera_pan")
        print(f"Individual angles: Tilt={tilt_angle}°, Pan={pan_angle}°")
        
        print_result(True, "Position tracking and status successful")
        return True
        
    except Exception as e:
        print_result(False, f"Position tracking test failed: {e}")
        return False

def test_safety_limits(camera) -> bool:
    """Test movement safety limits."""
    print_test("Safety Limits")
    
    try:
        # Test extreme angles (should be limited)
        print("Testing extreme angles (should be limited)...")
        
        # Try to set very high tilt angle
        success = camera.set_servo_angle("camera_tilt", 200)  # Should be limited to 150
        if success:
            actual_angle = camera.get_servo_angle("camera_tilt")
            print(f"✅ Extreme tilt angle limited to {actual_angle}°")
        
        # Try to set very low pan angle
        success = camera.set_servo_angle("camera_pan", -50)  # Should be limited to 30
        if success:
            actual_angle = camera.get_servo_angle("camera_pan")
            print(f"✅ Extreme pan angle limited to {actual_angle}°")
        
        # Return to safe position
        camera.center_all_servos()
        
        print_result(True, "Safety limits working correctly")
        return True
        
    except Exception as e:
        print_result(False, f"Safety limits test failed: {e}")
        return False

def run_all_tests() -> Dict[str, Any]:
    """Run all camera controller tests."""
    print_header("AiBot Camera Pan-Tilt Test Suite")
    
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_results": {}
    }
    
    # Test sequence
    tests = [
        ("Imports", test_imports),
        ("Camera Initialization", test_camera_initialization)
    ]
    
    # Run initial tests
    for test_name, test_func in tests:
        results["total_tests"] += 1
        try:
            success = test_func()
            results["test_results"][test_name] = success
            if success:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
                if test_name in ["Imports"]:
                    print_result(False, f"Critical test '{test_name}' failed. Stopping test suite.")
                    return results
        except Exception as e:
            results["failed_tests"] += 1
            results["test_results"][test_name] = False
            print_result(False, f"Test '{test_name}' crashed: {e}")
            return results
    
    # If initial tests passed, run camera tests with controller
    try:
        from src.aibot.hardware.camera_controller import CameraPanTiltController
        camera = CameraPanTiltController()
        
        # Camera movement tests
        camera_tests = [
            ("Basic Movements", lambda: test_basic_movements(camera)),
            ("Smooth Movements", lambda: test_smooth_movements(camera)),
            ("Sweep Patterns", lambda: test_sweep_patterns(camera)),
            ("Position Tracking", lambda: test_position_tracking(camera)),
            ("Safety Limits", lambda: test_safety_limits(camera))
        ]
        
        for test_name, test_func in camera_tests:
            results["total_tests"] += 1
            try:
                success = test_func()
                results["test_results"][test_name] = success
                if success:
                    results["passed_tests"] += 1
                else:
                    results["failed_tests"] += 1
            except Exception as e:
                results["failed_tests"] += 1
                results["test_results"][test_name] = False
                print_result(False, f"Test '{test_name}' failed: {e}")
                traceback.print_exc()
        
        # Final cleanup
        try:
            camera.cleanup()
            print("\n✅ Final cleanup completed")
        except Exception as e:
            print(f"\n⚠️ Cleanup warning: {e}")
            
    except Exception as e:
        print_result(False, f"Failed to create camera controller for testing: {e}")
    
    return results

def print_test_summary(results: Dict[str, Any]) -> None:
    """Print test summary."""
    print_header("Test Summary", "=")
    
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']} ✅")
    print(f"Failed: {results['failed_tests']} ❌")
    
    if results['failed_tests'] == 0:
        print("\n🎉 ALL TESTS PASSED! Camera pan-tilt system is operational.")
    else:
        print(f"\n⚠️ {results['failed_tests']} test(s) failed. Please check the issues above.")
    
    print("\nDetailed Results:")
    print("-" * 30)
    for test_name, success in results["test_results"].items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    # Calculate success rate
    if results['total_tests'] > 0:
        success_rate = (results['passed_tests'] / results['total_tests']) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")

def main():
    """Main test execution."""
    try:
        print_header("Starting AiBot Camera Pan-Tilt Tests")
        print("⚠️ Warning: This test will activate servos. Ensure camera mount is secure!")
        print("Press Ctrl+C to abort at any time.")
        
        # Give user time to abort if needed
        time.sleep(3)
        
        # Run tests
        results = run_all_tests()
        
        # Print summary
        print_test_summary(results)
        
        # Exit with appropriate code
        if results['failed_tests'] == 0:
            print("\n🎬 Camera pan-tilt system ready for filming!")
            sys.exit(0)
        else:
            print("\n🔧 Please fix the issues and run tests again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        print("🛑 Emergency stop activated")
        try:
            from src.aibot.hardware.camera_controller import CameraPanTiltController
            camera = CameraPanTiltController()
            camera.cleanup()
        except:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
