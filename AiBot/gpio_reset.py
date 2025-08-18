#!/usr/bin/env python3
"""
GPIO Reset utility to clean up any hanging GPIO processes.
"""

import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_gpio():
    """Clean up GPIO resources."""
    try:
        # Try to import and cleanup gpiozero
        import gpiozero
        gpiozero.Device.pin_factory.reset()
        logger.info("✅ GPIO reset successful")
        
        # Also try RPi.GPIO cleanup if available
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
            logger.info("✅ RPi.GPIO cleanup successful")
        except:
            pass
            
    except ImportError:
        logger.info("gpiozero not available, skipping GPIO reset")
    except Exception as e:
        logger.error(f"❌ GPIO reset failed: {e}")

if __name__ == "__main__":
    print("🔧 Cleaning up GPIO resources...")
    cleanup_gpio()
    print("✅ GPIO cleanup completed")
    
    # Small delay to ensure cleanup
    time.sleep(0.5)
