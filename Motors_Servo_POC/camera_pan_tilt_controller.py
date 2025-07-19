"""
Camera Pan-Tilt Controller Module
Class for controlling SG90 servos for camera pan and tilt using PCA9685 PWM driver with GPIO Zero
"""

import time
from pca9685_controller_gpiozero import PCA9685Controller


class CameraPanTiltController:
    """Controller for SG90 servos for camera pan and tilt using PCA9685"""
    
    def __init__(self, pca_controller, servo_config):
        """
        Initialize servo controller
        
        Args:
            pca_controller (PCA9685Controller): Instance of PCA9685Controller
            servo_config (dict): Servo configuration dictionary
        """
        self.pca = pca_controller
        self.servos = servo_config
        
        # SG90 servo specifications
        self.servo_min_pulse = 500   # Minimum pulse width in microseconds
        self.servo_max_pulse = 2500  # Maximum pulse width in microseconds
        self.servo_min_angle = 0     # Minimum angle in degrees
        self.servo_max_angle = 180   # Maximum angle in degrees
        
        # Current positions
        self.current_positions = {}
        
        # Initialize servos to center position
        self.center_all_servos()
        
        print(f"Camera Pan-Tilt controller initialized with {len(self.servos)} servos")
    
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
            servo_name (str): Name of the servo from config
            angle (int): Angle in degrees (0-180)
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        # Clamp angle
        angle = max(self.servo_min_angle, min(self.servo_max_angle, angle))
        
        # Convert angle to pulse width and then to duty cycle
        pulse_width = self.angle_to_pulse_width(angle)
        duty_cycle = self.pulse_width_to_duty_cycle(pulse_width)
        
        # Set PWM
        channel = self.servos[servo_name]
        self.pca.set_pwm(channel, duty_cycle)
        
        # Store current position
        self.current_positions[servo_name] = angle
        
        print(f"Servo {servo_name}: Angle={angle}°, Pulse={pulse_width}μs, Duty={duty_cycle}")
    
    def smooth_move_servo(self, servo_name, target_angle, duration=1.0, easing="ease_in_out"):
        """
        Smoothly move servo to target angle with easing
        
        Args:
            servo_name (str): Name of the servo from config
            target_angle (int): Target angle in degrees (0-180)
            duration (float): Duration of movement in seconds
            easing (str): Easing function ("linear", "ease_in", "ease_out", "ease_in_out")
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        # Get current position
        start_angle = self.get_servo_angle(servo_name)
        target_angle = max(self.servo_min_angle, min(self.servo_max_angle, target_angle))
        
        # Calculate movement parameters
        angle_diff = target_angle - start_angle
        
        if abs(angle_diff) < 1:  # Already close enough
            return
        
        # Movement parameters
        steps = max(20, int(abs(angle_diff) * 2))  # More steps for larger movements
        step_delay = duration / steps
        
        print(f"Smooth moving {servo_name} from {start_angle}° to {target_angle}° over {duration}s")
        
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
            
            # Set servo position (without printing to reduce spam)
            angle = max(self.servo_min_angle, min(self.servo_max_angle, int(current_angle)))
            pulse_width = self.angle_to_pulse_width(angle)
            duty_cycle = self.pulse_width_to_duty_cycle(pulse_width)
            
            channel = self.servos[servo_name]
            self.pca.set_pwm(channel, duty_cycle)
            self.current_positions[servo_name] = angle
            
            if i < steps:  # Don't delay after the last step
                time.sleep(step_delay)
        
        print(f"Servo {servo_name} smooth movement complete: {target_angle}°")
    
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
    
    def smooth_set_camera_position(self, tilt_angle=90, pan_angle=90, duration=1.0, easing="ease_in_out"):
        """
        Smoothly set camera position using both tilt and pan servos
        
        Args:
            tilt_angle (int): Tilt angle in degrees (0-180)
            pan_angle (int): Pan angle in degrees (0-180)
            duration (float): Duration of movement in seconds
            easing (str): Easing function type
        """
        # Move both servos simultaneously in separate threads
        import threading
        
        def move_tilt():
            if "camera_tilt" in self.servos:
                self.smooth_move_servo("camera_tilt", tilt_angle, duration, easing)
        
        def move_pan():
            if "camera_pan" in self.servos:
                self.smooth_move_servo("camera_pan", pan_angle, duration, easing)
        
        # Start both movements simultaneously
        tilt_thread = threading.Thread(target=move_tilt)
        pan_thread = threading.Thread(target=move_pan)
        
        tilt_thread.start()
        pan_thread.start()
        
        # Wait for both to complete
        tilt_thread.join()
        pan_thread.join()
        
        print(f"Camera position smoothly set: Tilt={tilt_angle}°, Pan={pan_angle}°")
    
    def get_servo_angle(self, servo_name):
        """
        Get current servo angle
        
        Args:
            servo_name (str): Name of the servo from config
            
        Returns:
            int: Current angle in degrees
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        return self.current_positions.get(servo_name, 90)  # Default to 90° if not set
    
    def center_servo(self, servo_name):
        """
        Center a specific servo (90 degrees)
        
        Args:
            servo_name (str): Name of the servo from config
        """
        self.set_servo_angle(servo_name, 90)
        print(f"Servo {servo_name} centered")
    
    def center_all_servos(self):
        """Center all servos"""
        for servo_name in self.servos:
            self.center_servo(servo_name)
        print("All servos centered")
    
    def sweep_servo(self, servo_name, start_angle=0, end_angle=180, steps=10, delay=0.1):
        """
        Sweep servo from start to end angle
        
        Args:
            servo_name (str): Name of the servo from config
            start_angle (int): Starting angle in degrees
            end_angle (int): Ending angle in degrees
            steps (int): Number of steps in the sweep
            delay (float): Delay between steps in seconds
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        print(f"Sweeping servo {servo_name} from {start_angle}° to {end_angle}°")
        
        angle_step = (end_angle - start_angle) / steps
        
        for i in range(steps + 1):
            angle = int(start_angle + i * angle_step)
            self.set_servo_angle(servo_name, angle)
            time.sleep(delay)
    
    def set_camera_position(self, tilt_angle=90, pan_angle=90):
        """
        Set camera position using both tilt and pan servos
        
        Args:
            tilt_angle (int): Tilt angle in degrees (0-180)
            pan_angle (int): Pan angle in degrees (0-180)
        """
        if "camera_tilt" in self.servos:
            self.set_servo_angle("camera_tilt", tilt_angle)
        
        if "camera_pan" in self.servos:
            self.set_servo_angle("camera_pan", pan_angle)
        
        print(f"Camera position set: Tilt={tilt_angle}°, Pan={pan_angle}°")
    
    def get_camera_position(self):
        """
        Get current camera position
        
        Returns:
            dict: Current tilt and pan angles
        """
        return {
            "tilt": self.get_servo_angle("camera_tilt"),
            "pan": self.get_servo_angle("camera_pan")
        }
    
    def look_up(self, angle=45, smooth=True, duration=0.8):
        """
        Tilt camera up by specified angle from center
        
        Args:
            angle (int): Angle above center (0-90)
            smooth (bool): Whether to use smooth movement
            duration (float): Duration of smooth movement in seconds
        """
        tilt_angle = 90 - min(90, max(0, angle))  # Fixed: subtract for up
        
        if smooth:
            self.smooth_move_servo("camera_tilt", tilt_angle, duration)
        else:
            self.set_servo_angle("camera_tilt", tilt_angle)
        
        print(f"Camera looking up at {angle}° above center")
    
    def look_down(self, angle=45, smooth=True, duration=0.8):
        """
        Tilt camera down by specified angle from center
        
        Args:
            angle (int): Angle below center (0-90)
            smooth (bool): Whether to use smooth movement
            duration (float): Duration of smooth movement in seconds
        """
        tilt_angle = 90 + min(90, max(0, angle))  # Fixed: add for down
        
        if smooth:
            self.smooth_move_servo("camera_tilt", tilt_angle, duration)
        else:
            self.set_servo_angle("camera_tilt", tilt_angle)
        
        print(f"Camera looking down at {angle}° below center")
    
    def look_left(self, angle=45, smooth=True, duration=0.8):
        """
        Pan camera left by specified angle from center
        
        Args:
            angle (int): Angle left of center (0-90)
            smooth (bool): Whether to use smooth movement
            duration (float): Duration of smooth movement in seconds
        """
        pan_angle = 90 + min(90, max(0, angle))
        
        if smooth:
            self.smooth_move_servo("camera_pan", pan_angle, duration)
        else:
            self.set_servo_angle("camera_pan", pan_angle)
        
        print(f"Camera looking left at {angle}° from center")
    
    def look_right(self, angle=45, smooth=True, duration=0.8):
        """
        Pan camera right by specified angle from center
        
        Args:
            angle (int): Angle right of center (0-90)
            smooth (bool): Whether to use smooth movement
            duration (float): Duration of smooth movement in seconds
        """
        pan_angle = 90 - min(90, max(0, angle))
        
        if smooth:
            self.smooth_move_servo("camera_pan", pan_angle, duration)
        else:
            self.set_servo_angle("camera_pan", pan_angle)
        
        print(f"Camera looking right at {angle}° from center")
    
    def disable_servo(self, servo_name):
        """
        Disable servo by setting PWM to 0
        
        Args:
            servo_name (str): Name of the servo from config
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        channel = self.servos[servo_name]
        self.pca.set_pwm(channel, 0)
        print(f"Servo {servo_name} disabled")
    
    def disable_all_servos(self):
        """Disable all servos"""
        for servo_name in self.servos:
            self.disable_servo(servo_name)
        print("All servos disabled")
    
    def get_servo_status(self):
        """
        Get status of all servos
        
        Returns:
            dict: Servo status information
        """
        status = {}
        for servo_name, channel in self.servos.items():
            status[servo_name] = {
                "channel": channel,
                "current_angle": self.get_servo_angle(servo_name),
                "pwm_duty_cycle": self.pca.get_pwm(channel),
            }
        return status
