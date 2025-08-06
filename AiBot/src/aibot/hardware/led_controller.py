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
    print("Warning: gpiozero not available. LED control will be simulated.")
    LED = None

logger = logging.getLogger(__name__)


class LEDController:
    """Handles LED hardware control with error handling."""
    
    def __init__(self, pin: int = 18):
        """Initialize LED controller with specified GPIO pin."""
        self.pin = pin
        self.led: Optional[LED] = None
        self.is_simulated = LED is None
        
        try:
            if not self.is_simulated:
                self.led = LED(pin)
                logger.info(f"LED controller initialized on GPIO pin {pin}")
            else:
                logger.warning("Running in simulation mode - no actual GPIO control")
        except Exception as e:
            logger.error(f"Failed to initialize LED on pin {pin}: {e}")
            self.is_simulated = True
    
    def turn_on(self) -> bool:
        """Turn on the LED."""
        try:
            if not self.is_simulated and self.led:
                self.led.on()
                logger.info("LED turned ON")
            else:
                logger.info("LED turned ON (simulated)")
            return True
        except Exception as e:
            logger.error(f"Failed to turn on LED: {e}")
            return False
    
    def turn_off(self) -> bool:
        """Turn off the LED."""
        try:
            if not self.is_simulated and self.led:
                self.led.off()
                logger.info("LED turned OFF")
            else:
                logger.info("LED turned OFF (simulated)")
            return True
        except Exception as e:
            logger.error(f"Failed to turn off LED: {e}")
            return False
    
    def get_status(self) -> str:
        """Get current LED status."""
        try:
            if not self.is_simulated and self.led:
                status = "ON" if self.led.is_lit else "OFF"
            else:
                status = "UNKNOWN (simulated)"
            return status
        except Exception as e:
            logger.error(f"Failed to get LED status: {e}")
            return "ERROR"
    
    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            if not self.is_simulated and self.led:
                self.led.close()
                logger.info("LED GPIO resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
