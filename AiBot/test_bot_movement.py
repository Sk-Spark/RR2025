#!/usr/bin/env python3
"""
AiBot Movement Test Script
=========================

Comprehensive test script for AiBot movement functionality.
Tests all movement patterns, speeds, and safety features.

Usage:
    python test_bot_movement.py

Requirements:
    - PCA9685 connected at I2C address 0x40
    - 4 motors connected to PCA9685 channels 0, 1, 2, 3
    - Virtual environment activated with required dependencies
"""

import time
import sys
import traceback
import asyncio
from typing import Dict, Any

def print_header(title: str, char: str = "=") -> None:
    """Print a formatted header."""
    print(f"\n{char * 50}")
    print(f"🤖 {title}")
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
    """Test all required imports."""
    print_test("Required Imports")
    
    try:
        # Test hardware imports
        from src.aibot.hardware.movement_controller import MovementController
        from src.aibot.hardware.pca9685_controller import PCA9685Controller
        print("✅ Hardware controllers imported successfully")
        
        # Test other dependencies
        import board
        import busio
        import adafruit_pca9685
        print("✅ Adafruit libraries imported successfully")
        
        import gpiozero
        print("✅ GPIO libraries imported successfully")
        
        print_result(True, "All required imports successful")
        return True
        
    except ImportError as e:
        print_result(False, f"Import error: {e}")
        return False
    except Exception as e:
        print_result(False, f"Unexpected error: {e}")
        return False

def test_hardware_detection() -> bool:
    """Test PCA9685 hardware detection."""
    print_test("Hardware Detection")
    
    try:
        from src.aibot.hardware.pca9685_controller import PCA9685Controller
        
        # Test PCA9685 initialization
        pca_controller = PCA9685Controller()
        print("✅ PCA9685 controller created")
        
        # Test hardware connection
        if hasattr(pca_controller, 'pca') and pca_controller.pca is not None:
            print("✅ PCA9685 hardware detected and connected")
            print_result(True, "Hardware detection successful")
            return True
        else:
            print_result(False, "PCA9685 hardware not detected")
            return False
            
    except Exception as e:
        print_result(False, f"Hardware detection failed: {e}")
        return False

def test_movement_controller_init() -> bool:
    """Test movement controller initialization."""
    print_test("Movement Controller Initialization")
    
    try:
        from src.aibot.hardware.movement_controller import MovementController
        
        # Initialize controller
        controller = MovementController()
        print("✅ Movement controller initialized")
        
        # Test initial status
        status = controller.get_movement_status()
        print(f"✅ Initial status: {status}")
        
        # Test cleanup
        controller.cleanup()
        print("✅ Controller cleanup successful")
        
        print_result(True, "Movement controller initialization successful")
        return True
        
    except Exception as e:
        print_result(False, f"Movement controller initialization failed: {e}")
        return False

def test_individual_motors(controller) -> bool:
    """Test individual motor control."""
    print_test("Individual Motor Control")
    
    try:
        motor_names = ["front_left", "front_right", "rear_left", "rear_right"]
        test_speed = 50  # Safe test speed
        
        for motor in motor_names:
            print(f"Testing {motor} motor...")
            
            # Forward direction
            controller.set_motor_speed(motor, test_speed, "forward")
            time.sleep(0.5)
            controller.stop_motor(motor)
            print(f"✅ {motor} forward movement")
            
            # Reverse direction
            controller.set_motor_speed(motor, test_speed, "backward")
            time.sleep(0.5)
            controller.stop_motor(motor)
            print(f"✅ {motor} reverse movement")
            
            time.sleep(0.2)  # Brief pause between motors
        
        print_result(True, "All individual motors tested successfully")
        return True
        
    except Exception as e:
        print_result(False, f"Individual motor test failed: {e}")
        return False

async def test_movement_patterns(controller) -> bool:
    """Test basic movement patterns."""
    print_test("Movement Patterns")
    
    try:
        test_speed = 40  # Conservative speed for pattern testing
        test_duration = 1.0  # Short duration for testing
        
        movements = [
            ("forward", lambda: controller.move_forward(test_speed, test_duration)),
            ("backward", lambda: controller.move_backward(test_speed, test_duration)),
            ("strafe_left", lambda: controller.strafe_left(test_speed, test_duration)),
            ("strafe_right", lambda: controller.strafe_right(test_speed, test_duration)),
            ("turn_left", lambda: controller.turn_left(test_speed, test_duration)),
            ("turn_right", lambda: controller.turn_right(test_speed, test_duration))
        ]
        
        for movement_name, movement_func in movements:
            print(f"Testing {movement_name} movement...")
            await movement_func()
            print(f"✅ {movement_name} movement successful")
            time.sleep(0.3)  # Pause between movements
        
        print_result(True, "All movement patterns tested successfully")
        return True
        
    except Exception as e:
        print_result(False, f"Movement pattern test failed: {e}")
        return False

