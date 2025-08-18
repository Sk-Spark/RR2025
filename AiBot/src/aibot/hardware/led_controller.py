#!/usr/bin/env python3
"""
LED Controller Module
Handles LED hardware control with error handling using gpiozero library.
"""

import logging
from typing import Optional

try:
    from gpiozero import LED
except ImportError:
    print("Error: gpiozero not available. Please install gpiozero for LED control.")
    LED = None

logger = logging.getLogger(__name__)


class LEDController:
    """Handles LED hardware control with error handling."""
    
    def __init__(self, pin: int = 18):
        """Initialize LED controller with specified GPIO pin."""
        self.pin = pin
        self.led = None
        
        try:
            if LED is not None:
                # Try to cleanup any existing GPIO usage first
                try:
                    import gpiozero
                    if hasattr(gpiozero.Device, 'pin_factory') and gpiozero.Device.pin_factory:
                        gpiozero.Device.pin_factory.reset()
                except:
                    pass
                
                self.led = LED(pin)
                logger.info(f"LED controller initialized on GPIO pin {pin}")
            else:
                logger.error("gpiozero not available - LED control requires hardware access")
        except Exception as e:
            logger.error(f"Failed to initialize LED on pin {pin}: {e}")
            if "GPIO busy" in str(e) or "Device or resource busy" in str(e):
                logger.info("Tip: GPIO pin is busy. Try running 'sudo pkill -f python' or reboot to free GPIO resources")
            self.led = None
    
    def turn_on(self) -> bool:
        """Turn on the LED."""
        try:
            if self.led:
                self.led.on()
                logger.info("LED turned ON")
                return True
            else:
                logger.error("LED hardware not available")
                return False
        except Exception as e:
            logger.error(f"Failed to turn on LED: {e}")
            return False
    
    def turn_off(self) -> bool:
        """Turn off the LED."""
        try:
            if self.led:
                self.led.off()
                logger.info("LED turned OFF")
                return True
            else:
                logger.error("LED hardware not available")
                return False
        except Exception as e:
            logger.error(f"Failed to turn off LED: {e}")
            return False
    
    def get_status(self) -> str:
        """Get current LED status."""
        try:
            if self.led:
                status = "ON" if self.led.is_lit else "OFF"
                return status
            else:
                logger.error("LED hardware not available")
                return "HARDWARE_ERROR"
        except Exception as e:
            logger.error(f"Failed to get LED status: {e}")
            return "ERROR"
    
    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            if self.led:
                self.led.close()
                logger.info("LED GPIO resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
