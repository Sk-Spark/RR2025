#!/usr/bin/env python3
"""
Test script to verify the LED control setup without Ollama dependency.
This script tests the LEDController and LEDControlPlugin independently.
"""

import asyncio
import sys
import os
import time

# Add the current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import LEDController, LEDControlPlugin

def test_led_controller():
    """Test the LED controller functionality."""
    print("Testing LED Controller...")
    
    # Initialize LED controller
    led_controller = LEDController(pin=18)
    
    # Test turn on
    print("Testing turn_on()...")
    result = led_controller.turn_on()
    print(f"Turn on result: {result}")
    
    # Test status
    print("Testing get_status()...")
    status = led_controller.get_status()
    print(f"LED status: {status}")
    
    # Wait for 2 seconds to see LED on
    print("Waiting 2 seconds with LED on...")
    time.sleep(2)
    
    # Test turn off
    print("Testing turn_off()...")
    result = led_controller.turn_off()
    print(f"Turn off result: {result}")
    
    # Test status again
    status = led_controller.get_status()
    print(f"LED status after turn off: {status}")
    
    # Wait for 1 second to see LED off
    print("Waiting 1 second with LED off...")
    time.sleep(1)
    
    # Cleanup
    led_controller.cleanup()
    print("LED controller test completed.")
    
    return led_controller

def test_led_plugin():
    """Test the LED plugin functionality."""
    print("\nTesting LED Plugin...")
    
    # Initialize LED controller and plugin
    led_controller = LEDController(pin=18)
    led_plugin = LEDControlPlugin(led_controller)
    
    # Test plugin functions
    print("Testing turn_led_on()...")
    result = led_plugin.turn_led_on()
    print(f"Plugin turn on result: {result}")
    
    print("Testing get_led_status()...")
    result = led_plugin.get_led_status()
    print(f"Plugin status result: {result}")
    
    # Wait for 2 seconds to see LED on
    print("Waiting 2 seconds with LED on...")
    time.sleep(2)
    
    print("Testing turn_led_off()...")
    result = led_plugin.turn_led_off()
    print(f"Plugin turn off result: {result}")
    
    # Wait for 1 second to see LED off
    print("Waiting 1 second with LED off...")
    time.sleep(1)
    
    # Cleanup
    led_controller.cleanup()
    print("LED plugin test completed.")

def main():
    """Run all tests."""
    print("🧪 LED Control Test Suite")
    print("=" * 40)
    
    try:
        # Test LED controller
        test_led_controller()
        
        # Test LED plugin
        test_led_plugin()
        
        print("\n✅ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Ensure llama3.2:1b model is available: ollama pull llama3.2:1b")
        print("3. Run the main script: python main.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Check your setup and try again.")

if __name__ == "__main__":
    main()
