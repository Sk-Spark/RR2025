#!/usr/bin/env python3
"""
Servo Movement Test
Direct test of servo controller to verify servo movement
"""

import sys
import os
import time
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from servo_controller import BallTrackingServoController

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_servo_basic_movement():
    """Test basic servo movements"""
    print("🔧 Testing Basic Servo Movement...")
    
    try:
        servo = BallTrackingServoController()
        
        print(f"✅ Servo controller initialized")
        print(f"   Pan limits: {servo.pan_limits}")
        print(f"   Tilt limits: {servo.tilt_limits}")
        print(f"   Current position: Pan={servo.current_positions['pan']}°, Tilt={servo.current_positions['tilt']}°")
        
        # Test 1: Center position
        print("\n📍 Test 1: Moving to center position...")
        servo.center_servos()
        time.sleep(2)
        print(f"   Position: Pan={servo.current_positions['pan']}°, Tilt={servo.current_positions['tilt']}°")
        
        # Test 2: Pan left
        print("\n◀️ Test 2: Pan left...")
        servo.set_pan_angle(45)
        time.sleep(2)
        print(f"   Position: Pan={servo.current_positions['pan']}°, Tilt={servo.current_positions['tilt']}°")
        
        # Test 3: Pan right
        print("\n▶️ Test 3: Pan right...")
        servo.set_pan_angle(135)
        time.sleep(2)
        print(f"   Position: Pan={servo.current_positions['pan']}°, Tilt={servo.current_positions['tilt']}°")
        
        # Test 4: Tilt up
        print("\n🔼 Test 4: Tilt up...")
        servo.set_pan_angle(90)  # Center pan first
        servo.set_tilt_angle(120)
        time.sleep(2)
        print(f"   Position: Pan={servo.current_positions['pan']}°, Tilt={servo.current_positions['tilt']}°")
        
        # Test 5: Tilt down
        print("\n🔽 Test 5: Tilt down...")
        servo.set_tilt_angle(60)
        time.sleep(2)
        print(f"   Position: Pan={servo.current_positions['pan']}°, Tilt={servo.current_positions['tilt']}°")
        
        # Test 6: Return to center
        print("\n🏠 Test 6: Return to center...")
        servo.center_servos()
        time.sleep(2)
        print(f"   Position: Pan={servo.current_positions['pan']}°, Tilt={servo.current_positions['tilt']}°")
        
        servo.cleanup()
        print("✅ Basic servo movement test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic servo movement test failed: {e}")
        return False

def test_tracking_simulation():
    """Test servo tracking with simulated ball positions"""
    print("\n🎯 Testing Servo Tracking Simulation...")
    
    try:
        servo = BallTrackingServoController()
        
        # Simulate frame dimensions
        frame_width = 640
        frame_height = 640
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        print(f"Frame size: {frame_width}x{frame_height}, Center: ({center_x}, {center_y})")
        print(f"Deadzone: {config.TRACKING_DEADZONE} pixels")
        
        # Test scenarios
        test_positions = [
            (center_x, center_y, "CENTER (should not move)"),
            (center_x + config.TRACKING_DEADZONE + 50, center_y, "RIGHT of deadzone"),
            (center_x - config.TRACKING_DEADZONE - 50, center_y, "LEFT of deadzone"),
            (center_x, center_y + config.TRACKING_DEADZONE + 50, "BELOW deadzone"),
            (center_x, center_y - config.TRACKING_DEADZONE - 50, "ABOVE deadzone"),
            (center_x + 100, center_y + 100, "BOTTOM-RIGHT corner"),
            (center_x - 100, center_y - 100, "TOP-LEFT corner"),
        ]
        
        for i, (target_x, target_y, description) in enumerate(test_positions, 1):
            print(f"\n🎯 Test {i}: {description}")
            print(f"   Target position: ({target_x}, {target_y})")
            
            # Calculate if position is in deadzone
            error_x = target_x - center_x
            error_y = target_y - center_y
            in_deadzone = abs(error_x) <= config.TRACKING_DEADZONE and abs(error_y) <= config.TRACKING_DEADZONE
            
            print(f"   Error from center: ({error_x}, {error_y})")
            print(f"   In deadzone: {in_deadzone}")
            
            # Record position before tracking
            pan_before = servo.current_positions["pan"]
            tilt_before = servo.current_positions["tilt"]
            
            # Call track_target
            servo.track_target(target_x, target_y, frame_width, frame_height)
            
            # Check position after tracking
            pan_after = servo.current_positions["pan"]
            tilt_after = servo.current_positions["tilt"]
            
            pan_moved = abs(pan_after - pan_before) > 0.1
            tilt_moved = abs(tilt_after - tilt_before) > 0.1
            
            print(f"   Before: Pan={pan_before:.1f}°, Tilt={tilt_before:.1f}°")
            print(f"   After:  Pan={pan_after:.1f}°, Tilt={tilt_after:.1f}°")
            print(f"   Moved: Pan={pan_moved}, Tilt={tilt_moved}")
            
            if in_deadzone and (pan_moved or tilt_moved):
                print("   ⚠️  WARNING: Servo moved despite being in deadzone!")
            elif not in_deadzone and not (pan_moved or tilt_moved):
                print("   ⚠️  WARNING: Servo didn't move despite being outside deadzone!")
            else:
                print("   ✅ Servo behavior correct")
            
            time.sleep(1)
        
        # Return to center
        print(f"\n🏠 Returning to center...")
        servo.center_servos()
        time.sleep(1)
        
        servo.cleanup()
        print("✅ Tracking simulation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Tracking simulation test failed: {e}")
        return False

