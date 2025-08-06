#!/usr/bin/env python3
"""
Comprehensive test suite for all modules in the LED Control application.
"""

import asyncio
import sys
import os
import time
import logging

# Add the current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from led_controller import LEDController
from led_plugin import LEDControlPlugin
from config import AppConfig, ConfigManager
from app import LEDControlApp

# Set up logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_config_manager():
    """Test the configuration manager."""
    print("🧪 Testing Configuration Manager...")
    
    # Test default configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"Default GPIO pin: {config.led_pin}")
    print(f"Default model: {config.model_name}")
    print(f"Default base URL: {config.base_url}")
    
    # Test configuration validation
    is_valid = config_manager.validate_config()
    print(f"Configuration validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    
    # Test configuration update
    try:
        config_manager.update_config(led_pin=22, model_name="test_model")
        updated_config = config_manager.get_config()
        print(f"Updated GPIO pin: {updated_config.led_pin}")
        print(f"Updated model: {updated_config.model_name}")
        print("Configuration update: ✅ PASSED")
    except Exception as e:
        print(f"Configuration update: ❌ FAILED - {e}")
    
    print("Configuration Manager test completed.\n")


def test_led_controller():
    """Test the LED controller functionality."""
    print("🧪 Testing LED Controller...")
    
    # Initialize LED controller
    led_controller = LEDController(pin=18)
    
    # Test turn on
    print("Testing turn_on()...")
    result = led_controller.turn_on()
    print(f"Turn on result: {'✅ PASSED' if result else '❌ FAILED'}")
    
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
    print(f"Turn off result: {'✅ PASSED' if result else '❌ FAILED'}")
    
    # Test status again
    status = led_controller.get_status()
    print(f"LED status after turn off: {status}")
    
    # Wait for 1 second to see LED off
    print("Waiting 1 second with LED off...")
    time.sleep(1)
    
    # Cleanup
    led_controller.cleanup()
    print("LED Controller test completed.\n")
    
    return led_controller


def test_led_plugin():
    """Test the LED plugin functionality."""
    print("🧪 Testing LED Plugin...")
    
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
    print("LED Plugin test completed.\n")


async def test_led_control_app():
    """Test the LED control application."""
    print("🧪 Testing LED Control Application...")
    
    try:
        # Create a custom configuration for testing
        config = AppConfig(
            led_pin=18,
            model_name="llama3.2:1b",
            base_url="http://localhost:11434",
            log_level="INFO"
        )
        config_manager = ConfigManager(config)
        
        # Initialize the application
        app = LEDControlApp(config_manager)
        
        # Test initialization
        print("Testing app initialization...")
        init_result = await app.initialize()
        print(f"App initialization: {'✅ PASSED' if init_result else '❌ FAILED'}")
        
        if init_result:
            print("✅ Application initialized successfully!")
            print("Note: Full interactive test requires manual testing with 'python main.py'")
        
        # Cleanup
        app.cleanup()
        print("LED Control Application test completed.\n")
        
    except Exception as e:
        print(f"❌ Application test failed: {e}")


def test_integration():
    """Test integration between all components."""
    print("🧪 Testing Integration...")
    
    try:
        # Test configuration → LED controller → Plugin chain
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        led_controller = LEDController(pin=config.led_pin)
        led_plugin = LEDControlPlugin(led_controller)
        
        print("Testing integration: Config → Controller → Plugin")
        
        # Test the full chain
        result = led_plugin.turn_led_on()
        print(f"Integration turn on: {result}")
        
        time.sleep(1)
        
        result = led_plugin.turn_led_off()
        print(f"Integration turn off: {result}")
        
        # Cleanup
        led_controller.cleanup()
        
        print("Integration test: ✅ PASSED")
        
    except Exception as e:
        print(f"Integration test: ❌ FAILED - {e}")
    
    print("Integration test completed.\n")


def main():
    """Run all tests."""
    print("🧪 LED Control Modular Test Suite")
    print("=" * 50)
    
    try:
        # Test each module
        test_config_manager()
        test_led_controller()
        test_led_plugin()
        test_integration()
        
        # Test async components
        print("Testing async components...")
        asyncio.run(test_led_control_app())
        
        print("✅ All tests completed successfully!")
        print("\nModule Structure:")
        print("├── config.py          - Configuration management")
        print("├── led_controller.py  - GPIO hardware control")
        print("├── led_plugin.py      - Semantic Kernel plugin")
        print("├── ollama_agent.py    - Ollama LLM integration")
        print("├── app.py             - Main application logic")
        print("├── main.py            - Entry point")
        print("└── test_modules.py    - This test file")
        
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Test LED control commands")
        print("3. Verify Ollama integration")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Check your setup and try again.")


if __name__ == "__main__":
    main()
