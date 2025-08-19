#!/usr/bin/env python3
"""
AiBot Test Runner
Simplified test runner for AiBot components
"""

import os
import sys
import subprocess
import argparse

def run_movement_controller_tests(interactive=False, verbose=False):
    """Run movement controller tests"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_script = os.path.join(script_dir, "test_movement_controller.py")
    
    cmd = [sys.executable, test_script]
    
    if interactive:
        cmd.append("--interactive")
    if verbose:
        cmd.append("--verbose")
    
    print(f"🚀 Running movement controller tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=script_dir)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_all_tests(verbose=False):
    """Run all available tests"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all test files
    test_files = []
    for file in os.listdir(script_dir):
        if file.startswith("test_") and file.endswith(".py"):
            test_files.append(file)
    
    if not test_files:
        print("❌ No test files found!")
        return False
    
    print(f"🧪 Found {len(test_files)} test file(s): {', '.join(test_files)}")
    print("-" * 50)
    
    all_passed = True
    for test_file in test_files:
        test_path = os.path.join(script_dir, test_file)
        cmd = [sys.executable, test_path]
        if verbose:
            cmd.append("--verbose")
        
        print(f"\n🔄 Running {test_file}...")
        try:
            result = subprocess.run(cmd, cwd=script_dir)
            if result.returncode != 0:
                all_passed = False
                print(f"❌ {test_file} failed!")
            else:
                print(f"✅ {test_file} passed!")
        except Exception as e:
            print(f"💥 Error running {test_file}: {e}")
            all_passed = False
    
    return all_passed

def main():
    parser = argparse.ArgumentParser(description="AiBot Test Runner")
    parser.add_argument("--test", "-t", choices=["movement", "all"], default="all",
                        help="Which tests to run (default: all)")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run interactive tests")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")
    
    args = parser.parse_args()
    
    print("🤖 AiBot Test Runner")
    print("=" * 40)
    
    success = True
    
    if args.test == "movement":
        success = run_movement_controller_tests(args.interactive, args.verbose)
    elif args.test == "all":
        if args.interactive:
            print("⚠️  Interactive mode only available for specific tests")
            success = run_movement_controller_tests(True, args.verbose)
        else:
            success = run_all_tests(args.verbose)
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