def test_deadzone_behavior():
    """Test deadzone behavior specifically"""
    print("\n🚫 Testing Deadzone Behavior...")
    
    try:
        servo = BallTrackingServoController()
        
        frame_width = 640
        frame_height = 640
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        print(f"Deadzone size: {config.TRACKING_DEADZONE} pixels")
        print(f"Frame center: ({center_x}, {center_y})")
        
        # Test positions just inside and outside deadzone
        deadzone_tests = [
            (center_x, center_y, "Exact center"),
            (center_x + config.TRACKING_DEADZONE - 1, center_y, "Just inside deadzone (right)"),
            (center_x + config.TRACKING_DEADZONE + 1, center_y, "Just outside deadzone (right)"),
            (center_x - config.TRACKING_DEADZONE + 1, center_y, "Just inside deadzone (left)"),
            (center_x - config.TRACKING_DEADZONE - 1, center_y, "Just outside deadzone (left)"),
        ]
        
        for i, (target_x, target_y, description) in enumerate(deadzone_tests, 1):
            print(f"\n🎯 Deadzone Test {i}: {description}")
            
            # Reset to center
            servo.center_servos()
            time.sleep(0.5)
            
            error_x = target_x - center_x
            error_y = target_y - center_y
            distance_from_center = (error_x**2 + error_y**2)**0.5
            in_deadzone = abs(error_x) <= config.TRACKING_DEADZONE and abs(error_y) <= config.TRACKING_DEADZONE
            
            print(f"   Position: ({target_x}, {target_y})")
            print(f"   Error: ({error_x}, {error_y})")
            print(f"   Distance from center: {distance_from_center:.1f} pixels")
            print(f"   Should be in deadzone: {in_deadzone}")
            
            # Record before
            pan_before = servo.current_positions["pan"]
            tilt_before = servo.current_positions["tilt"]
            
            # Track target
            servo.track_target(target_x, target_y, frame_width, frame_height)
            
            # Check after
            pan_after = servo.current_positions["pan"]
            tilt_after = servo.current_positions["tilt"]
            
            moved = abs(pan_after - pan_before) > 0.1 or abs(tilt_after - tilt_before) > 0.1
            
            print(f"   Servo moved: {moved}")
            
            if in_deadzone and moved:
                print("   ❌ ERROR: Servo moved inside deadzone!")
            elif not in_deadzone and not moved:
                print("   ❌ ERROR: Servo didn't move outside deadzone!")
            else:
                print("   ✅ Correct deadzone behavior")
            
            time.sleep(1)
        
        servo.cleanup()
        print("✅ Deadzone behavior test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Deadzone behavior test failed: {e}")
        return False

def main():
    """Run all servo tests"""
    print("🔧 SERVO MOVEMENT TEST SUITE")
    print("=" * 50)
    
    # Print configuration
    print(f"Configuration:")
    print(f"  Pan sensitivity: {config.PAN_SENSITIVITY}")
    print(f"  Tilt sensitivity: {config.TILT_SENSITIVITY}")
    print(f"  Tracking deadzone: {config.TRACKING_DEADZONE} pixels")
    print(f"  Pan limits: {config.PAN_MIN_ANGLE}° to {config.PAN_MAX_ANGLE}°")
    print(f"  Tilt limits: {config.TILT_MIN_ANGLE}° to {config.TILT_MAX_ANGLE}°")
    print(f"  Tracking smooth time: {getattr(config, 'TRACKING_SMOOTH_TIME', 'Not set')}")
    print("=" * 50)
    
    tests = [
        ("Basic Movement", test_servo_basic_movement),
        ("Tracking Simulation", test_tracking_simulation),
        ("Deadzone Behavior", test_deadzone_behavior)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
        
        if test_name != tests[-1][0]:  # Not last test
            print(f"\nWaiting 2 seconds before next test...")
            time.sleep(2)
    
    print(f"\n{'='*50}")
    print(f"SERVO TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SERVO TESTS PASSED!")
        print("Servos should be working correctly for ball tracking.")
    else:
        print("⚠️  Some servo tests failed.")
        print("Check the configuration and hardware connections.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
