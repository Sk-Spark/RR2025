"""
Ball Tracking Servo Controller
Controls pan and tilt servos for ball tracking using PCA9685 PWM driver
Based on proven implementation from Motors_Servo_POC
"""

import time
import threading
import logging
import config

logger = logging.getLogger(__name__)

# Hardware dependencies - handle gracefully if not available
try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    HARDWARE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Hardware modules not available: {e}")
    HARDWARE_AVAILABLE = False


class PCA9685Controller:
    """Simple PCA9685 controller using direct I2C without gpiozero"""
    
    def __init__(self, i2c_address=0x40, frequency=50):
        """
        Initialize PCA9685 controller
        
        Args:
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            frequency (int): PWM frequency in Hz (default: 50Hz for servos)
        """
        if not HARDWARE_AVAILABLE:
            logger.warning("PCA9685 hardware not available, using mock controller")
            self.mock_mode = True
            return
        
        try:
            logger.info(f"Initializing PCA9685 at I2C address {hex(i2c_address)}...")
            
            # Initialize I2C bus directly
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685
            self.pca = PCA9685(self.i2c, address=i2c_address)
            self.pca.frequency = frequency
            
            self.mock_mode = False
            logger.info(f"PCA9685 initialized successfully at {frequency}Hz")
            
        except Exception as e:
            logger.error(f"Error initializing PCA9685: {e}")
            self.mock_mode = True
    
    def set_pwm(self, channel, duty_cycle):
        """
        Set PWM duty cycle for a channel
        
        Args:
            channel (int): PWM channel (0-15)
            duty_cycle (int): Duty cycle (0-65535)
        """
        if self.mock_mode:
            logger.debug(f"Mock PCA9685: Channel {channel} = {duty_cycle}")
            return
            
        try:
            self.pca.channels[channel].duty_cycle = duty_cycle
        except Exception as e:
            logger.error(f"Error setting PWM on channel {channel}: {e}")
            raise
    
    def get_pwm(self, channel):
        """
        Get PWM duty cycle for a channel
        
        Args:
            channel (int): PWM channel (0-15)
            
        Returns:
            int: Current duty cycle (0-65535)
        """
        if self.mock_mode:
            return 32768  # Mock value (50% duty cycle)
            
        try:
            return self.pca.channels[channel].duty_cycle
        except Exception as e:
            logger.error(f"Error getting PWM on channel {channel}: {e}")
            return 0


class BallTrackingServoController:
    """
    Servo controller for ball tracking with pan and tilt servos
    Based on proven CameraPanTiltController implementation
    """
    
    def __init__(self):
        """Initialize servo controller"""
        # Initialize PCA9685 controller
        self.pca = PCA9685Controller(
            i2c_address=config.I2C_ADDRESS, 
            frequency=config.PWM_FREQUENCY
        )
        
        # Servo configuration
        self.servos = {
            "pan": config.PAN_SERVO_CHANNEL,
            "tilt": config.TILT_SERVO_CHANNEL,
        }
        
        # SG90 servo specifications (from Motors_Servo_POC)
        self.servo_min_pulse = 500   # Minimum pulse width in microseconds
        self.servo_max_pulse = 2500  # Maximum pulse width in microseconds
        self.servo_min_angle = 0     # Minimum angle in degrees
        self.servo_max_angle = 180   # Maximum angle in degrees
        
        # Current positions
        self.current_positions = {
            "pan": config.PAN_CENTER_ANGLE,
            "tilt": config.TILT_CENTER_ANGLE
        }
        
        # Movement constraints
        self.pan_limits = (config.PAN_MIN_ANGLE, config.PAN_MAX_ANGLE)
        self.tilt_limits = (config.TILT_MIN_ANGLE, config.TILT_MAX_ANGLE)
        
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
        
        # Convert angle to pulse width and then to duty cycle
        pulse_width = self.angle_to_pulse_width(angle)
        duty_cycle = self.pulse_width_to_duty_cycle(pulse_width)
        
        # Set PWM
        channel = self.servos[servo_name]
        self.pca.set_pwm(channel, duty_cycle)
        
        # Store current position
        self.current_positions[servo_name] = angle
        
        logger.debug(f"Servo {servo_name}: Angle={angle}°, Pulse={pulse_width}μs, Duty={duty_cycle}")
    
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
        
        # Convert pixel errors to servo adjustments
        pan_adjustment = (error_x / center_x) * config.PAN_SENSITIVITY
        tilt_adjustment = (error_y / center_y) * config.TILT_SENSITIVITY
        
        # Calculate new positions
        new_pan = self.current_positions["pan"] + pan_adjustment
        new_tilt = self.current_positions["tilt"] - tilt_adjustment  # Invert for natural movement
        
        # Apply limits
        new_pan = max(self.pan_limits[0], min(self.pan_limits[1], new_pan))
        new_tilt = max(self.tilt_limits[0], min(self.tilt_limits[1], new_tilt))
        
        # Use smooth movement for more natural tracking
        if hasattr(config, 'TRACKING_SMOOTH_TIME'):
            self.smooth_set_pan_tilt(new_pan, new_tilt, duration=config.TRACKING_SMOOTH_TIME)
        else:
            self.set_pan_tilt(new_pan, new_tilt)
        
        logger.debug(f"Tracking: error=({error_x:.1f},{error_y:.1f}), new_pos=({new_pan:.1f},{new_tilt:.1f})")
    
    def cleanup(self):
        """Cleanup servo controller"""
        try:
            # Center servos before shutdown
            self.center_servos()
            time.sleep(0.5)
            logger.info("Servo controller cleanup complete")
        except Exception as e:
            logger.error(f"Error during servo cleanup: {e}")
