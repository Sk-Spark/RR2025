#!/usr/bin/env python3
"""
Hardware Test Runner for AiBot
Runs all hardware-specific tests on Raspberry Pi 5
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_test_script(script_name: str, description: str) -> bool:
    """Run a test script and return success status"""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Test script not found: {script_path}")
        return False
    
    print(f"\n🧪 Running: {description}")
    print("=" * 50)
    
    try:
        # Run the test script using the current Python interpreter
        result = subprocess.run([
            sys.executable, str(script_path), '--no-confirm'
        ], check=False, capture_output=False)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"💥 {description} - CRASHED: {e}")
        return False


def main():
    """Main function to run all hardware tests"""
    print("🤖 AiBot Hardware Test Suite")
    print("============================")
    print("⚠️  WARNING: These tests will control physical hardware!")
    print("    Ensure the robot is safely positioned and connected.")
    
    # Safety confirmation
    response = input("\nProceed with all hardware tests? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("Test suite cancelled by user.")
        return False
    
    # List of tests to run
    test_scripts = [
        ("test_movement_hardware.py", "Movement Controller Hardware Tests"),
        # Add more hardware test scripts here as they are created
        # ("test_led_hardware.py", "LED Controller Hardware Tests"),
        # ("test_pca9685_hardware.py", "PCA9685 Controller Hardware Tests"),
    ]
    
    total_tests = len(test_scripts)
    passed_tests = 0
    failed_tests = []
    
    start_time = time.time()
    
    for script_name, description in test_scripts:
        if run_test_script(script_name, description):
            passed_tests += 1
        else:
            failed_tests.append(description)
        
        time.sleep(1)  # Brief pause between tests
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🏁 Hardware Test Suite Summary")
    print("=" * 60)
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"⏱️  Duration: {duration:.1f} seconds")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
        return False
    else:
        print("\n🎉 All hardware tests passed!")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
