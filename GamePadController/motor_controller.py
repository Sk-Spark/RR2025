"""
Motor Controller Module for Robot Control
Class for controlling DC motors using PCA9685 PWM driver
"""

from pca9685_controller import PCA9685Controller


class MotorController:
    """Controller for DC motors using PCA9685"""
    
    def __init__(self, pca_controller, motor_config):
        """
        Initialize motor controller
        
        Args:
            pca_controller (PCA9685Controller): Instance of PCA9685Controller
            motor_config (dict): Motor configuration dictionary
        """
        self.pca = pca_controller
        self.motors = motor_config
        
        # Initialize all motors to stopped state
        self.stop_all_motors()
        
        print(f"Motor controller initialized with {len(self.motors)} motors")
    
    def set_motor_speed(self, motor_name, speed, direction="forward"):
        """
        Set motor speed and direction
        
        Args:
            motor_name (str): Name of the motor from config
            speed (int): Speed value (0-100)
            direction (str): Direction ("forward" or "backward")
        """
        if motor_name not in self.motors:
            raise ValueError(f"Motor {motor_name} not found in configuration")
        
        motor = self.motors[motor_name]
        
        # Convert speed percentage to PWM duty cycle (0-65535)
        speed = max(0, min(100, speed))  # Clamp between 0-100
        duty_cycle = int((speed / 100) * 65535)
        
        # Set PWM for motor enable/speed
        self.pca.set_pwm(motor["channel"], duty_cycle)
        
        # Set direction pins
        if direction == "forward":
            self.pca.set_pwm(motor["in1"], 65535)  # High
            self.pca.set_pwm(motor["in2"], 0)      # Low
        elif direction == "backward":
            self.pca.set_pwm(motor["in1"], 0)      # Low
            self.pca.set_pwm(motor["in2"], 65535)  # High
        else:
            raise ValueError(f"Invalid direction: {direction}. Use 'forward' or 'backward'")
        
        print(f"Motor {motor_name}: Speed={speed}%, Direction={direction}")
    
    def stop_motor(self, motor_name):
        """
        Stop a specific motor
        
        Args:
            motor_name (str): Name of the motor from config
        """
        if motor_name not in self.motors:
            raise ValueError(f"Motor {motor_name} not found in configuration")
        
        motor = self.motors[motor_name]
        
        # Set all channels to 0
        self.pca.set_pwm(motor["channel"], 0)
        self.pca.set_pwm(motor["in1"], 0)
        self.pca.set_pwm(motor["in2"], 0)
        
        print(f"Motor {motor_name} stopped")
    
    def stop_all_motors(self):
        """Stop all motors"""
        for motor_name in self.motors:
            self.stop_motor(motor_name)
        print("All motors stopped")
    
    def move_forward(self, speed=50):
        """
        Move all motors forward at specified speed
        
        Args:
            speed (int): Speed value (0-100)
        """
        for motor_name in self.motors:
            self.set_motor_speed(motor_name, speed, "forward")
        print(f"Moving forward at {speed}% speed")
    
    def move_backward(self, speed=50):
        """
        Move all motors backward at specified speed
        
        Args:
            speed (int): Speed value (0-100)
        """
        for motor_name in self.motors:
            self.set_motor_speed(motor_name, speed, "backward")
        print(f"Moving backward at {speed}% speed")
    
    def turn_left(self, speed=50):
        """
        Turn left by rotating right side motors forward and left side motors backward
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Right side motors forward
        self.set_motor_speed("front_right", speed, "forward")
        self.set_motor_speed("rear_right", speed, "forward")
        
        # Left side motors backward
        self.set_motor_speed("front_left", speed, "backward")
        self.set_motor_speed("rear_left", speed, "backward")
        
        print(f"Turning left at {speed}% speed")
    
    def turn_right(self, speed=50):
        """
        Turn right by rotating left side motors forward and right side motors backward
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Left side motors forward
        self.set_motor_speed("front_left", speed, "forward")
        self.set_motor_speed("rear_left", speed, "forward")
        
        # Right side motors backward
        self.set_motor_speed("front_right", speed, "backward")
        self.set_motor_speed("rear_right", speed, "backward")
        
        print(f"Turning right at {speed}% speed")
    
    def strafe_left(self, speed=50):
        """
        Strafe left (mecanum wheel movement)
        
        Args:
            speed (int): Speed value (0-100)
        """
        # For mecanum wheels: front_left & rear_right backward, front_right & rear_left forward
        self.set_motor_speed("front_left", speed, "backward")
        self.set_motor_speed("rear_right", speed, "backward")
        self.set_motor_speed("front_right", speed, "forward")
        self.set_motor_speed("rear_left", speed, "forward")
        
        print(f"Strafing left at {speed}% speed")
    
    def strafe_right(self, speed=50):
        """
        Strafe right (mecanum wheel movement)
        
        Args:
            speed (int): Speed value (0-100)
        """
        # For mecanum wheels: front_left & rear_right forward, front_right & rear_left backward
        self.set_motor_speed("front_left", speed, "forward")
        self.set_motor_speed("rear_right", speed, "forward")
        self.set_motor_speed("front_right", speed, "backward")
        self.set_motor_speed("rear_left", speed, "backward")
        
        print(f"Strafing right at {speed}% speed")
