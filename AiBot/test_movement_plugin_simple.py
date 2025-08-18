#!/usr/bin/env python3
"""
Simple test script for movement plugins - Tests each movement function independently
without requiring the full aibot package dependencies.
"""

import asyncio
import logging
import sys
import os
import time
from typing import List, Tuple

# Add src to path and import directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import only what we need without triggering the full package
from src.aibot.hardware.movement_controller import MovementController
from src.aibot.plugins.movement_plugin import MovementControlPlugin

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMovementPluginTester:
    """Simple test class for movement plugin functions"""
    
    def __init__(self):
        self.movement_controller = None
        self.movement_plugin = None
        self.test_results = []
        
    async def setup(self):
        """Initialize the movement controller and plugin"""
        try:
            print("🔧 Setting up movement controller and plugin...")
            
            # Initialize movement controller with a simple motor config
            motor_config = {
                "front_right": {"channel": 15, "in1": 14, "in2": 13},
                "front_left": {"channel": 4, "in1": 5, "in2": 6},
                "rear_right": {"channel": 10, "in1": 12, "in2": 11},
                "rear_left": {"channel": 9, "in1": 7, "in2": 8},
            }
            
            self.movement_controller = MovementController(motor_config=motor_config)
            self.movement_plugin = MovementControlPlugin(self.movement_controller)
            
            print("✅ Setup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            logger.exception("Setup error")
            return False
    
    def log_test_result(self, test_name: str, expected: str, actual: str, success: bool):
        """Log test result for reporting"""
        self.test_results.append({
            'test': test_name,
            'expected': expected,
            'actual': actual,
            'success': success
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            print(f"   Expected: {expected}")
            print(f"   Actual:   {actual}")
        print()
    
    async def test_move_forward(self):
        """Test move_forward function with various parameters"""
        print("🧪 Testing move_forward function...")
        
        try:
            # Test 1: Default parameters
            result = await self.movement_plugin.move_forward()
            expected_keywords = ["forward", "50%", "1.0"]
            success = all(keyword in result for keyword in expected_keywords)
            self.log_test_result("move_forward (defaults)", "Contains: forward, 50%, 1.0", result, success)
            
            # Test 2: Custom parameters  
            result = await self.movement_plugin.move_forward(speed=75, duration=0.5)
            expected_keywords = ["forward", "75%", "0.5"]
            success = all(keyword in result for keyword in expected_keywords)
            self.log_test_result("move_forward (custom)", "Contains: forward, 75%, 0.5", result, success)
            
        except Exception as e:
            print(f"❌ Error in move_forward test: {e}")
            self.log_test_result("move_forward", "Success", f"Error: {e}", False)
    
    async def test_move_backward(self):
        """Test move_backward function"""
        print("🧪 Testing move_backward function...")
        
        try:
            result = await self.movement_plugin.move_backward(speed=60, duration=0.5)
            expected_keywords = ["backward", "60%", "0.5"]
            success = all(keyword in result for keyword in expected_keywords)
            self.log_test_result("move_backward", "Contains: backward, 60%, 0.5", result, success)
            
        except Exception as e:
            print(f"❌ Error in move_backward test: {e}")
            self.log_test_result("move_backward", "Success", f"Error: {e}", False)
    
    async def test_turn_left(self):
        """Test turn_left function"""
        print("🧪 Testing turn_left function...")
        
        try:
            result = await self.movement_plugin.turn_left(speed=40, duration=0.3)
            expected_keywords = ["left", "40%", "0.3"]
            success = all(keyword in result for keyword in expected_keywords)
            self.log_test_result("turn_left", "Contains: left, 40%, 0.3", result, success)
            
        except Exception as e:
            print(f"❌ Error in turn_left test: {e}")
            self.log_test_result("turn_left", "Success", f"Error: {e}", False)
    
    async def test_turn_right(self):
        """Test turn_right function"""
        print("🧪 Testing turn_right function...")
        
        try:
            result = await self.movement_plugin.turn_right(speed=70, duration=0.4)
            expected_keywords = ["right", "70%", "0.4"]
            success = all(keyword in result for keyword in expected_keywords)
            self.log_test_result("turn_right", "Contains: right, 70%, 0.4", result, success)
            
        except Exception as e:
            print(f"❌ Error in turn_right test: {e}")
            self.log_test_result("turn_right", "Success", f"Error: {e}", False)
    
    async def test_stop_robot(self):
        """Test stop_robot function"""
        print("🧪 Testing stop_robot function...")
        
        try:
            result = self.movement_plugin.stop_robot()
            success = "stopped" in result.lower()
            self.log_test_result("stop_robot", "Contains: stopped", result, success)
            
        except Exception as e:
            print(f"❌ Error in stop_robot test: {e}")
            self.log_test_result("stop_robot", "Success", f"Error: {e}", False)
    
    async def test_get_movement_status(self):
        """Test get_movement_status function"""
        print("🧪 Testing get_movement_status function...")
        
        try:
            result = self.movement_plugin.get_movement_status()
            success = "robot is currently" in result.lower()
            self.log_test_result("get_movement_status", "Contains: robot is currently", result, success)
            
        except Exception as e:
            print(f"❌ Error in get_movement_status test: {e}")
            self.log_test_result("get_movement_status", "Success", f"Error: {e}", False)
    
    async def test_parameter_clamping(self):
        """Test parameter validation and clamping"""
        print("🧪 Testing parameter clamping...")
        
        try:
            # Test over-limit values
            result = await self.movement_plugin.move_forward(speed=150, duration=15.0)
            # Should be clamped to 100% and 10.0 seconds
            success = "100%" in result and "10.0" in result
            self.log_test_result("parameter_clamping (high)", "Clamped to 100% and 10.0s", result, success)
            
            # Test under-limit values  
            result = await self.movement_plugin.turn_left(speed=-10, duration=-1.0)
            # Should be clamped to 0% and 0.1 seconds
            success = ("0%" in result or "0 %" in result) and "0.1" in result
            self.log_test_result("parameter_clamping (low)", "Clamped to 0% and 0.1s", result, success)
            
        except Exception as e:
            print(f"❌ Error in parameter clamping test: {e}")
            self.log_test_result("parameter_clamping", "Success", f"Error: {e}", False)
    
    async def test_sequential_timing(self):
        """Test that movements take expected time"""
        print("🧪 Testing sequential timing...")
        
        try:
            start_time = time.time()
            
            # Execute two short movements
            await self.movement_plugin.move_forward(speed=50, duration=0.2)
            await self.movement_plugin.turn_right(speed=50, duration=0.2)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should take approximately 0.4 seconds (0.2 + 0.2)
            expected_min = 0.3  # Allow some margin
            expected_max = 1.0  # Allow for overhead
            
            success = expected_min <= total_time <= expected_max
            self.log_test_result(
                "sequential_timing", 
                f"Time between {expected_min}-{expected_max}s", 
                f"Took {total_time:.2f}s", 
                success
            )
            
        except Exception as e:
            print(f"❌ Error in timing test: {e}")
            self.log_test_result("sequential_timing", "Success", f"Error: {e}", False)
    
    def print_summary(self):
        """Print test summary"""
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        
        if total_tests > 0:
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['actual']}")
            print()
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {failed_tests} test(s) failed - check implementation")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.movement_controller:
                self.movement_controller.cleanup()
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"Warning: Cleanup error: {e}")

async def main():
    """Main test execution"""
    print("🚀 Movement Plugin Independent Testing")
    print("=" * 50)
    
    tester = SimpleMovementPluginTester()
    
    try:
        # Setup
        if not await tester.setup():
            return
        
        # Run all tests
        await tester.test_move_forward()
        await tester.test_move_backward()
        await tester.test_turn_left()
        await tester.test_turn_right()
        await tester.test_stop_robot()
        await tester.test_get_movement_status()
        await tester.test_parameter_clamping()
        await tester.test_sequential_timing()
        
        # Print summary
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        logging.exception("Test execution error")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
