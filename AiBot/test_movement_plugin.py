#!/usr/bin/env python3
"""
Test script for movement plugins - Tests each movement function independently
to verify they return correct results and execute properly.
"""

import asyncio
import logging
import sys
import os
import time
from typing import List, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.hardware.movement_controller import MovementController
from src.aibot.plugins.movement_plugin import MovementControlPlugin

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MovementPluginTester:
    """Test class for movement plugin functions"""
    
    def __init__(self):
        self.movement_controller = None
        self.movement_plugin = None
        self.test_results = []
        
    async def setup(self):
        """Initialize the movement controller and plugin"""
        try:
            print("🔧 Setting up movement controller and plugin...")
            
            # Initialize movement controller (will use mock/simulation if no hardware)
            self.movement_controller = MovementController()
            
            # Initialize movement plugin
            self.movement_plugin = MovementControlPlugin(self.movement_controller)
            
            print("✅ Setup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
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
        print(f"   Expected: {expected}")
        print(f"   Actual:   {actual}")
        print()
    
    async def test_move_forward(self):
        """Test move_forward function with various parameters"""
        print("🧪 Testing move_forward function...")
        
        # Test 1: Default parameters
        result = await self.movement_plugin.move_forward()
        expected_pattern = "Robot moved forward at 50% speed for 1.0 seconds"
        success = expected_pattern in result
        self.log_test_result("move_forward (defaults)", expected_pattern, result, success)
        
        # Test 2: Custom speed and duration
        result = await self.movement_plugin.move_forward(speed=75, duration=2.0)
        expected_pattern = "Robot moved forward at 75% speed for 2.0 seconds"
        success = expected_pattern in result
        self.log_test_result("move_forward (custom params)", expected_pattern, result, success)
        
        # Test 3: Edge case - minimum values
        result = await self.movement_plugin.move_forward(speed=1, duration=0.1)
        expected_pattern = "Robot moved forward at 1% speed for 0.1 seconds"
        success = expected_pattern in result
        self.log_test_result("move_forward (minimum values)", expected_pattern, result, success)
        
        # Test 4: Edge case - maximum values
        result = await self.movement_plugin.move_forward(speed=100, duration=10.0)
        expected_pattern = "Robot moved forward at 100% speed for 10.0 seconds"
        success = expected_pattern in result
        self.log_test_result("move_forward (maximum values)", expected_pattern, result, success)
        
        # Test 5: Parameter clamping - over limits
        result = await self.movement_plugin.move_forward(speed=150, duration=15.0)
        expected_pattern = "Robot moved forward at 100% speed for 10.0 seconds"
        success = expected_pattern in result
        self.log_test_result("move_forward (clamping test)", expected_pattern, result, success)
    
    async def test_move_backward(self):
        """Test move_backward function"""
        print("🧪 Testing move_backward function...")
        
        # Test default parameters
        result = await self.movement_plugin.move_backward()
        expected_pattern = "Robot moved backward at 50% speed for 1.0 seconds"
        success = expected_pattern in result
        self.log_test_result("move_backward (defaults)", expected_pattern, result, success)
        
        # Test custom parameters
        result = await self.movement_plugin.move_backward(speed=60, duration=1.5)
        expected_pattern = "Robot moved backward at 60% speed for 1.5 seconds"
        success = expected_pattern in result
        self.log_test_result("move_backward (custom params)", expected_pattern, result, success)
    
    async def test_turn_left(self):
        """Test turn_left function"""
        print("🧪 Testing turn_left function...")
        
        # Test default parameters
        result = await self.movement_plugin.turn_left()
        expected_pattern = "Robot turned left at 50% speed for 1.0 seconds"
        success = expected_pattern in result
        self.log_test_result("turn_left (defaults)", expected_pattern, result, success)
        
        # Test custom parameters
        result = await self.movement_plugin.turn_left(speed=40, duration=0.5)
        expected_pattern = "Robot turned left at 40% speed for 0.5 seconds"
        success = expected_pattern in result
        self.log_test_result("turn_left (custom params)", expected_pattern, result, success)
    
    async def test_turn_right(self):
        """Test turn_right function"""
        print("🧪 Testing turn_right function...")
        
        # Test default parameters
        result = await self.movement_plugin.turn_right()
        expected_pattern = "Robot turned right at 50% speed for 1.0 seconds"
        success = expected_pattern in result
        self.log_test_result("turn_right (defaults)", expected_pattern, result, success)
        
        # Test custom parameters
        result = await self.movement_plugin.turn_right(speed=70, duration=0.8)
        expected_pattern = "Robot turned right at 70% speed for 0.8 seconds"
        success = expected_pattern in result
        self.log_test_result("turn_right (custom params)", expected_pattern, result, success)
    
    async def test_stop_robot(self):
        """Test stop_robot function"""
        print("🧪 Testing stop_robot function...")
        
        result = self.movement_plugin.stop_robot()
        expected_pattern = "Robot stopped successfully"
        success = expected_pattern in result
        self.log_test_result("stop_robot", expected_pattern, result, success)
    
    async def test_get_movement_status(self):
        """Test get_movement_status function"""
        print("🧪 Testing get_movement_status function...")
        
        result = self.movement_plugin.get_movement_status()
        expected_pattern = "Robot is currently"
        success = expected_pattern in result
        self.log_test_result("get_movement_status", expected_pattern, result, success)
    
    async def test_sequential_execution(self):
        """Test that movements execute sequentially and don't interfere"""
        print("🧪 Testing sequential execution...")
        
        start_time = time.time()
        
        # Execute three short movements in sequence
        result1 = await self.movement_plugin.move_forward(speed=50, duration=0.5)
        result2 = await self.movement_plugin.turn_right(speed=50, duration=0.3)
        result3 = await self.movement_plugin.move_backward(speed=50, duration=0.5)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should take approximately 1.3 seconds (0.5 + 0.3 + 0.5)
        expected_min_time = 1.2  # Allow some margin
        expected_max_time = 2.0  # Allow for processing overhead
        
        time_success = expected_min_time <= total_time <= expected_max_time
        results_success = all([
            "moved forward" in result1,
            "turned right" in result2,
            "moved backward" in result3
        ])
        
        overall_success = time_success and results_success
        
        self.log_test_result(
            "sequential_execution", 
            f"3 movements in {expected_min_time}-{expected_max_time}s", 
            f"3 movements in {total_time:.2f}s", 
            overall_success
        )
    
    async def test_parameter_validation(self):
        """Test parameter validation and clamping"""
        print("🧪 Testing parameter validation...")
        
        # Test negative values (should be clamped to 0/0.1)
        result = await self.movement_plugin.move_forward(speed=-10, duration=-1.0)
        expected_pattern = "Robot moved forward at 0% speed for 0.1 seconds"
        success = expected_pattern in result
        self.log_test_result("parameter_validation (negative)", expected_pattern, result, success)
        
        # Test extremely high values (should be clamped to 100/10.0)
        result = await self.movement_plugin.turn_left(speed=999, duration=999.0)
        expected_pattern = "Robot turned left at 100% speed for 10.0 seconds"
        success = expected_pattern in result
        self.log_test_result("parameter_validation (excessive)", expected_pattern, result, success)
    
    def print_summary(self):
        """Print test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}")
            print()
        
        print("✅ Test execution completed!")
    
    def cleanup(self):
        """Clean up resources"""
        if self.movement_controller:
            self.movement_controller.cleanup()
        print("🧹 Cleanup completed")

async def main():
    """Main test execution"""
    print("🚀 Movement Plugin Independent Testing")
    print("=" * 50)
    
    tester = MovementPluginTester()
    
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
        await tester.test_sequential_execution()
        await tester.test_parameter_validation()
        
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
