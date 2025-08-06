#!/usr/bin/env python3
"""
Camera Controller for DummyAiBot - Testing without Hardware
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CameraController:
    """Dummy camera controller for testing without hardware"""
    
    def __init__(self, config=None):
        self.config = config
        self.pan_angle = 0.0    # Current pan angle (-90 to 90)
        self.tilt_angle = 0.0   # Current tilt angle (-90 to 90)
        self.is_moving = False
        logger.info("Camera controller initialized (simulation mode)")
    
    async def set_pan_angle(self, angle: float) -> bool:
        """Simulate setting pan angle"""
        try:
            # Clamp angle to valid range
            angle = max(-90, min(90, angle))
            
            logger.info(f"Simulating pan to {angle} degrees")
            self.is_moving = True
            
            # Simulate movement time based on angle change
            angle_diff = abs(angle - self.pan_angle)
            movement_time = angle_diff / 90.0  # 1 second for 90 degrees
            
            await asyncio.sleep(max(0.1, movement_time))  # Minimum 0.1 second
            
            self.pan_angle = angle
            self.is_moving = False
            
            logger.info(f"Pan completed at {self.pan_angle}°")
            return True
            
        except Exception as e:
            logger.error(f"Error setting pan angle: {e}")
            self.is_moving = False
            return False
    
    async def set_tilt_angle(self, angle: float) -> bool:
        """Simulate setting tilt angle"""
        try:
            angle = max(-90, min(90, angle))
            
            logger.info(f"Simulating tilt to {angle} degrees")
            self.is_moving = True
            
            angle_diff = abs(angle - self.tilt_angle)
            movement_time = angle_diff / 90.0
            
            await asyncio.sleep(max(0.1, movement_time))
            
            self.tilt_angle = angle
            self.is_moving = False
            
            logger.info(f"Tilt completed at {self.tilt_angle}°")
            return True
            
        except Exception as e:
            logger.error(f"Error setting tilt angle: {e}")
            self.is_moving = False
            return False
    
    async def center_camera(self) -> bool:
        """Center both pan and tilt"""
        try:
            logger.info("Centering camera")
            
            pan_task = self.set_pan_angle(0.0)
            tilt_task = self.set_tilt_angle(0.0)
            
            results = await asyncio.gather(pan_task, tilt_task, return_exceptions=True)
            
            success = all(isinstance(result, bool) and result for result in results)
            
            if success:
                logger.info("Camera centered successfully")
            else:
                logger.error("Failed to center camera")
            
            return success
            
        except Exception as e:
            logger.error(f"Error centering camera: {e}")
            return False
    
    async def pan_left(self, degrees: float = 15) -> bool:
        """Pan camera left by specified degrees"""
        new_angle = self.pan_angle - degrees
        return await self.set_pan_angle(new_angle)
    
    async def pan_right(self, degrees: float = 15) -> bool:
        """Pan camera right by specified degrees"""
        new_angle = self.pan_angle + degrees
        return await self.set_pan_angle(new_angle)
    
    async def tilt_up(self, degrees: float = 15) -> bool:
        """Tilt camera up by specified degrees"""
        new_angle = self.tilt_angle + degrees
        return await self.set_tilt_angle(new_angle)
    
    async def tilt_down(self, degrees: float = 15) -> bool:
        """Tilt camera down by specified degrees"""
        new_angle = self.tilt_angle - degrees
        return await self.set_tilt_angle(new_angle)
    
    async def scan_area(self, scan_range: float = 60, steps: int = 5) -> bool:
        """Simulate scanning an area"""
        try:
            logger.info(f"Starting area scan: {scan_range}° range, {steps} steps")
            
            start_angle = self.pan_angle - scan_range / 2
            end_angle = self.pan_angle + scan_range / 2
            step_size = scan_range / (steps - 1) if steps > 1 else 0
            
            for i in range(steps):
                angle = start_angle + (step_size * i)
                await self.set_pan_angle(angle)
                await asyncio.sleep(0.5)  # Pause at each position
            
            # Return to original position
            await self.set_pan_angle(self.pan_angle)
            
            logger.info("Area scan completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during area scan: {e}")
            return False
    
    def get_camera_position(self) -> dict:
        """Get current camera position"""
        return {
            "pan_angle": self.pan_angle,
            "tilt_angle": self.tilt_angle,
            "is_moving": self.is_moving
        }
    
    def get_status(self) -> dict:
        """Get camera controller status"""
        return {
            "controller_type": "pure_simulation",
            "pan_angle": self.pan_angle,
            "tilt_angle": self.tilt_angle,
            "is_moving": self.is_moving,
            "pan_range": (-90, 90),
            "tilt_range": (-90, 90),
            "available_commands": [
                "center", "pan_left", "pan_right", "tilt_up", "tilt_down",
                "set_pan_angle", "set_tilt_angle", "scan_area"
            ],
            "status": "ready" if not self.is_moving else "moving",
            "note": "Simulation only - no hardware"
        }
    
    def cleanup(self):
        """Cleanup camera controller"""
        logger.info("Camera controller cleaned up")
