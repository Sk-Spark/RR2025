#!/usr/bin/env python3
"""
Camera Pan-Tilt Controller Plugin for AiBot
Provides servo control for camera pan and tilt movements using PCA9685 PWM driver
"""

import time
import logging
import threading
from typing import Optional, Dict, Any
from .pca9685_controller import PCA9685Controller

logger = logging.getLogger(__name__)


class CameraPanTiltController:
    """
    Advanced camera pan-tilt controller for AiBot using SG90 servos
    Provides smooth movements, positioning, and camera control capabilities
    """
    
    def __init__(self, pca_controller: Optional[PCA9685Controller] = None, servo_config: Optional[Dict[str, int]] = None):
        """
        Initialize camera pan-tilt controller
        
        Args:
            pca_controller: Instance of PCA9685Controller (will create if None)
            servo_config: Servo configuration dictionary with channel mappings
        """
        # Initialize PCA9685 controller if not provided
        if pca_controller is None:
            self.pca = PCA9685Controller()
        else:
            self.pca = pca_controller
        
        # Default servo configuration for AiBot
        self.servos = servo_config or {
            "camera_tilt": 3,  # Tilt servo on channel 3
            "camera_pan": 2,   # Pan servo on channel 2
        }
        
        # SG90 servo specifications
        self.servo_min_pulse = 500   # Minimum pulse width in microseconds
        self.servo_max_pulse = 2500  # Maximum pulse width in microseconds
        self.servo_min_angle = 0     # Minimum angle in degrees
        self.servo_max_angle = 180   # Maximum angle in degrees
        
        # Current positions tracking
        self.current_positions = {}
        
        # Movement limits for safety (prevent mechanical stress)
        self.movement_limits = {
            "camera_tilt": {"min": 30, "max": 150},  # Prevent over-rotation
            "camera_pan": {"min": 30, "max": 150}   # Prevent over-rotation
        }
        
        # Initialize servos to center position
        self.center_all_servos()
        
        logger.info(f"Camera pan-tilt controller initialized with {len(self.servos)} servos")
    
    def angle_to_pulse_width(self, angle: float) -> int:
        """
        Convert angle to pulse width for SG90 servo
        
        Args:
            angle: Angle in degrees (0-180)
            
        Returns:
            Pulse width in microseconds
        """
        # Clamp angle between servo limits
        angle = max(self.servo_min_angle, min(self.servo_max_angle, angle))
        
        # Linear interpolation between min and max pulse widths
        pulse_width = self.servo_min_pulse + (angle / self.servo_max_angle) * (self.servo_max_pulse - self.servo_min_pulse)
        
        return int(pulse_width)
    
    def pulse_width_to_duty_cycle(self, pulse_width: int) -> int:
        """
        Convert pulse width to PWM duty cycle
        
        Args:
            pulse_width: Pulse width in microseconds
            
        Returns:
            PWM duty cycle value (0-65535)
        """
        # Calculate duty cycle for 50Hz PWM (20ms period)
        period_us = 20000  # 20ms in microseconds
        duty_cycle = int((pulse_width / period_us) * 65535)
        
        return duty_cycle
    
    def set_servo_angle(self, servo_name: str, angle: float) -> bool:
        """
        Set servo to specific angle with safety limits
        
        Args:
            servo_name: Name of the servo from config
            angle: Angle in degrees (0-180)
            
        Returns:
            Success status
        """
        if servo_name not in self.servos:
            logger.error(f"Servo {servo_name} not found in configuration")
            return False
        
        try:
            # Apply movement limits for safety
            if servo_name in self.movement_limits:
                limits = self.movement_limits[servo_name]
                angle = max(limits["min"], min(limits["max"], angle))
            else:
                # Use global servo limits
                angle = max(self.servo_min_angle, min(self.servo_max_angle, angle))
            
            # Convert angle to pulse width and then to duty cycle
            pulse_width = self.angle_to_pulse_width(angle)
            duty_cycle = self.pulse_width_to_duty_cycle(pulse_width)
            
            # Set PWM
            channel = self.servos[servo_name]
            self.pca.set_pwm(channel, duty_cycle)
            
            # Store current position
            self.current_positions[servo_name] = angle
            
            logger.debug(f"Servo {servo_name}: Angle={angle}°, Pulse={pulse_width}μs, Duty={duty_cycle}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set servo angle for {servo_name}: {e}")
            return False
    
    def get_servo_angle(self, servo_name: str) -> float:
        """
        Get current servo angle
        
        Args:
            servo_name: Name of the servo from config
            
        Returns:
            Current angle in degrees (default 90° if not set)
        """
        if servo_name not in self.servos:
            logger.error(f"Servo {servo_name} not found in configuration")
            return 90.0
        
        return self.current_positions.get(servo_name, 90.0)
    
    def smooth_move_servo(self, servo_name: str, target_angle: float, duration: float = 1.0, easing: str = "ease_in_out") -> bool:
        """
        Smoothly move servo to target angle with easing
        
        Args:
            servo_name: Name of the servo from config
            target_angle: Target angle in degrees
            duration: Duration of movement in seconds
            easing: Easing function ("linear", "ease_in", "ease_out", "ease_in_out")
            
        Returns:
            Success status
        """
        if servo_name not in self.servos:
            logger.error(f"Servo {servo_name} not found in configuration")
            return False
        
        try:
            # Get current position
            start_angle = self.get_servo_angle(servo_name)
            
            # Apply movement limits
            if servo_name in self.movement_limits:
                limits = self.movement_limits[servo_name]
                target_angle = max(limits["min"], min(limits["max"], target_angle))
            
            # Calculate movement parameters
            angle_diff = target_angle - start_angle
            
            if abs(angle_diff) < 1:  # Already close enough
                return True
            
            # Movement parameters
            steps = max(20, int(abs(angle_diff) * 2))  # More steps for larger movements
            step_delay = duration / steps
            
            logger.info(f"Smooth moving {servo_name} from {start_angle}° to {target_angle}° over {duration}s")
            
            for i in range(steps + 1):
                # Calculate progress (0.0 to 1.0)
                progress = i / steps
                
                # Apply easing function
                eased_progress = self._apply_easing(progress, easing)
                
                # Calculate current angle
                current_angle = start_angle + (angle_diff * eased_progress)
                
                # Set servo position
                if not self.set_servo_angle(servo_name, current_angle):
                    return False
                
                if i < steps:  # Don't delay after the last step
                    time.sleep(step_delay)
            
            logger.info(f"Servo {servo_name} smooth movement complete: {target_angle}°")
            return True
            
        except Exception as e:
            logger.error(f"Failed to smoothly move servo {servo_name}: {e}")
            return False
    
    def _apply_easing(self, t: float, easing: str) -> float:
        """Apply easing function to progress value"""
        if easing == "linear":
            return t
        elif easing == "ease_in":
            return t * t
        elif easing == "ease_out":
            return 1 - (1 - t) * (1 - t)
        elif easing == "ease_in_out":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:
            return t  # Default to linear
    
    def set_camera_position(self, tilt_angle: float = 90, pan_angle: float = 90, smooth: bool = False, duration: float = 1.0) -> bool:
        """
        Set camera position using both tilt and pan servos
        
        Args:
            tilt_angle: Tilt angle in degrees
            pan_angle: Pan angle in degrees
            smooth: Whether to use smooth movement
            duration: Duration of smooth movement in seconds
            
        Returns:
            Success status
        """
        try:
            if smooth:
                return self.smooth_set_camera_position(tilt_angle, pan_angle, duration)
            else:
                success = True
                if "camera_tilt" in self.servos:
                    success &= self.set_servo_angle("camera_tilt", tilt_angle)
                
                if "camera_pan" in self.servos:
                    success &= self.set_servo_angle("camera_pan", pan_angle)
                
                if success:
                    logger.info(f"Camera position set: Tilt={tilt_angle}°, Pan={pan_angle}°")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to set camera position: {e}")
            return False
    
    def smooth_set_camera_position(self, tilt_angle: float = 90, pan_angle: float = 90, duration: float = 1.0, easing: str = "ease_in_out") -> bool:
        """
        Smoothly set camera position using both servos simultaneously
        
        Args:
            tilt_angle: Tilt angle in degrees
            pan_angle: Pan angle in degrees
            duration: Duration of movement in seconds
            easing: Easing function type
            
        Returns:
            Success status
        """
        try:
            results = {"tilt": True, "pan": True}
            
            def move_tilt():
                if "camera_tilt" in self.servos:
                    results["tilt"] = self.smooth_move_servo("camera_tilt", tilt_angle, duration, easing)
            
            def move_pan():
                if "camera_pan" in self.servos:
                    results["pan"] = self.smooth_move_servo("camera_pan", pan_angle, duration, easing)
            
            # Start both movements simultaneously
            tilt_thread = threading.Thread(target=move_tilt)
            pan_thread = threading.Thread(target=move_pan)
            
            tilt_thread.start()
            pan_thread.start()
            
            # Wait for both to complete
            tilt_thread.join()
            pan_thread.join()
            
            success = results["tilt"] and results["pan"]
            if success:
                logger.info(f"Camera position smoothly set: Tilt={tilt_angle}°, Pan={pan_angle}°")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to smoothly set camera position: {e}")
            return False
    
    def get_camera_position(self) -> Dict[str, float]:
        """
        Get current camera position
        
        Returns:
            Dictionary with current tilt and pan angles
        """
        return {
            "tilt": self.get_servo_angle("camera_tilt"),
            "pan": self.get_servo_angle("camera_pan")
        }
    
    def center_all_servos(self) -> bool:
        """
        Center all servos to 90 degrees
        
        Returns:
            Success status
        """
        try:
            success = True
            for servo_name in self.servos:
                success &= self.set_servo_angle(servo_name, 90)
            
            if success:
                logger.info("All camera servos centered")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to center servos: {e}")
            return False
    
    def look_up(self, angle: float = 45, smooth: bool = True, duration: float = 0.8) -> bool:
        """
        Tilt camera up by specified angle from center
        
        Args:
            angle: Angle above center (0-60)
            smooth: Whether to use smooth movement
            duration: Duration of smooth movement in seconds
            
        Returns:
            Success status
        """
        # Calculate tilt angle (subtract from 90 for up movement)
        tilt_angle = 90 - min(60, max(0, angle))
        
        if smooth:
            success = self.smooth_move_servo("camera_tilt", tilt_angle, duration)
        else:
            success = self.set_servo_angle("camera_tilt", tilt_angle)
        
        if success:
            logger.info(f"Camera looking up at {angle}° above center")
        
        return success
    
    def look_down(self, angle: float = 45, smooth: bool = True, duration: float = 0.8) -> bool:
        """
        Tilt camera down by specified angle from center
        
        Args:
            angle: Angle below center (0-60)
            smooth: Whether to use smooth movement
            duration: Duration of smooth movement in seconds
            
        Returns:
            Success status
        """
        # Calculate tilt angle (add to 90 for down movement)
        tilt_angle = 90 + min(60, max(0, angle))
        
        if smooth:
            success = self.smooth_move_servo("camera_tilt", tilt_angle, duration)
        else:
            success = self.set_servo_angle("camera_tilt", tilt_angle)
        
        if success:
            logger.info(f"Camera looking down at {angle}° below center")
        
        return success
    
    def look_left(self, angle: float = 45, smooth: bool = True, duration: float = 0.8) -> bool:
        """
        Pan camera left by specified angle from center
        
        Args:
            angle: Angle left of center (0-60)
            smooth: Whether to use smooth movement
            duration: Duration of smooth movement in seconds
            
        Returns:
            Success status
        """
        # Calculate pan angle (add to 90 for left movement)
        pan_angle = 90 + min(60, max(0, angle))
        
        if smooth:
            success = self.smooth_move_servo("camera_pan", pan_angle, duration)
        else:
            success = self.set_servo_angle("camera_pan", pan_angle)
        
        if success:
            logger.info(f"Camera looking left at {angle}° from center")
        
        return success
    
    def look_right(self, angle: float = 45, smooth: bool = True, duration: float = 0.8) -> bool:
        """
        Pan camera right by specified angle from center
        
        Args:
            angle: Angle right of center (0-60)
            smooth: Whether to use smooth movement
            duration: Duration of smooth movement in seconds
            
        Returns:
            Success status
        """
        # Calculate pan angle (subtract from 90 for right movement)
        pan_angle = 90 - min(60, max(0, angle))
        
        if smooth:
            success = self.smooth_move_servo("camera_pan", pan_angle, duration)
        else:
            success = self.set_servo_angle("camera_pan", pan_angle)
        
        if success:
            logger.info(f"Camera looking right at {angle}° from center")
        
        return success
    
    def sweep_horizontal(self, speed: float = 1.0, range_angle: float = 60) -> bool:
        """
        Sweep camera horizontally (pan left to right and back)
        
        Args:
            speed: Sweep speed (lower = slower)
            range_angle: Total sweep range from center (0-60)
            
        Returns:
            Success status
        """
        try:
            duration = 1.0 / speed
            range_angle = min(60, max(10, range_angle))
            
            # Sweep right
            if not self.look_right(range_angle, smooth=True, duration=duration):
                return False
            
            # Sweep left
            if not self.look_left(range_angle, smooth=True, duration=duration * 2):
                return False
            
            # Return to center
            if not self.set_servo_angle("camera_pan", 90):
                return False
            
            logger.info(f"Horizontal sweep completed with {range_angle}° range")
            return True
            
        except Exception as e:
            logger.error(f"Failed to perform horizontal sweep: {e}")
            return False
    
    def sweep_vertical(self, speed: float = 1.0, range_angle: float = 45) -> bool:
        """
        Sweep camera vertically (tilt up to down and back)
        
        Args:
            speed: Sweep speed (lower = slower)
            range_angle: Total sweep range from center (0-45)
            
        Returns:
            Success status
        """
        try:
            duration = 1.0 / speed
            range_angle = min(45, max(10, range_angle))
            
            # Sweep up
            if not self.look_up(range_angle, smooth=True, duration=duration):
                return False
            
            # Sweep down
            if not self.look_down(range_angle, smooth=True, duration=duration * 2):
                return False
            
            # Return to center
            if not self.set_servo_angle("camera_tilt", 90):
                return False
            
            logger.info(f"Vertical sweep completed with {range_angle}° range")
            return True
            
        except Exception as e:
            logger.error(f"Failed to perform vertical sweep: {e}")
            return False
    
    def disable_servos(self) -> bool:
        """
        Disable all servos by setting PWM to 0
        
        Returns:
            Success status
        """
        try:
            for servo_name, channel in self.servos.items():
                self.pca.set_pwm(channel, 0)
            
            logger.info("All camera servos disabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable servos: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of camera pan-tilt system
        
        Returns:
            Status dictionary with all servo information
        """
        try:
            status = {
                "servos": {},
                "camera_position": self.get_camera_position(),
                "movement_limits": self.movement_limits,
                "servo_count": len(self.servos)
            }
            
            for servo_name, channel in self.servos.items():
                status["servos"][servo_name] = {
                    "channel": channel,
                    "current_angle": self.get_servo_angle(servo_name),
                    "limits": self.movement_limits.get(servo_name, {"min": 0, "max": 180})
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get camera status: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Clean up camera controller resources"""
        try:
            # Center servos before cleanup
            self.center_all_servos()
            time.sleep(0.5)
            
            # Disable servos
            self.disable_servos()
            
            logger.info("Camera pan-tilt controller cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during camera controller cleanup: {e}")
