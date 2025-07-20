"""
Servo Controller Module for Robot Control
Class for controlling SG90 servos using PCA9685 PWM driver
"""

import time
from pca9685_controller import PCA9685Controller


class ServoController:
    """Controller for SG90 servos using PCA9685"""
    
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
        
        print(f"Servo controller initialized with {len(self.servos)} servos")
    
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
        
        # Linear interpolation between min and max pulse widths
        pulse_width = self.servo_min_pulse + (angle / self.servo_max_angle) * (self.servo_max_pulse - self.servo_min_pulse)
        
        return int(pulse_width)
    
    def set_servo_angle(self, servo_name, angle):
        """
        Set servo to specific angle
        
        Args:
            servo_name (str): Name of the servo from config
            angle (int): Angle in degrees (0-180)
        """
        if servo_name not in self.servos:
            raise ValueError(f"Servo {servo_name} not found in configuration")
        
        # Get servo channel
        channel = self.servos[servo_name]
        
        # Convert angle to pulse width
        pulse_width = self.angle_to_pulse_width(angle)
        
        # Set PWM pulse width
        self.pca.set_pulse_width(channel, pulse_width)
        
        # Update current position
        self.current_positions[servo_name] = angle
        
        print(f"Servo {servo_name} set to {angle}° (pulse: {pulse_width}μs)")
    
    def get_servo_angle(self, servo_name):
        """
        Get current servo angle
        
        Args:
            servo_name (str): Name of the servo from config
            
        Returns:
            int: Current angle in degrees
        """
        return self.current_positions.get(servo_name, 90)  # Default to center
    
    def center_servo(self, servo_name):
        """
        Center a specific servo (90 degrees)
        
        Args:
            servo_name (str): Name of the servo from config
        """
        self.set_servo_angle(servo_name, 90)
    
    def center_all_servos(self):
        """Center all servos to 90 degrees"""
        for servo_name in self.servos:
            self.center_servo(servo_name)
        print("All servos centered")
    
    def move_servo_smooth(self, servo_name, target_angle, steps=10, delay=0.05):
        """
        Move servo smoothly to target angle
        
        Args:
            servo_name (str): Name of the servo from config
            target_angle (int): Target angle in degrees (0-180)
            steps (int): Number of intermediate steps
            delay (float): Delay between steps in seconds
        """
        current_angle = self.get_servo_angle(servo_name)
        angle_diff = target_angle - current_angle
        
        for i in range(steps + 1):
            intermediate_angle = current_angle + (angle_diff * i / steps)
            self.set_servo_angle(servo_name, int(intermediate_angle))
            if i < steps:  # Don't delay after the last step
                time.sleep(delay)
    
    def pan_tilt_camera(self, pan_angle, tilt_angle):
        """
        Set camera pan and tilt angles simultaneously
        
        Args:
            pan_angle (int): Pan angle in degrees (0-180)
            tilt_angle (int): Tilt angle in degrees (0-180)
        """
        if "camera_pan" in self.servos:
            self.set_servo_angle("camera_pan", pan_angle)
        
        if "camera_tilt" in self.servos:
            self.set_servo_angle("camera_tilt", tilt_angle)
        
        print(f"Camera: Pan={pan_angle}°, Tilt={tilt_angle}°")
    
    def adjust_servo_relative(self, servo_name, angle_delta):
        """
        Adjust servo position relative to current position
        
        Args:
            servo_name (str): Name of the servo from config
            angle_delta (int): Angle change in degrees (can be negative)
        """
        current_angle = self.get_servo_angle(servo_name)
        new_angle = current_angle + angle_delta
        
        # Clamp to valid range
        new_angle = max(0, min(180, new_angle))
        
        self.set_servo_angle(servo_name, new_angle)
    
    def sweep_servo(self, servo_name, min_angle=0, max_angle=180, steps=10, delay=0.1):
        """
        Sweep servo between min and max angles
        
        Args:
            servo_name (str): Name of the servo from config
            min_angle (int): Minimum angle in degrees
            max_angle (int): Maximum angle in degrees
            steps (int): Number of steps in sweep
            delay (float): Delay between steps in seconds
        """
        print(f"Sweeping {servo_name} from {min_angle}° to {max_angle}°")
        
        # Sweep forward
        for i in range(steps + 1):
            angle = min_angle + (max_angle - min_angle) * i / steps
            self.set_servo_angle(servo_name, int(angle))
            time.sleep(delay)
        
        # Sweep backward
        for i in range(steps, -1, -1):
            angle = min_angle + (max_angle - min_angle) * i / steps
            self.set_servo_angle(servo_name, int(angle))
            time.sleep(delay)
