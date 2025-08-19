#!/usr/bin/env python3
"""
Test script for Movement Controller
Tests movement controller functionality with both mock and real hardware
"""

import unittest
import asyncio
import logging
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aibot.hardware.movement_controller import MovementController
from aibot.hardware.pca9685_controller import PCA9685Controller


class MockPCA9685Controller:
    """Mock PCA9685 controller for testing without hardware"""
    
    def __init__(self):
        self.pwm_values = {}
        self.cleanup_called = False
        
    def set_pwm(self, channel: int, duty_cycle: int) -> bool:
        """Mock set_pwm method"""
        self.pwm_values[channel] = duty_cycle
        return True
    
    def cleanup(self):
        """Mock cleanup method"""
        self.cleanup_called = True


class TestMovementController(unittest.TestCase):
    """Test cases for MovementController class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_pca = MockPCA9685Controller()
        self.movement_controller = MovementController(pca_controller=self.mock_pca)
        
        # Configure logging for tests
        logging.basicConfig(level=logging.DEBUG)
        
    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self.movement_controller, 'cleanup'):
            self.movement_controller.cleanup()

    def test_initialization(self):
        """Test movement controller initialization"""
        # Test default motor configuration
        expected_motors = {
            "front_right": {"channel": 15, "in1": 14, "in2": 13},
            "front_left": {"channel": 4, "in1": 5, "in2": 6},
            "rear_right": {"channel": 10, "in1": 12, "in2": 11},
            "rear_left": {"channel": 9, "in1": 7, "in2": 8},
        }
        
        self.assertEqual(self.movement_controller.motors, expected_motors)
        self.assertFalse(self.movement_controller._is_moving)
        self.assertIsNone(self.movement_controller._current_movement_task)

    def test_initialization_with_custom_config(self):
        """Test movement controller initialization with custom motor config"""
        custom_config = {
            "motor1": {"channel": 0, "in1": 1, "in2": 2},
            "motor2": {"channel": 3, "in1": 4, "in2": 5},
        }
        
        controller = MovementController(pca_controller=self.mock_pca, motor_config=custom_config)
        self.assertEqual(controller.motors, custom_config)

    def test_set_motor_speed_forward(self):
        """Test setting motor speed in forward direction"""
        success = self.movement_controller.set_motor_speed("front_right", 50, "forward")
        
        self.assertTrue(success)
        # Check PWM values were set correctly
        self.assertEqual(self.mock_pca.pwm_values[15], 32767)  # 50% of 65535
        self.assertEqual(self.mock_pca.pwm_values[14], 65535)  # IN1 high
        self.assertEqual(self.mock_pca.pwm_values[13], 0)     # IN2 low

    def test_set_motor_speed_backward(self):
        """Test setting motor speed in backward direction"""
        success = self.movement_controller.set_motor_speed("front_left", 75, "backward")
        
        self.assertTrue(success)
        # Check PWM values were set correctly
        self.assertEqual(self.mock_pca.pwm_values[4], 49151)  # 75% of 65535
        self.assertEqual(self.mock_pca.pwm_values[5], 0)      # IN1 low
        self.assertEqual(self.mock_pca.pwm_values[6], 65535)  # IN2 high

    def test_set_motor_speed_invalid_motor(self):
        """Test setting speed for non-existent motor"""
        success = self.movement_controller.set_motor_speed("invalid_motor", 50, "forward")
        self.assertFalse(success)

    def test_set_motor_speed_invalid_direction(self):
        """Test setting motor speed with invalid direction"""
        success = self.movement_controller.set_motor_speed("front_right", 50, "invalid")
        self.assertFalse(success)

    def test_set_motor_speed_clamping(self):
        """Test speed value clamping (0-100)"""
        # Test upper bound clamping
        success = self.movement_controller.set_motor_speed("front_right", 150, "forward")
        self.assertTrue(success)
        self.assertEqual(self.mock_pca.pwm_values[15], 65535)  # Should be clamped to 100%
        
        # Test lower bound clamping
        success = self.movement_controller.set_motor_speed("front_right", -10, "forward")
        self.assertTrue(success)
        self.assertEqual(self.mock_pca.pwm_values[15], 0)  # Should be clamped to 0%

    def test_stop_motor(self):
        """Test stopping individual motor"""
        # First set motor to some speed
        self.movement_controller.set_motor_speed("rear_right", 50, "forward")
        
        # Then stop it
        success = self.movement_controller.stop_motor("rear_right")
        
        self.assertTrue(success)
        # Check all channels are set to 0
        self.assertEqual(self.mock_pca.pwm_values[10], 0)  # Channel
        self.assertEqual(self.mock_pca.pwm_values[12], 0)  # IN1
        self.assertEqual(self.mock_pca.pwm_values[11], 0)  # IN2

    def test_stop_motor_invalid(self):
        """Test stopping non-existent motor"""
        success = self.movement_controller.stop_motor("invalid_motor")
        self.assertFalse(success)

    def test_stop_all_motors(self):
        """Test stopping all motors"""
        # Set all motors to some speed
        for motor_name in self.movement_controller.motors:
            self.movement_controller.set_motor_speed(motor_name, 50, "forward")
        
        # Stop all motors
        success = self.movement_controller.stop_all_motors()
        
        self.assertTrue(success)
        self.assertFalse(self.movement_controller._is_moving)
        
        # Check all motor channels are stopped
        for motor_name, motor_config in self.movement_controller.motors.items():
            self.assertEqual(self.mock_pca.pwm_values[motor_config["channel"]], 0)
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in1"]], 0)
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in2"]], 0)

    def test_execute_forward(self):
        """Test internal forward movement execution"""
        success = self.movement_controller._execute_forward(60)
        
        self.assertTrue(success)
        # Check all motors are set to forward at 60% speed
        for motor_name, motor_config in self.movement_controller.motors.items():
            self.assertEqual(self.mock_pca.pwm_values[motor_config["channel"]], 39321)  # 60% of 65535
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in1"]], 65535)
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in2"]], 0)

    def test_execute_backward(self):
        """Test internal backward movement execution"""
        success = self.movement_controller._execute_backward(40)
        
        self.assertTrue(success)
        # Check all motors are set to backward at 40% speed
        for motor_name, motor_config in self.movement_controller.motors.items():
            self.assertEqual(self.mock_pca.pwm_values[motor_config["channel"]], 26214)  # 40% of 65535
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in1"]], 0)
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in2"]], 65535)

    def test_execute_turn_left(self):
        """Test internal left turn execution"""
        success = self.movement_controller._execute_turn_left(50)
        
        self.assertTrue(success)
        # Right motors forward
        self.assertEqual(self.mock_pca.pwm_values[15], 32767)  # front_right channel
        self.assertEqual(self.mock_pca.pwm_values[14], 65535)  # front_right IN1
        self.assertEqual(self.mock_pca.pwm_values[13], 0)      # front_right IN2
        
        self.assertEqual(self.mock_pca.pwm_values[10], 32767)  # rear_right channel
        self.assertEqual(self.mock_pca.pwm_values[12], 65535)  # rear_right IN1
        self.assertEqual(self.mock_pca.pwm_values[11], 0)      # rear_right IN2
        
        # Left motors backward
        self.assertEqual(self.mock_pca.pwm_values[4], 32767)   # front_left channel
        self.assertEqual(self.mock_pca.pwm_values[5], 0)       # front_left IN1
        self.assertEqual(self.mock_pca.pwm_values[6], 65535)   # front_left IN2
        
        self.assertEqual(self.mock_pca.pwm_values[9], 32767)   # rear_left channel
        self.assertEqual(self.mock_pca.pwm_values[7], 0)       # rear_left IN1
        self.assertEqual(self.mock_pca.pwm_values[8], 65535)   # rear_left IN2

    def test_execute_turn_right(self):
        """Test internal right turn execution"""
        success = self.movement_controller._execute_turn_right(50)
        
        self.assertTrue(success)
        # Left motors forward
        self.assertEqual(self.mock_pca.pwm_values[4], 32767)   # front_left channel
        self.assertEqual(self.mock_pca.pwm_values[5], 65535)   # front_left IN1
        self.assertEqual(self.mock_pca.pwm_values[6], 0)       # front_left IN2
        
        self.assertEqual(self.mock_pca.pwm_values[9], 32767)   # rear_left channel
        self.assertEqual(self.mock_pca.pwm_values[7], 65535)   # rear_left IN1
        self.assertEqual(self.mock_pca.pwm_values[8], 0)       # rear_left IN2
        
        # Right motors backward
        self.assertEqual(self.mock_pca.pwm_values[15], 32767)  # front_right channel
        self.assertEqual(self.mock_pca.pwm_values[14], 0)      # front_right IN1
        self.assertEqual(self.mock_pca.pwm_values[13], 65535)  # front_right IN2
        
        self.assertEqual(self.mock_pca.pwm_values[10], 32767)  # rear_right channel
        self.assertEqual(self.mock_pca.pwm_values[12], 0)      # rear_right IN1
        self.assertEqual(self.mock_pca.pwm_values[11], 65535)  # rear_right IN2

    def test_execute_strafe_left(self):
        """Test internal left strafe execution (mecanum wheels)"""
        success = self.movement_controller._execute_strafe_left(50)
        
        self.assertTrue(success)
        # Front left and rear right forward
        self.assertEqual(self.mock_pca.pwm_values[4], 32767)   # front_left channel
        self.assertEqual(self.mock_pca.pwm_values[5], 65535)   # front_left IN1
        self.assertEqual(self.mock_pca.pwm_values[6], 0)       # front_left IN2
        
        self.assertEqual(self.mock_pca.pwm_values[10], 32767)  # rear_right channel
        self.assertEqual(self.mock_pca.pwm_values[12], 65535)  # rear_right IN1
        self.assertEqual(self.mock_pca.pwm_values[11], 0)      # rear_right IN2
        
        # Front right and rear left backward
        self.assertEqual(self.mock_pca.pwm_values[15], 32767)  # front_right channel
        self.assertEqual(self.mock_pca.pwm_values[14], 0)      # front_right IN1
        self.assertEqual(self.mock_pca.pwm_values[13], 65535)  # front_right IN2
        
        self.assertEqual(self.mock_pca.pwm_values[9], 32767)   # rear_left channel
        self.assertEqual(self.mock_pca.pwm_values[7], 0)       # rear_left IN1
        self.assertEqual(self.mock_pca.pwm_values[8], 65535)   # rear_left IN2

    def test_execute_strafe_right(self):
        """Test internal right strafe execution (mecanum wheels)"""
        success = self.movement_controller._execute_strafe_right(50)
        
        self.assertTrue(success)
        # Front right and rear left forward
        self.assertEqual(self.mock_pca.pwm_values[15], 32767)  # front_right channel
        self.assertEqual(self.mock_pca.pwm_values[14], 65535)  # front_right IN1
        self.assertEqual(self.mock_pca.pwm_values[13], 0)      # front_right IN2
        
        self.assertEqual(self.mock_pca.pwm_values[9], 32767)   # rear_left channel
        self.assertEqual(self.mock_pca.pwm_values[7], 65535)   # rear_left IN1
        self.assertEqual(self.mock_pca.pwm_values[8], 0)       # rear_left IN2
        
        # Front left and rear right backward
        self.assertEqual(self.mock_pca.pwm_values[4], 32767)   # front_left channel
        self.assertEqual(self.mock_pca.pwm_values[5], 0)       # front_left IN1
        self.assertEqual(self.mock_pca.pwm_values[6], 65535)   # front_left IN2
        
        self.assertEqual(self.mock_pca.pwm_values[10], 32767)  # rear_right channel
        self.assertEqual(self.mock_pca.pwm_values[12], 0)      # rear_right IN1
        self.assertEqual(self.mock_pca.pwm_values[11], 65535)  # rear_right IN2

    def test_get_movement_status(self):
        """Test getting movement status"""
        # Initially should be stopped
        status = self.movement_controller.get_movement_status()
        self.assertEqual(status, "stopped")
        
        # Set moving status
        self.movement_controller._is_moving = True
        status = self.movement_controller.get_movement_status()
        self.assertEqual(status, "moving")

    def test_cleanup(self):
        """Test cleanup functionality"""
        self.movement_controller.cleanup()
        self.assertTrue(self.mock_pca.cleanup_called)


class TestMovementControllerAsync(unittest.IsolatedAsyncioTestCase):
    """Async test cases for MovementController movement methods"""
    
    async def asyncSetUp(self):
        """Set up test fixtures before each async test method."""
        self.mock_pca = MockPCA9685Controller()
        self.movement_controller = MovementController(pca_controller=self.mock_pca)
        
        # Configure logging for tests
        logging.basicConfig(level=logging.DEBUG)
        
    async def asyncTearDown(self):
        """Clean up after each async test method."""
        if hasattr(self.movement_controller, 'cleanup'):
            self.movement_controller.cleanup()

    async def test_move_forward(self):
        """Test forward movement with timeout"""
        result = await self.movement_controller.move_forward(speed=50, duration=0.1)
        
        self.assertTrue(result)
        # Check that all motors were set to forward
        for motor_name, motor_config in self.movement_controller.motors.items():
            self.assertEqual(self.mock_pca.pwm_values[motor_config["channel"]], 32767)
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in1"]], 65535)
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in2"]], 0)

    async def test_move_backward(self):
        """Test backward movement with timeout"""
        result = await self.movement_controller.move_backward(speed=75, duration=0.1)
        
        self.assertTrue(result)
        # Check that all motors were set to backward
        for motor_name, motor_config in self.movement_controller.motors.items():
            self.assertEqual(self.mock_pca.pwm_values[motor_config["channel"]], 49151)  # 75%
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in1"]], 0)
            self.assertEqual(self.mock_pca.pwm_values[motor_config["in2"]], 65535)

    async def test_turn_left(self):
        """Test left turn movement with timeout"""
        result = await self.movement_controller.turn_left(speed=60, duration=0.1)
        
        self.assertTrue(result)
        # Verify turn left pattern was executed
        # Right motors forward, left motors backward
        self.assertEqual(self.mock_pca.pwm_values[14], 65535)  # front_right IN1
        self.assertEqual(self.mock_pca.pwm_values[5], 0)       # front_left IN1

    async def test_turn_right(self):
        """Test right turn movement with timeout"""
        result = await self.movement_controller.turn_right(speed=60, duration=0.1)
        
        self.assertTrue(result)
        # Verify turn right pattern was executed
        # Left motors forward, right motors backward
        self.assertEqual(self.mock_pca.pwm_values[5], 65535)   # front_left IN1
        self.assertEqual(self.mock_pca.pwm_values[14], 0)      # front_right IN1

    async def test_strafe_left(self):
        """Test left strafe movement with timeout"""
        result = await self.movement_controller.strafe_left(speed=50, duration=0.1)
        
        self.assertTrue(result)
        # Verify strafe left pattern was executed
        self.assertEqual(self.mock_pca.pwm_values[5], 65535)   # front_left IN1 (forward)
        self.assertEqual(self.mock_pca.pwm_values[12], 65535)  # rear_right IN1 (forward)
        self.assertEqual(self.mock_pca.pwm_values[14], 0)      # front_right IN1 (backward)
        self.assertEqual(self.mock_pca.pwm_values[7], 0)       # rear_left IN1 (backward)

    async def test_strafe_right(self):
        """Test right strafe movement with timeout"""
        result = await self.movement_controller.strafe_right(speed=50, duration=0.1)
        
        self.assertTrue(result)
        # Verify strafe right pattern was executed
        self.assertEqual(self.mock_pca.pwm_values[14], 65535)  # front_right IN1 (forward)
        self.assertEqual(self.mock_pca.pwm_values[7], 65535)   # rear_left IN1 (forward)
        self.assertEqual(self.mock_pca.pwm_values[5], 0)       # front_left IN1 (backward)
        self.assertEqual(self.mock_pca.pwm_values[12], 0)      # rear_right IN1 (backward)

    async def test_movement_cancellation(self):
        """Test that new movement cancels previous movement"""
        # Start a long movement
        task1 = asyncio.create_task(
            self.movement_controller.move_forward(speed=50, duration=1.0)
        )
        
        # Wait a bit then start another movement
        await asyncio.sleep(0.05)
        result2 = await self.movement_controller.move_backward(speed=50, duration=0.1)
        
        # The second movement should succeed
        self.assertTrue(result2)
        
        # Wait for the first task to complete (should be cancelled)
        try:
            await task1
        except asyncio.CancelledError:
            pass

    async def test_auto_stop_timing(self):
        """Test that movement automatically stops after specified duration"""
        import time
        
        start_time = time.time()
        result = await self.movement_controller.move_forward(speed=50, duration=0.2)
        end_time = time.time()
        
        self.assertTrue(result)
        # Check that the duration was approximately correct (within tolerance)
        elapsed_time = end_time - start_time
        self.assertGreaterEqual(elapsed_time, 0.15)  # Should be at least 0.15 seconds
        self.assertLessEqual(elapsed_time, 0.35)     # Should be less than 0.35 seconds


class TestMovementControllerIntegration(unittest.TestCase):
    """Integration tests with mock PCA9685 hardware errors"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_pca = MockPCA9685Controller()
        self.movement_controller = MovementController(pca_controller=self.mock_pca)
    
    def test_motor_failure_handling(self):
        """Test handling of motor control failures"""
        # Make the mock PCA controller fail
        self.mock_pca.set_pwm = Mock(return_value=False)
        
        success = self.movement_controller.set_motor_speed("front_right", 50, "forward")
        self.assertFalse(success)
    
    def test_exception_handling(self):
        """Test handling of exceptions in motor control"""
        # Make the mock PCA controller raise an exception
        self.mock_pca.set_pwm = Mock(side_effect=Exception("Hardware error"))
        
        success = self.movement_controller.set_motor_speed("front_right", 50, "forward")
        self.assertFalse(success)


