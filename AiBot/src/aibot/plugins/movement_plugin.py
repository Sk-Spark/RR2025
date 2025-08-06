#!/usr/bin/env python3
"""
Movement Plugin Module for AiBot
Semantic Kernel plugin for robot movement control with automatic delays
"""

import logging
import asyncio
from typing import Annotated

from semantic_kernel.functions import kernel_function
from ..hardware.movement_controller import MovementController

logger = logging.getLogger(__name__)


class MovementControlPlugin:
    """Semantic Kernel plugin for robot movement control with automatic stop delays."""
    
    def __init__(self, movement_controller: MovementController):
        """Initialize the movement control plugin with a controller."""
        self.movement_controller = movement_controller
    
    @kernel_function(
        description="Move the robot forward at a specified speed for 1 second",
        name="move_forward"
    )
    async def move_forward(self, speed: Annotated[int, "Speed percentage (0-100)"] = 50) -> Annotated[str, "Result of moving forward"]:
        """Move the robot forward for 1 second then auto-stop."""
        try:
            speed = max(0, min(100, int(speed)))  # Clamp speed between 0-100
            success = await self.movement_controller.move_forward(speed, duration=1.0)
            
            if success:
                return f"Robot moved forward at {speed}% speed for 1 second and stopped automatically"
            else:
                return "Failed to move robot forward"
        except Exception as e:
            logger.error(f"Error in move_forward: {e}")
            return f"Error moving forward: {e}"
    
    @kernel_function(
        description="Move the robot backward at a specified speed for 1 second",
        name="move_backward"
    )
    async def move_backward(self, speed: Annotated[int, "Speed percentage (0-100)"] = 50) -> Annotated[str, "Result of moving backward"]:
        """Move the robot backward for 1 second then auto-stop."""
        try:
            speed = max(0, min(100, int(speed)))  # Clamp speed between 0-100
            success = await self.movement_controller.move_backward(speed, duration=1.0)
            
            if success:
                return f"Robot moved backward at {speed}% speed for 1 second and stopped automatically"
            else:
                return "Failed to move robot backward"
        except Exception as e:
            logger.error(f"Error in move_backward: {e}")
            return f"Error moving backward: {e}"
    
    @kernel_function(
        description="Turn the robot left for 1 second",
        name="turn_left"
    )
    async def turn_left(self, speed: Annotated[int, "Speed percentage (0-100)"] = 50) -> Annotated[str, "Result of turning left"]:
        """Turn the robot left for 1 second then auto-stop."""
        try:
            speed = max(0, min(100, int(speed)))  # Clamp speed between 0-100
            success = await self.movement_controller.turn_left(speed, duration=1.0)
            
            if success:
                return f"Robot turned left at {speed}% speed for 1 second and stopped automatically"
            else:
                return "Failed to turn robot left"
        except Exception as e:
            logger.error(f"Error in turn_left: {e}")
            return f"Error turning left: {e}"
    
    @kernel_function(
        description="Turn the robot right for 1 second",
        name="turn_right"
    )
    async def turn_right(self, speed: Annotated[int, "Speed percentage (0-100)"] = 50) -> Annotated[str, "Result of turning right"]:
        """Turn the robot right for 1 second then auto-stop."""
        try:
            speed = max(0, min(100, int(speed)))  # Clamp speed between 0-100
            success = await self.movement_controller.turn_right(speed, duration=1.0)
            
            if success:
                return f"Robot turned right at {speed}% speed for 1 second and stopped automatically"
            else:
                return "Failed to turn robot right"
        except Exception as e:
            logger.error(f"Error in turn_right: {e}")
            return f"Error turning right: {e}"
    
    @kernel_function(
        description="Move the robot sideways to the left (strafe left) for 1 second",
        name="strafe_left"
    )
    async def strafe_left(self, speed: Annotated[int, "Speed percentage (0-100)"] = 50) -> Annotated[str, "Result of strafing left"]:
        """Move the robot sideways to the left for 1 second then auto-stop."""
        try:
            speed = max(0, min(100, int(speed)))  # Clamp speed between 0-100
            success = await self.movement_controller.strafe_left(speed, duration=1.0)
            
            if success:
                return f"Robot strafed left at {speed}% speed for 1 second and stopped automatically"
            else:
                return "Failed to strafe robot left"
        except Exception as e:
            logger.error(f"Error in strafe_left: {e}")
            return f"Error strafing left: {e}"
    
    @kernel_function(
        description="Move the robot sideways to the right (strafe right) for 1 second",
        name="strafe_right"
    )
    async def strafe_right(self, speed: Annotated[int, "Speed percentage (0-100)"] = 50) -> Annotated[str, "Result of strafing right"]:
        """Move the robot sideways to the right for 1 second then auto-stop."""
        try:
            speed = max(0, min(100, int(speed)))  # Clamp speed between 0-100
            success = await self.movement_controller.strafe_right(speed, duration=1.0)
            
            if success:
                return f"Robot strafed right at {speed}% speed for 1 second and stopped automatically"
            else:
                return "Failed to strafe robot right"
        except Exception as e:
            logger.error(f"Error in strafe_right: {e}")
            return f"Error strafing right: {e}"
    
    @kernel_function(
        description="Stop all robot movement immediately",
        name="stop_robot"
    )
    def stop_robot(self) -> Annotated[str, "Result of stopping robot"]:
        """Stop all robot movement immediately."""
        try:
            success = self.movement_controller.stop_all_motors()
            if success:
                return "Robot stopped successfully"
            else:
                return "Failed to stop robot"
        except Exception as e:
            logger.error(f"Error in stop_robot: {e}")
            return f"Error stopping robot: {e}"
    
    @kernel_function(
        description="Get the current movement status of the robot",
        name="get_movement_status"
    )
    def get_movement_status(self) -> Annotated[str, "Current movement status"]:
        """Get the current movement status of the robot."""
        try:
            status = self.movement_controller.get_movement_status()
            return f"Robot is currently {status}"
        except Exception as e:
            logger.error(f"Error in get_movement_status: {e}")
            return f"Error getting movement status: {e}"
