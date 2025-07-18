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
    
    def look_up(self, angle=45):
        """
        Tilt camera up by specified angle from center
        
        Args:
            angle (int): Angle above center (0-90)
        """
        tilt_angle = 90 - min(90, max(0, angle))  # Fixed: subtract for up
        self.set_servo_angle("camera_tilt", tilt_angle)
        print(f"Camera looking up at {angle}° above center")
    
    def look_down(self, angle=45):
        """
        Tilt camera down by specified angle from center
        
        Args:
            angle (int): Angle below center (0-90)
        """
        tilt_angle = 90 + min(90, max(0, angle))  # Fixed: add for down
        self.set_servo_angle("camera_tilt", tilt_angle)
        print(f"Camera looking down at {angle}° below center")
    
    def look_left(self, angle=45):
        """
        Pan camera left by specified angle from center
        
        Args:
            angle (int): Angle left of center (0-90)
        """
        pan_angle = 90 + min(90, max(0, angle))
        self.set_servo_angle("camera_pan", pan_angle)
        print(f"Camera looking left at {angle}° from center")
    
    def look_right(self, angle=45):
        """
        Pan camera right by specified angle from center
        
        Args:
            angle (int): Angle right of center (0-90)
        """
        pan_angle = 90 - min(90, max(0, angle))
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