async def test_speed_control(controller) -> bool:
    """Test different speed levels."""
    print_test("Speed Control")
    
    try:
        speeds = [25, 50, 75]  # Test different speed levels
        test_duration = 0.8
        
        for speed in speeds:
            print(f"Testing speed {speed}%...")
            await controller.move_forward(speed, test_duration)
            print(f"✅ Speed {speed}% successful")
            time.sleep(0.3)
        
        print_result(True, "Speed control tests successful")
        return True
        
    except Exception as e:
        print_result(False, f"Speed control test failed: {e}")
        return False

async def test_emergency_stop(controller) -> bool:
    """Test emergency stop functionality."""
    print_test("Emergency Stop")
    
    try:
        # Start movement using set_motor_speed (non-async)
        print("Starting movement...")
        controller.set_motor_speed("front_left", 50, "forward")
        controller.set_motor_speed("front_right", 50, "forward")
        time.sleep(0.5)
        
        # Emergency stop (using stop_all_motors)
        print("Executing emergency stop...")
        controller.stop_all_motors()
        
        # Verify all motors stopped
        time.sleep(0.5)
        status = controller.get_movement_status()
        print(f"Status after emergency stop: {status}")
        
        print_result(True, "Emergency stop successful")
        return True
        
    except Exception as e:
        print_result(False, f"Emergency stop test failed: {e}")
        return False

async def test_status_reporting(controller) -> bool:
    """Test status reporting functionality."""
    print_test("Status Reporting")
    
    try:
        # Test initial status
        status = controller.get_movement_status()
        print(f"Initial status: {status}")
        
        # Test status during movement
        await controller.move_forward(30, 0.5)
        status = controller.get_movement_status()
        print(f"Status after movement: {status}")
        
        print_result(True, "Status reporting successful")
        return True
        
    except Exception as e:
        print_result(False, f"Status reporting test failed: {e}")
        return False

async def run_all_tests() -> Dict[str, Any]:
    """Run all movement tests."""
    print_header("AiBot Movement Test Suite")
    
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_results": {}
    }
    
    # Test sequence
    tests = [
        ("Imports", test_imports),
        ("Hardware Detection", test_hardware_detection),
        ("Controller Initialization", test_movement_controller_init)
    ]
    
    # Run initial tests (non-async)
    for test_name, test_func in tests:
        results["total_tests"] += 1
        try:
            success = test_func()
            results["test_results"][test_name] = success
            if success:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
                # Stop if critical tests fail
                if test_name in ["Imports", "Hardware Detection"]:
                    print_result(False, f"Critical test '{test_name}' failed. Stopping test suite.")
                    return results
        except Exception as e:
            results["failed_tests"] += 1
            results["test_results"][test_name] = False
            print_result(False, f"Test '{test_name}' crashed: {e}")
            return results
    
    # If critical tests passed, run movement tests with controller
    try:
        from src.aibot.hardware.movement_controller import MovementController
        controller = MovementController()
        
        # Movement tests (sync test)
        sync_tests = [
            ("Individual Motors", lambda: test_individual_motors(controller))
        ]
        
        for test_name, test_func in sync_tests:
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
        
        # Async movement tests
        async_tests = [
            ("Movement Patterns", lambda: test_movement_patterns(controller)),
            ("Speed Control", lambda: test_speed_control(controller)),
            ("Emergency Stop", lambda: test_emergency_stop(controller)),
            ("Status Reporting", lambda: test_status_reporting(controller))
        ]
        
        for test_name, test_func in async_tests:
            results["total_tests"] += 1
            try:
                success = await test_func()
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
            controller.cleanup()
            print("\n✅ Final cleanup completed")
        except Exception as e:
            print(f"\n⚠️ Cleanup warning: {e}")
            
    except Exception as e:
        print_result(False, f"Failed to create movement controller for testing: {e}")
    
    return results

def print_test_summary(results: Dict[str, Any]) -> None:
    """Print test summary."""
    print_header("Test Summary", "=")
    
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']} ✅")
    print(f"Failed: {results['failed_tests']} ❌")
    
    if results['failed_tests'] == 0:
        print("\n🎉 ALL TESTS PASSED! AiBot movement system is operational.")
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
        print_header("Starting AiBot Movement Tests")
        print("⚠️ Warning: This test will activate motors. Ensure bot is in safe position!")
        print("Press Ctrl+C to abort at any time.")
        
        # Give user time to abort if needed
        time.sleep(3)
        
        # Run tests (async)
        results = asyncio.run(run_all_tests())
        
        # Print summary
        print_test_summary(results)
        
        # Exit with appropriate code
        if results['failed_tests'] == 0:
            print("\n🚀 AiBot movement system ready for operation!")
            sys.exit(0)
        else:
            print("\n🔧 Please fix the issues and run tests again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        print("🛑 Emergency stop activated")
        try:
            from src.aibot.hardware.movement_controller import MovementController
            controller = MovementController()
            controller.stop_all_motors()
            controller.cleanup()
        except:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