def run_interactive_test():
    """Run interactive test for manual hardware validation"""
    print("🤖 AiBot Movement Controller Interactive Test")
    print("=" * 50)
    print("This will test movement controller with mock hardware.")
    print("Press Ctrl+C to exit at any time.\n")
    
    try:
        # Create mock controller
        mock_pca = MockPCA9685Controller()
        controller = MovementController(pca_controller=mock_pca)
        
        async def test_movements():
            print("Testing all movement functions...")
            
            movements = [
                ("Forward", controller.move_forward, 50, 0.5),
                ("Backward", controller.move_backward, 50, 0.5),
                ("Turn Left", controller.turn_left, 50, 0.5),
                ("Turn Right", controller.turn_right, 50, 0.5),
                ("Strafe Left", controller.strafe_left, 50, 0.5),
                ("Strafe Right", controller.strafe_right, 50, 0.5),
            ]
            
            for name, func, speed, duration in movements:
                print(f"\n🔄 Testing {name} movement...")
                print(f"   Speed: {speed}%, Duration: {duration}s")
                
                result = await func(speed=speed, duration=duration)
                status = "✅ SUCCESS" if result else "❌ FAILED"
                print(f"   Result: {status}")
                
                # Show PWM values for demonstration
                print(f"   Mock PWM Values: {dict(list(mock_pca.pwm_values.items())[:6])}...")
                
                await asyncio.sleep(0.2)  # Brief pause between tests
            
            print(f"\n📊 Movement Status: {controller.get_movement_status()}")
            print("🛑 Stopping all motors...")
            controller.stop_all_motors()
            print(f"📊 Final Status: {controller.get_movement_status()}")
            
            print("\n🧹 Cleaning up...")
            controller.cleanup()
            print("✅ Cleanup completed!")
        
        # Run async test
        asyncio.run(test_movements())
        
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AiBot Movement Controller Test Script")
    parser.add_argument("--interactive", "-i", action="store_true", 
                        help="Run interactive test instead of unit tests")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    if args.interactive:
        run_interactive_test()
    else:
        print("🧪 Running Movement Controller Unit Tests")
        print("=" * 45)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test classes
        suite.addTests(loader.loadTestsFromTestCase(TestMovementController))
        suite.addTests(loader.loadTestsFromTestCase(TestMovementControllerAsync))
        suite.addTests(loader.loadTestsFromTestCase(TestMovementControllerIntegration))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print(f"\n📊 Test Results Summary:")
        print(f"   Tests Run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        if result.failures:
            print(f"\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"   - {test}")
        
        if result.errors:
            print(f"\n💥 Errors:")
            for test, traceback in result.errors:
                print(f"   - {test}")
        
        if not result.failures and not result.errors:
            print("\n🎉 All tests passed!")
