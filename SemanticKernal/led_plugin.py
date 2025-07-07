#!/usr/bin/env python3
"""
LED Plugin Module
Semantic Kernel plugin for LED control using kernel functions.
"""

import logging
from typing import Annotated

from semantic_kernel.functions import kernel_function
from led_controller import LEDController

logger = logging.getLogger(__name__)


class LEDControlPlugin:
    """Semantic Kernel plugin for LED control."""
    
    def __init__(self, led_controller: LEDController):
        """Initialize the LED control plugin with a controller."""
        self.led_controller = led_controller
    
    @kernel_function(
        description="Turn the LED on",
        name="turn_led_on"
    )
    def turn_led_on(self) -> Annotated[str, "Result of turning LED on"]:
        """Turn the LED on."""
        success = self.led_controller.turn_on()
        return "LED has been turned on successfully" if success else "Failed to turn on LED"
    
    @kernel_function(
        description="Turn the LED off",
        name="turn_led_off"
    )
    def turn_led_off(self) -> Annotated[str, "Result of turning LED off"]:
        """Turn the LED off."""
        success = self.led_controller.turn_off()
        return "LED has been turned off successfully" if success else "Failed to turn off LED"
    
    @kernel_function(
        description="Get the current status of the LED",
        name="get_led_status"
    )
    def get_led_status(self) -> Annotated[str, "Current LED status"]:
        """Get the current LED status."""
        status = self.led_controller.get_status()
        return f"LED is currently {status}"
