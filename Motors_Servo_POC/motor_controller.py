"""
Motor Controller Module
Class for controlling DC motors using PCA9685 PWM driver with GPIO Zero
"""

from pca9685_controller_gpiozero import PCA9685Controller


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
        Turn left by moving right motors forward and left motors backward
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Right motors forward
        self.set_motor_speed("rear_right", speed, "forward")
        self.set_motor_speed("front_right", speed, "forward")
        
        # Left motors backward
        self.set_motor_speed("rear_left", speed, "backward")
        self.set_motor_speed("front_left", speed, "backward")
        
        print(f"Turning left at {speed}% speed")
    
    def turn_right(self, speed=50):
        """
        Turn right by moving left motors forward and right motors backward
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Left motors forward
        self.set_motor_speed("rear_left", speed, "forward")
        self.set_motor_speed("front_left", speed, "forward")
        
        # Right motors backward
        self.set_motor_speed("rear_right", speed, "backward")
        self.set_motor_speed("front_right", speed, "backward")
        
        print(f"Turning right at {speed}% speed")
    
    # Mecanum wheel specific movements
    def strafe_left(self, speed=50):
        """
        Strafe left using mecanum wheel kinematics
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Front left and rear right forward, front right and rear left backward
        self.set_motor_speed("front_left", speed, "forward")
        self.set_motor_speed("rear_right", speed, "forward")
        self.set_motor_speed("front_right", speed, "backward")
        self.set_motor_speed("rear_left", speed, "backward")
        
        print(f"Strafing left at {speed}% speed")
    
    def strafe_right(self, speed=50):
        """
        Strafe right using mecanum wheel kinematics
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Front right and rear left forward, front left and rear right backward
        self.set_motor_speed("front_right", speed, "forward")
        self.set_motor_speed("rear_left", speed, "forward")
        self.set_motor_speed("front_left", speed, "backward")
        self.set_motor_speed("rear_right", speed, "backward")
        
        print(f"Strafing right at {speed}% speed")
    
    def move_diagonal_forward_left(self, speed=50):
        """
        Move diagonally forward-left using mecanum wheels
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Only front left and rear right motors move forward
        self.set_motor_speed("front_left", speed, "forward")
        self.set_motor_speed("rear_right", speed, "forward")
        self.stop_motor("front_right")
        self.stop_motor("rear_left")
        
        print(f"Moving diagonally forward-left at {speed}% speed")
    
    def move_diagonal_forward_right(self, speed=50):
        """
        Move diagonally forward-right using mecanum wheels
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Only front right and rear left motors move forward
        self.set_motor_speed("front_right", speed, "forward")
        self.set_motor_speed("rear_left", speed, "forward")
        self.stop_motor("front_left")
        self.stop_motor("rear_right")
        
        print(f"Moving diagonally forward-right at {speed}% speed")
    
    def move_diagonal_backward_left(self, speed=50):
        """
        Move diagonally backward-left using mecanum wheels
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Only front right and rear left motors move backward
        self.set_motor_speed("front_right", speed, "backward")
        self.set_motor_speed("rear_left", speed, "backward")
        self.stop_motor("front_left")
        self.stop_motor("rear_right")
        
        print(f"Moving diagonally backward-left at {speed}% speed")
    
    def move_diagonal_backward_right(self, speed=50):
        """
        Move diagonally backward-right using mecanum wheels
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Only front left and rear right motors move backward
        self.set_motor_speed("front_left", speed, "backward")
        self.set_motor_speed("rear_right", speed, "backward")
        self.stop_motor("front_right")
        self.stop_motor("rear_left")
        
        print(f"Moving diagonally backward-right at {speed}% speed")
    
    def rotate_clockwise(self, speed=50):
        """
        Rotate clockwise in place using mecanum wheels
        
        Args:
            speed (int): Speed value (0-100)
        """
        # All motors rotate in same direction for clockwise rotation
        self.set_motor_speed("front_left", speed, "forward")
        self.set_motor_speed("rear_left", speed, "forward")
        self.set_motor_speed("front_right", speed, "backward")
        self.set_motor_speed("rear_right", speed, "backward")
        
        print(f"Rotating clockwise at {speed}% speed")
    
    def rotate_counterclockwise(self, speed=50):
        """
        Rotate counterclockwise in place using mecanum wheels
        
        Args:
            speed (int): Speed value (0-100)
        """
        # All motors rotate in opposite direction for counterclockwise rotation
        self.set_motor_speed("front_left", speed, "backward")
        self.set_motor_speed("rear_left", speed, "backward")
        self.set_motor_speed("front_right", speed, "forward")
        self.set_motor_speed("rear_right", speed, "forward")
        
        print(f"Rotating counterclockwise at {speed}% speed")
    
    def mecanum_move(self, x_speed=0, y_speed=0, rotation_speed=0):
        """
        Advanced mecanum movement with combined translation and rotation
        
        Args:
            x_speed (int): Speed in X direction (-100 to 100, negative = left)
            y_speed (int): Speed in Y direction (-100 to 100, negative = backward)
            rotation_speed (int): Rotation speed (-100 to 100, negative = counterclockwise)
        """
        # Clamp speeds to valid range
        x_speed = max(-100, min(100, x_speed))
        y_speed = max(-100, min(100, y_speed))
        rotation_speed = max(-100, min(100, rotation_speed))
        
        # Calculate motor speeds using mecanum kinematics
        # Mecanum wheel equations:
        # FL = y + x + rotation
        # FR = y - x - rotation  
        # RL = y - x + rotation
        # RR = y + x - rotation
        
        fl_speed = y_speed + x_speed + rotation_speed
        fr_speed = y_speed - x_speed - rotation_speed
        rl_speed = y_speed - x_speed + rotation_speed
        rr_speed = y_speed + x_speed - rotation_speed
        
        # Normalize speeds to stay within -100 to 100 range
        max_speed = max(abs(fl_speed), abs(fr_speed), abs(rl_speed), abs(rr_speed))
        if max_speed > 100:
            fl_speed = int((fl_speed / max_speed) * 100)
            fr_speed = int((fr_speed / max_speed) * 100)
            rl_speed = int((rl_speed / max_speed) * 100)
            rr_speed = int((rr_speed / max_speed) * 100)
        
        # Set motor speeds and directions
        motors_speeds = {
            "front_left": fl_speed,
            "front_right": fr_speed,
            "rear_left": rl_speed,
            "rear_right": rr_speed
        }
        
        for motor_name, speed in motors_speeds.items():
            if speed == 0:
                self.stop_motor(motor_name)
            else:
                direction = "forward" if speed > 0 else "backward"
                self.set_motor_speed(motor_name, abs(speed), direction)
        
        print(f"Mecanum move: X={x_speed}, Y={y_speed}, Rot={rotation_speed}")
        print(f"Motor speeds: FL={fl_speed}, FR={fr_speed}, RL={rl_speed}, RR={rr_speed}")
    
    def pivot_left(self, speed=50):
        """
        Pivot left by moving right motors forward and stopping left motors
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Stop left motors
        self.stop_motor("rear_left")
        self.stop_motor("front_left")
        
        # Right motors forward
        self.set_motor_speed("rear_right", speed, "forward")
        self.set_motor_speed("front_right", speed, "forward")
        
        print(f"Pivoting left at {speed}% speed")
    
    def pivot_right(self, speed=50):
        """
        Pivot right by moving left motors forward and stopping right motors
        
        Args:
            speed (int): Speed value (0-100)
        """
        # Stop right motors
        self.stop_motor("rear_right")
        self.stop_motor("front_right")
        
        # Left motors forward
        self.set_motor_speed("rear_left", speed, "forward")
        self.set_motor_speed("front_left", speed, "forward")
        
        print(f"Pivoting right at {speed}% speed")
    
    def get_motor_status(self):
        """
        Get status of all motors
        
        Returns:
            dict: Motor status information
        """
        status = {}
        for motor_name, motor in self.motors.items():
            status[motor_name] = {
                "channel": motor["channel"],
                "speed_pwm": self.pca.get_pwm(motor["channel"]),
                "in1_pwm": self.pca.get_pwm(motor["in1"]),
                "in2_pwm": self.pca.get_pwm(motor["in2"]),
            }
        return status
