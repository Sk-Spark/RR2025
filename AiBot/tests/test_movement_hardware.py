#!/usr/bin/env python3
"""
Hardware Test Script for Movement Controller
Tests actual movement controller functionality on Raspberry Pi 5
No mocking - tests real hardware components
"""

import sys
import os
import time
import asyncio
import logging
from typing import Dict, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aibot.hardware.movement_controller import MovementController
from aibot.hardware.pca9685_controller import PCA9685Controller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/movement_test.log')
    ]
)

logger = logging.getLogger(__name__)


class MovementControllerHardwareTest:
    """Hardware test class for MovementController on Raspberry Pi 5"""
    
    def __init__(self):
        """Initialize the hardware test"""
        self.movement_controller = None
        self.test_results: Dict[str, bool] = {}
        self.failed_tests: List[str] = []
        
    def setup(self) -> bool:
        """Initialize the movement controller"""
        try:
            logger.info("🔧 Initializing Movement Controller for hardware testing...")
            self.movement_controller = MovementController()
            logger.info("✅ Movement Controller initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Movement Controller: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.movement_controller:
            logger.info("🧹 Cleaning up Movement Controller...")
            self.movement_controller.stop_all_motors()
            if hasattr(self.movement_controller, 'cleanup'):
                self.movement_controller.cleanup()
    
    def test_motor_initialization(self) -> bool:
        """Test that all motors are properly initialized"""
        test_name = "Motor Initialization"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Check that all expected motors are configured
            expected_motors = ["front_right", "front_left", "rear_right", "rear_left"]
            actual_motors = list(self.movement_controller.motors.keys())
            
            if set(expected_motors) == set(actual_motors):
                logger.info(f"✅ {test_name} - All motors configured correctly")
                return True
            else:
                logger.error(f"❌ {test_name} - Motor configuration mismatch")
                logger.error(f"Expected: {expected_motors}")
                logger.error(f"Actual: {actual_motors}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            return False
    
    def test_individual_motor_control(self) -> bool:
        """Test individual motor control"""
        test_name = "Individual Motor Control"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Test each motor individually
            for motor_name in self.movement_controller.motors:
                logger.info(f"  Testing motor: {motor_name}")
                
                # Test forward direction at low speed
                success = self.movement_controller.set_motor_speed(motor_name, 30, "forward")
                if not success:
                    logger.error(f"❌ Failed to set {motor_name} forward")
                    return False
                
                time.sleep(0.5)  # Brief movement
                
                # Test backward direction at low speed
                success = self.movement_controller.set_motor_speed(motor_name, 30, "backward")
                if not success:
                    logger.error(f"❌ Failed to set {motor_name} backward")
                    return False
                
                time.sleep(0.5)  # Brief movement
                
                # Stop the motor
                success = self.movement_controller.stop_motor(motor_name)
                if not success:
                    logger.error(f"❌ Failed to stop {motor_name}")
                    return False
                
                time.sleep(0.2)
            
            logger.info(f"✅ {test_name} - All individual motors tested successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            return False
    
    def test_speed_control(self) -> bool:
        """Test motor speed control at different levels"""
        test_name = "Speed Control"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            motor_name = "front_right"  # Test with one motor
            speed_levels = [25, 50, 75]
            
            for speed in speed_levels:
                logger.info(f"  Testing speed: {speed}%")
                
                success = self.movement_controller.set_motor_speed(motor_name, speed, "forward")
                if not success:
                    logger.error(f"❌ Failed to set speed {speed}% for {motor_name}")
                    return False
                
                time.sleep(1.0)  # Let motor run at this speed
                
                # Stop motor
                self.movement_controller.stop_motor(motor_name)
                time.sleep(0.5)
            
            logger.info(f"✅ {test_name} - Speed control tested successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            return False
    
    def test_stop_all_motors(self) -> bool:
        """Test emergency stop functionality"""
        test_name = "Stop All Motors"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Start all motors
            for motor_name in self.movement_controller.motors:
                self.movement_controller.set_motor_speed(motor_name, 40, "forward")
            
            time.sleep(0.5)
            
            # Stop all motors
            success = self.movement_controller.stop_all_motors()
            if not success:
                logger.error(f"❌ Stop all motors failed")
                return False
            
            logger.info(f"✅ {test_name} - Emergency stop tested successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            return False
    
    async def test_movement_patterns(self) -> bool:
        """Test basic movement patterns"""
        test_name = "Movement Patterns"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Test forward movement
            logger.info("  Testing forward movement...")
            await self.movement_controller.move_forward(duration=1.0)
            await asyncio.sleep(0.5)
            
            # Test backward movement
            logger.info("  Testing backward movement...")
            await self.movement_controller.move_backward(duration=1.0)
            await asyncio.sleep(0.5)
            
            # Test left turn
            logger.info("  Testing left turn...")
            await self.movement_controller.turn_left(duration=1.0)
            await asyncio.sleep(0.5)
            
            # Test right turn
            logger.info("  Testing right turn...")
            await self.movement_controller.turn_right(duration=1.0)
            await asyncio.sleep(0.5)
            
            # Test strafe left (if supported)
            if hasattr(self.movement_controller, 'strafe_left'):
                logger.info("  Testing strafe left...")
                await self.movement_controller.strafe_left(duration=1.0)
                await asyncio.sleep(0.5)
            
            # Test strafe right (if supported)
            if hasattr(self.movement_controller, 'strafe_right'):
                logger.info("  Testing strafe right...")
                await self.movement_controller.strafe_right(duration=1.0)
                await asyncio.sleep(0.5)
            
            logger.info(f"✅ {test_name} - All movement patterns tested successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            return False
    
    def test_movement_status(self) -> bool:
        """Test movement status tracking"""
        test_name = "Movement Status"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Initially should not be moving
            status = self.movement_controller.get_movement_status()
            if status != "stopped":
                logger.error(f"❌ Controller reports '{status}' when it should be stopped")
                return False
            
            # Start a motor and check status
            self.movement_controller.set_motor_speed("front_right", 30, "forward")
            time.sleep(0.1)
            
            # Stop and check status again
            self.movement_controller.stop_all_motors()
            time.sleep(0.1)
            
            status = self.movement_controller.get_movement_status()
            if status != "stopped":
                logger.error(f"❌ Controller reports '{status}' after stop_all_motors")
                return False
            
            logger.info(f"✅ {test_name} - Movement status tracking works correctly")
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid inputs"""
        test_name = "Error Handling"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Test invalid motor name
            result = self.movement_controller.set_motor_speed("invalid_motor", 50, "forward")
            if result:
                logger.error(f"❌ Should have failed for invalid motor name")
                return False
            
            # Test invalid direction
            result = self.movement_controller.set_motor_speed("front_right", 50, "invalid_direction")
            if result:
                logger.error(f"❌ Should have failed for invalid direction")
                return False
            
            # Test speed clamping (should not crash with out-of-range values)
            result = self.movement_controller.set_motor_speed("front_right", 150, "forward")  # Over 100%
            if not result:
                logger.error(f"❌ Should handle speed clamping gracefully")
                return False
            
            result = self.movement_controller.set_motor_speed("front_right", -10, "forward")  # Negative
            if not result:
                logger.error(f"❌ Should handle negative speed gracefully")
                return False
            
            # Clean up
            self.movement_controller.stop_all_motors()
            
            logger.info(f"✅ {test_name} - Error handling works correctly")
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all hardware tests"""
        logger.info("🚀 Starting Movement Controller Hardware Tests")
        logger.info("=" * 60)
        
        if not self.setup():
            logger.error("❌ Setup failed, aborting tests")
            return False
        
        # List of tests to run
        tests = [
            ("Motor Initialization", self.test_motor_initialization),
            ("Individual Motor Control", self.test_individual_motor_control),
            ("Speed Control", self.test_speed_control),
            ("Stop All Motors", self.test_stop_all_motors),
            ("Movement Status", self.test_movement_status),
            ("Error Handling", self.test_error_handling),
            ("Movement Patterns", self.test_movement_patterns),  # Async test
        ]
        
        total_tests = len(tests)
        passed_tests = 0
        
        try:
            for test_name, test_func in tests:
                logger.info(f"\n📋 Running test: {test_name}")
                
                try:
                    if test_name == "Movement Patterns":
                        # This is an async test
                        result = await test_func()
                    else:
                        result = test_func()
                    
                    self.test_results[test_name] = result
                    if result:
                        passed_tests += 1
                    else:
                        self.failed_tests.append(test_name)
                        
                except Exception as e:
                    logger.error(f"❌ Test {test_name} crashed: {e}")
                    self.test_results[test_name] = False
                    self.failed_tests.append(test_name)
                
                # Always ensure motors are stopped between tests
                if self.movement_controller:
                    self.movement_controller.stop_all_motors()
                    time.sleep(0.5)
        
        finally:
            self.cleanup()
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("🏁 Test Summary")
        logger.info("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
        
        logger.info(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
        
        if self.failed_tests:
            logger.info(f"❌ Failed tests: {', '.join(self.failed_tests)}")
            return False
        else:
            logger.info("🎉 All tests passed!")
            return True


def main():
    """Main function to run the hardware tests"""
    print("🤖 AiBot Movement Controller Hardware Test")
    print("==========================================")
    print("⚠️  WARNING: This test will move physical motors!")
    print("    Make sure the robot is safely positioned.")
    
    # Safety confirmation
    response = input("\nProceed with hardware testing? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("Test cancelled by user.")
        return False
    
    # Create and run the test
    test_runner = MovementControllerHardwareTest()
    
    try:
        # Run the async test suite
        result = asyncio.run(test_runner.run_all_tests())
        return result
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        test_runner.cleanup()
        return False
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        test_runner.cleanup()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Movement Controller Hardware Test')
    parser.add_argument('--no-confirm', action='store_true', 
                      help='Skip safety confirmation (use with caution)')
    parser.add_argument('--log-level', default='INFO', 
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                      help='Set logging level')
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    if args.no_confirm:
        # Skip confirmation for automated testing
        test_runner = MovementControllerHardwareTest()
        success = asyncio.run(test_runner.run_all_tests())
        sys.exit(0 if success else 1)
    else:
        success = main()
        sys.exit(0 if success else 1)
