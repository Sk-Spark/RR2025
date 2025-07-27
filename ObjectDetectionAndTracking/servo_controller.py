"""
Ball Tracking Servo Controller
Controls pan and tilt servos for ball tracking using PCA9685 PWM driver
Based on proven implementation from Motors_Servo_POC
"""

import time
import threading
import logging
import config
from pca9685_controller import PCA9685Controller

logger = logging.getLogger(__name__)


class BallTrackingServoController:
    """
    Servo controller for ball tracking with pan and tilt servos
    Based on proven CameraPanTiltController implementation
    """
    
    def __init__(self):
        """Initialize servo controller with real PCA9685 hardware only"""
        # Initialize PCA9685 controller with real hardware
        self.pca = PCA9685Controller(
            i2c_address=config.PCA9685_ADDRESS, 
            frequency=config.PCA9685_FREQUENCY
        )
        logger.info("Servo controller initialized with PCA9685 hardware")
        
        # Servo configuration
        self.servos = {
            "pan": config.PAN_SERVO_CHANNEL,
            "tilt": config.TILT_SERVO_CHANNEL,
        }
        
        # Current positions
        self.current_positions = {
            "pan": config.PAN_CENTER_ANGLE,
            "tilt": config.TILT_CENTER_ANGLE
        }
        
        # Movement constraints
        self.pan_limits = (config.PAN_MIN_ANGLE, config.PAN_MAX_ANGLE)
        self.tilt_limits = (config.TILT_MIN_ANGLE, config.TILT_MAX_ANGLE)
        
        # Servo specifications for angle calculations
        self.servo_min_angle = 0
        self.servo_max_angle = 180
        self.servo_min_pulse = 500
        self.servo_max_pulse = 2500
        
        # Initialize servos to center position
        self.center_servos()
        
        logger.info(f"Servo controller initialized - Pan: CH{config.PAN_SERVO_CHANNEL}, Tilt: CH{config.TILT_SERVO_CHANNEL}")
    
    def angle_to_pulse_width(self, angle):
        """
        Convert angle to pulse width for SG90 servo
        
        Args:
            angle (int): Angle in degrees (0-180)
            
        Returns:
            int: Pulse width in microseconds
        """
        # Clamp angle between 0 and 180
        angle = max(self.servo_min_angle, min(self.servo_max_angle, angle))
        
        # Linear interpolation
        pulse_width = self.servo_min_pulse + (angle / self.servo_max_angle) * (self.servo_max_pulse - self.servo_min_pulse)
        
        return int(pulse_width)
    
    def pulse_width_to_duty_cycle(self, pulse_width):
        """
        Convert pulse width to PWM duty cycle
        
        Args:
            pulse_width (int): Pulse width in microseconds
            
        Returns:
            int: PWM duty cycle value (0-65535)
        """
        # Calculate duty cycle for 50Hz PWM (20ms period)
        period_us = 20000  # 20ms in microseconds
        duty_cycle = int((pulse_width / period_us) * 65535)
        
        return duty_cycle
    
    def set_servo_angle(self, servo_name, angle):
        """
        Set servo to specific angle
        
        Args:
            servo_name (str): Name of the servo ("pan" or "tilt")
            angle (int): Angle in degrees (0-180)
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        # Apply servo-specific limits
        if servo_name == "pan":
            angle = max(self.pan_limits[0], min(self.pan_limits[1], angle))
        elif servo_name == "tilt":
            angle = max(self.tilt_limits[0], min(self.tilt_limits[1], angle))
        
        # Store current position
        self.current_positions[servo_name] = angle
        
        # Use the PCA9685Controller's set_servo_angle method
        channel = self.servos[servo_name]
        self.pca.set_servo_angle(channel, angle)
        logger.debug(f"Servo {servo_name} set to {angle}° on channel {channel}")
    
    def smooth_move_servo(self, servo_name, target_angle, duration=1.0, easing="ease_in_out"):
        """
        Smoothly move servo to target angle with easing
        
        Args:
            servo_name (str): Name of the servo ("pan" or "tilt")
            target_angle (int): Target angle in degrees (0-180)
            duration (float): Duration of movement in seconds
            easing (str): Easing function ("linear", "ease_in", "ease_out", "ease_in_out")
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        # Get current position
        start_angle = self.current_positions[servo_name]
        
        # Apply servo-specific limits
        if servo_name == "pan":
            target_angle = max(self.pan_limits[0], min(self.pan_limits[1], target_angle))
        elif servo_name == "tilt":
            target_angle = max(self.tilt_limits[0], min(self.tilt_limits[1], target_angle))
        
        # Calculate movement parameters
        angle_diff = target_angle - start_angle
        
        if abs(angle_diff) < 1:  # Already close enough
            return
        
        # Movement parameters
        steps = max(20, int(abs(angle_diff) * 2))  # More steps for larger movements
        step_delay = duration / steps
        
        logger.debug(f"Smooth moving {servo_name} from {start_angle}° to {target_angle}° over {duration}s")
        
        for i in range(steps + 1):
            # Calculate progress (0.0 to 1.0)
            progress = i / steps
            
            # Apply easing function
            if easing == "linear":
                eased_progress = progress
            elif easing == "ease_in":
                eased_progress = self._ease_in(progress)
            elif easing == "ease_out":
                eased_progress = self._ease_out(progress)
            elif easing == "ease_in_out":
                eased_progress = self._ease_in_out(progress)
            else:
                eased_progress = progress  # Default to linear
            
            # Calculate current angle
            current_angle = start_angle + (angle_diff * eased_progress)
            
            # Set servo position
            angle = int(current_angle)
            if servo_name == "pan":
                angle = max(self.pan_limits[0], min(self.pan_limits[1], angle))
            elif servo_name == "tilt":
                angle = max(self.tilt_limits[0], min(self.tilt_limits[1], angle))
            
            pulse_width = self.angle_to_pulse_width(angle)
            duty_cycle = self.pulse_width_to_duty_cycle(pulse_width)
            
            channel = self.servos[servo_name]
            self.pca.set_pwm(channel, duty_cycle)
            self.current_positions[servo_name] = angle
            
            if i < steps:  # Don't delay after the last step
                time.sleep(step_delay)
        
        logger.debug(f"Servo {servo_name} smooth movement complete: {target_angle}°")
    
    def _ease_in(self, t):
        """Ease-in function (quadratic)"""
        return t * t
    
    def _ease_out(self, t):
        """Ease-out function (quadratic)"""
        return 1 - (1 - t) * (1 - t)
    
    def _ease_in_out(self, t):
        """Ease-in-out function (quadratic)"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - 2 * (1 - t) * (1 - t)
    
    def set_pan_angle(self, angle: float):
        """Set pan servo angle"""
        self.set_servo_angle("pan", int(angle))
    
    def set_tilt_angle(self, angle: float):
        """Set tilt servo angle"""
        self.set_servo_angle("tilt", int(angle))
    
    def set_pan_tilt(self, pan_angle: float, tilt_angle: float):
        """Set both pan and tilt angles"""
        self.set_pan_angle(pan_angle)
        self.set_tilt_angle(tilt_angle)
    
    def smooth_set_pan_tilt(self, pan_angle: float, tilt_angle: float, duration=1.0, easing="ease_in_out"):
        """
        Smoothly set camera position using both pan and tilt servos
        
        Args:
            pan_angle (float): Pan angle in degrees
            tilt_angle (float): Tilt angle in degrees
            duration (float): Duration of movement in seconds
            easing (str): Easing function type
        """
        # Move both servos simultaneously in separate threads
        def move_tilt():
            self.smooth_move_servo("tilt", int(tilt_angle), duration, easing)
        
        def move_pan():
            self.smooth_move_servo("pan", int(pan_angle), duration, easing)
        
        # Start both movements simultaneously
        tilt_thread = threading.Thread(target=move_tilt)
        pan_thread = threading.Thread(target=move_pan)
        
        tilt_thread.start()
        pan_thread.start()
        
        # Wait for both to complete
        tilt_thread.join()
        pan_thread.join()
    
    def center_servos(self):
        """Move servos to center position"""
        self.set_pan_angle(config.PAN_CENTER_ANGLE)
        self.set_tilt_angle(config.TILT_CENTER_ANGLE)
        logger.info("Servos centered")
    
    def get_current_position(self):
        """Get current servo positions"""
        return {
            "pan": self.current_positions["pan"],
            "tilt": self.current_positions["tilt"]
        }
    
    def get_status(self):
        """Get servo controller status"""
        return {
            "current_pan": self.current_positions["pan"],
            "current_tilt": self.current_positions["tilt"],
            "pan_limits": self.pan_limits,
            "tilt_limits": self.tilt_limits,
            "hardware_available": True
        }
    
    def stop_tracking_mode(self):
        """Stop tracking mode - placeholder for compatibility"""
        # This method is called by ball_tracker during cleanup
        # No special action needed for our servo controller
        pass
    
    def track_target(self, target_x: float, target_y: float, frame_width: int, frame_height: int):
        """
        Track a target by adjusting servo positions
        
        Args:
            target_x (float): Target X coordinate in frame
            target_y (float): Target Y coordinate in frame
            frame_width (int): Frame width in pixels
            frame_height (int): Frame height in pixels
        """
        # Calculate center offsets
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        error_x = target_x - center_x
        error_y = target_y - center_y
        
        # Check if target is within deadzone
        if abs(error_x) <= config.TRACKING_DEADZONE and abs(error_y) <= config.TRACKING_DEADZONE:
            logger.debug(f"Target in deadzone - no servo movement needed")
            return
        
        # Convert pixel errors to servo adjustments
        # Invert pan direction: if ball is right of center (positive error_x), 
        # camera should pan left (negative adjustment) to center the ball
        pan_adjustment = -(error_x / center_x) * config.PAN_SENSITIVITY
        tilt_adjustment = (error_y / center_y) * config.TILT_SENSITIVITY
        
        # Calculate new positions
        new_pan = self.current_positions["pan"] + pan_adjustment
        new_tilt = self.current_positions["tilt"] + tilt_adjustment  
        
        # Apply limits
        new_pan = max(self.pan_limits[0], min(self.pan_limits[1], new_pan))
        new_tilt = max(self.tilt_limits[0], min(self.tilt_limits[1], new_tilt))
        
        # Log the tracking movement
        logger.info(f"🎯 SERVO TRACKING: Target=({target_x:.0f},{target_y:.0f}) Error=({error_x:.1f},{error_y:.1f}) Pan: {self.current_positions['pan']:.1f}°→{new_pan:.1f}° Tilt: {self.current_positions['tilt']:.1f}°→{new_tilt:.1f}°")
        
        # Use smooth movement for more natural tracking
        if hasattr(config, 'TRACKING_SMOOTH_TIME'):
            self.smooth_set_pan_tilt(new_pan, new_tilt, duration=config.TRACKING_SMOOTH_TIME)
        else:
            self.set_pan_tilt(new_pan, new_tilt)
        
        logger.info(f"✅ SERVO MOVED: Pan={self.current_positions['pan']:.1f}° Tilt={self.current_positions['tilt']:.1f}°")
    
    def get_status(self):
        """Get servo controller status"""
        return {
            'current_pan': self.current_positions["pan"],
            'current_tilt': self.current_positions["tilt"],
            'pan_limits': self.pan_limits,
            'tilt_limits': self.tilt_limits,
            'tracking_active': True,  # Always active when system is running
            'hardware_available': True
        }
    
    def stop_tracking_mode(self):
        """Stop tracking mode (placeholder for compatibility)"""
        logger.debug("Stop tracking mode called")
        
    def cleanup(self):
        """Cleanup servo controller"""
        try:
            # Center servos before shutdown
            self.center_servos()
            time.sleep(0.5)
            logger.info("Servo controller cleanup complete")
        except Exception as e:
            logger.error(f"Error during servo cleanup: {e}")
