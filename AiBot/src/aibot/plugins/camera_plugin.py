#!/home/spark/RR2025/AiBot/venv/bin/python3
"""
Camera Control Plugin Module for AiBot
Semantic Kernel plugin for camera pan and tilt control
"""

import logging
import asyncio
from typing import Annotated

from semantic_kernel.functions import kernel_function
from ..hardware.camera_controller import CameraPanTiltController

logger = logging.getLogger(__name__)


class CameraControlPlugin:
    """Semantic Kernel plugin for camera pan and tilt control."""
    
    def __init__(self, camera_controller: CameraPanTiltController):
        """Initialize the camera control plugin with a controller."""
        self.camera_controller = camera_controller
    
    @kernel_function(
        description="Pan the camera to a specific angle (0-180 degrees)",
        name="pan_to_angle"
    )
    async def pan_to_angle(
        self, 
        angle: Annotated[int, "Pan angle in degrees (0-180)"] = 90
    ) -> Annotated[str, "Result of panning camera"]:
        """Pan the camera to a specific angle."""
        try:
            angle = max(0, min(180, int(angle)))  # Clamp angle between 0-180
            success = await asyncio.to_thread(self.camera_controller.set_servo_angle, "camera_pan", angle)
            
            if success:
                logger.info(f"Camera panned to {angle} degrees")
                return f"Camera panned to {angle} degrees successfully"
            else:
                logger.warning("Camera pan failed")
                return "Failed to pan camera"
        except Exception as e:
            logger.error(f"Error in pan_to_angle: {e}")
            return f"Error panning camera: {e}"
    
    @kernel_function(
        description="Tilt the camera to a specific angle (0-180 degrees)",
        name="tilt_to_angle"
    )
    async def tilt_to_angle(
        self, 
        angle: Annotated[int, "Tilt angle in degrees (0-180)"] = 90
    ) -> Annotated[str, "Result of tilting camera"]:
        """Tilt the camera to a specific angle."""
        try:
            angle = max(0, min(180, int(angle)))  # Clamp angle between 0-180
            success = await asyncio.to_thread(self.camera_controller.set_servo_angle, "camera_tilt", angle)
            
            if success:
                logger.info(f"Camera tilted to {angle} degrees")
                return f"Camera tilted to {angle} degrees successfully"
            else:
                logger.warning("Camera tilt failed")
                return "Failed to tilt camera"
        except Exception as e:
            logger.error(f"Error in tilt_to_angle: {e}")
            return f"Error tilting camera: {e}"
    
    @kernel_function(
        description="Pan the camera by a relative amount (positive = right, negative = left)",
        name="pan_relative"
    )
    async def pan_relative(
        self, 
        degrees: Annotated[int, "Degrees to pan (positive=right, negative=left)"] = 10
    ) -> Annotated[str, "Result of relative pan"]:
        """Pan the camera by a relative amount."""
        try:
            degrees = max(-180, min(180, int(degrees)))  # Clamp between -180 and 180
            current_angle = self.camera_controller.get_servo_angle("camera_pan")
            new_angle = max(0, min(180, current_angle + degrees))
            success = await asyncio.to_thread(self.camera_controller.set_servo_angle, "camera_pan", new_angle)
            
            if success:
                direction = "right" if degrees > 0 else "left"
                logger.info(f"Camera panned {abs(degrees)} degrees {direction}")
                return f"Camera panned {abs(degrees)} degrees {direction} successfully"
            else:
                logger.warning("Camera relative pan failed")
                return "Failed to pan camera relatively"
        except Exception as e:
            logger.error(f"Error in pan_relative: {e}")
            return f"Error in relative pan: {e}"
    
    @kernel_function(
        description="Tilt the camera by a relative amount (positive = up, negative = down)",
        name="tilt_relative"
    )
    async def tilt_relative(
        self, 
        degrees: Annotated[int, "Degrees to tilt (positive=up, negative=down)"] = 10
    ) -> Annotated[str, "Result of relative tilt"]:
        """Tilt the camera by a relative amount."""
        try:
            degrees = max(-180, min(180, int(degrees)))  # Clamp between -180 and 180
            current_angle = self.camera_controller.get_servo_angle("camera_tilt")
            new_angle = max(0, min(180, current_angle + degrees))
            success = await asyncio.to_thread(self.camera_controller.set_servo_angle, "camera_tilt", new_angle)
            
            if success:
                direction = "up" if degrees > 0 else "down"
                logger.info(f"Camera tilted {abs(degrees)} degrees {direction}")
                return f"Camera tilted {abs(degrees)} degrees {direction} successfully"
            else:
                logger.warning("Camera relative tilt failed")
                return "Failed to tilt camera relatively"
        except Exception as e:
            logger.error(f"Error in tilt_relative: {e}")
            return f"Error in relative tilt: {e}"
    
    @kernel_function(
        description="Set both pan and tilt angles simultaneously",
        name="set_camera_position"
    )
    async def set_camera_position(
        self, 
        pan_angle: Annotated[int, "Pan angle in degrees (0-180)"] = 90,
        tilt_angle: Annotated[int, "Tilt angle in degrees (0-180)"] = 90
    ) -> Annotated[str, "Result of setting camera position"]:
        """Set both pan and tilt angles simultaneously."""
        try:
            pan_angle = max(0, min(180, int(pan_angle)))
            tilt_angle = max(0, min(180, int(tilt_angle)))
            
            success = await asyncio.to_thread(
                self.camera_controller.set_camera_position, 
                tilt_angle, 
                pan_angle
            )
            
            if success:
                logger.info(f"Camera positioned to pan={pan_angle}°, tilt={tilt_angle}°")
                return f"Camera positioned to pan={pan_angle}°, tilt={tilt_angle}° successfully"
            else:
                logger.warning("Camera positioning failed")
                return "Failed to position camera"
        except Exception as e:
            logger.error(f"Error in set_camera_position: {e}")
            return f"Error positioning camera: {e}"
    
    @kernel_function(
        description="Center the camera to default position (90° pan, 90° tilt)",
        name="center_camera"
    )
    async def center_camera(self) -> Annotated[str, "Result of centering camera"]:
        """Center the camera to default position."""
        try:
            success = await asyncio.to_thread(self.camera_controller.center_all_servos)
            
            if success:
                logger.info("Camera centered to default position")
                return "Camera centered to default position (90°, 90°) successfully"
            else:
                logger.warning("Camera centering failed")
                return "Failed to center camera"
        except Exception as e:
            logger.error(f"Error in center_camera: {e}")
            return f"Error centering camera: {e}"
    
    @kernel_function(
        description="Perform a smooth pan sweep from left to right",
        name="pan_sweep"
    )
    async def pan_sweep(
        self, 
        start_angle: Annotated[int, "Starting pan angle (0-180)"] = 30,
        end_angle: Annotated[int, "Ending pan angle (0-180)"] = 150,
        duration: Annotated[float, "Duration in seconds (1-10)"] = 3.0
    ) -> Annotated[str, "Result of pan sweep"]:
        """Perform a smooth pan sweep between two angles."""
        try:
            start_angle = max(0, min(180, int(start_angle)))
            end_angle = max(0, min(180, int(end_angle)))
            duration = max(1.0, min(10.0, float(duration)))
            
            success = await asyncio.to_thread(
                self.camera_controller.sweep_horizontal,
                1.0,  # speed
                abs(end_angle - start_angle)  # range
            )
            
            if success:
                logger.info(f"Pan sweep completed from {start_angle}° to {end_angle}°")
                return f"Pan sweep completed from {start_angle}° to {end_angle}° in {duration} seconds"
            else:
                logger.warning("Pan sweep failed")
                return "Failed to perform pan sweep"
        except Exception as e:
            logger.error(f"Error in pan_sweep: {e}")
            return f"Error in pan sweep: {e}"
    
    @kernel_function(
        description="Perform a smooth tilt sweep from bottom to top",
        name="tilt_sweep"
    )
    async def tilt_sweep(
        self, 
        start_angle: Annotated[int, "Starting tilt angle (0-180)"] = 60,
        end_angle: Annotated[int, "Ending tilt angle (0-180)"] = 120,
        duration: Annotated[float, "Duration in seconds (1-10)"] = 3.0
    ) -> Annotated[str, "Result of tilt sweep"]:
        """Perform a smooth tilt sweep between two angles."""
        try:
            start_angle = max(0, min(180, int(start_angle)))
            end_angle = max(0, min(180, int(end_angle)))
            duration = max(1.0, min(10.0, float(duration)))
            
            success = await asyncio.to_thread(
                self.camera_controller.sweep_vertical,
                1.0,  # speed
                abs(end_angle - start_angle)  # range
            )
            
            if success:
                logger.info(f"Tilt sweep completed from {start_angle}° to {end_angle}°")
                return f"Tilt sweep completed from {start_angle}° to {end_angle}° in {duration} seconds"
            else:
                logger.warning("Tilt sweep failed")
                return "Failed to perform tilt sweep"
        except Exception as e:
            logger.error(f"Error in tilt_sweep: {e}")
            return f"Error in tilt sweep: {e}"
    
    @kernel_function(
        description="Perform a security scan by scanning nearby surrounding area (360° pan sweep with tilt adjustments)",
        name="security_scan"
    )
    async def security_scan(
        self, 
        scan_speed: Annotated[str, "Scan speed: 'slow', 'normal', or 'fast'"] = "normal"
    ) -> Annotated[str, "Result of security scan"]:
        """Perform a security scan pattern."""
        try:
            # Map speed to speed value
            speed_map = {
                "slow": 0.5,
                "normal": 1.0,
                "fast": 2.0
            }
            speed = speed_map.get(scan_speed.lower(), 1.0)
            
            # Perform horizontal sweep as security scan
            success = await asyncio.to_thread(
                self.camera_controller.sweep_horizontal,
                speed,
                120  # wide range for security
            )
            
            if success:
                logger.info(f"Security scan completed at {scan_speed} speed")
                return f"Security scan completed at {scan_speed} speed successfully"
            else:
                logger.warning("Security scan failed")
                return "Failed to perform security scan"
        except Exception as e:
            logger.error(f"Error in security_scan: {e}")
            return f"Error in security scan: {e}"
    
    @kernel_function(
        description="Get the current camera position (pan and tilt angles)",
        name="get_camera_position"
    )
    def get_camera_position(self) -> Annotated[str, "Current camera position"]:
        """Get the current camera position."""
        try:
            position = self.camera_controller.get_camera_position()
            pan_angle = position.get('camera_pan', 'unknown')
            tilt_angle = position.get('camera_tilt', 'unknown')
            
            logger.info(f"Camera position: pan={pan_angle}°, tilt={tilt_angle}°")
            return f"Camera position: pan={pan_angle}°, tilt={tilt_angle}°"
        except Exception as e:
            logger.error(f"Error in get_camera_position: {e}")
            return f"Error getting camera position: {e}"
    
    @kernel_function(
        description="Track a target by adjusting camera position smoothly",
        name="track_target"
    )
    async def track_target(
        self, 
        target_pan: Annotated[int, "Target pan angle (0-180)"] = 90,
        target_tilt: Annotated[int, "Target tilt angle (0-180)"] = 90,
        tracking_speed: Annotated[str, "Tracking speed: 'slow', 'normal', or 'fast'"] = "normal"
    ) -> Annotated[str, "Result of target tracking"]:
        """Track a target by smoothly adjusting camera position."""
        try:
            target_pan = max(0, min(180, int(target_pan)))
            target_tilt = max(0, min(180, int(target_tilt)))
            
            # Map speed to duration
            speed_map = {
                "slow": 2.0,
                "normal": 1.0,
                "fast": 0.5
            }
            duration = speed_map.get(tracking_speed.lower(), 1.0)
            
            success = await asyncio.to_thread(
                self.camera_controller.smooth_set_camera_position,
                target_tilt,
                target_pan,
                duration
            )
            
            if success:
                logger.info(f"Target tracked to pan={target_pan}°, tilt={target_tilt}°")
                return f"Target tracked to pan={target_pan}°, tilt={target_tilt}° at {tracking_speed} speed"
            else:
                logger.warning("Target tracking failed")
                return "Failed to track target"
        except Exception as e:
            logger.error(f"Error in track_target: {e}")
            return f"Error tracking target: {e}"
    
    @kernel_function(
        description="Look up with the camera",
        name="look_up"
    )
    async def look_up(
        self, 
        angle: Annotated[int, "Angle to look up (degrees)"] = 45
    ) -> Annotated[str, "Result of looking up"]:
        """Look up with the camera."""
        try:
            angle = max(0, min(90, int(angle)))  # Clamp angle
            success = await asyncio.to_thread(self.camera_controller.look_up, angle)
            
            if success:
                logger.info(f"Camera looked up by {angle} degrees")
                return f"Camera looked up by {angle} degrees successfully"
            else:
                logger.warning("Look up failed")
                return "Failed to look up"
        except Exception as e:
            logger.error(f"Error in look_up: {e}")
            return f"Error looking up: {e}"
    
    @kernel_function(
        description="Look down with the camera",
        name="look_down"
    )
    async def look_down(
        self, 
        angle: Annotated[int, "Angle to look down (degrees)"] = 45
    ) -> Annotated[str, "Result of looking down"]:
        """Look down with the camera."""
        try:
            angle = max(0, min(90, int(angle)))  # Clamp angle
            success = await asyncio.to_thread(self.camera_controller.look_down, angle)
            
            if success:
                logger.info(f"Camera looked down by {angle} degrees")
                return f"Camera looked down by {angle} degrees successfully"
            else:
                logger.warning("Look down failed")
                return "Failed to look down"
        except Exception as e:
            logger.error(f"Error in look_down: {e}")
            return f"Error looking down: {e}"
    
    @kernel_function(
        description="Look left with the camera",
        name="look_left"
    )
    async def look_left(
        self, 
        angle: Annotated[int, "Angle to look left (degrees)"] = 45
    ) -> Annotated[str, "Result of looking left"]:
        """Look left with the camera."""
        try:
            angle = max(0, min(90, int(angle)))  # Clamp angle
            success = await asyncio.to_thread(self.camera_controller.look_left, angle)
            
            if success:
                logger.info(f"Camera looked left by {angle} degrees")
                return f"Camera looked left by {angle} degrees successfully"
            else:
                logger.warning("Look left failed")
                return "Failed to look left"
        except Exception as e:
            logger.error(f"Error in look_left: {e}")
            return f"Error looking left: {e}"
    
    @kernel_function(
        description="Look right with the camera",
        name="look_right"
    )
    async def look_right(
        self, 
        angle: Annotated[int, "Angle to look right (degrees)"] = 45
    ) -> Annotated[str, "Result of looking right"]:
        """Look right with the camera."""
        try:
            angle = max(0, min(90, int(angle)))  # Clamp angle
            success = await asyncio.to_thread(self.camera_controller.look_right, angle)
            
            if success:
                logger.info(f"Camera looked right by {angle} degrees")
                return f"Camera looked right by {angle} degrees successfully"
            else:
                logger.warning("Look right failed")
                return "Failed to look right"
        except Exception as e:
            logger.error(f"Error in look_right: {e}")
            return f"Error looking right: {e}"
