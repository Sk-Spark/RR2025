"""
Motor Controller Module for Ball Tracking Robot
Controls 4 mecanum wheel motors using PCA9685 PWM driver for following the ball
"""

import board
import busio
from adafruit_pca9685 import PCA9685
import time


class MotorController:
    """Controller for DC motors using PCA9685 for ball following robot"""
    
    def __init__(self, motor_config, i2c_address=0x40, frequency=1000):
        """
        Initialize motor controller
        
        Args:
            motor_config (dict): Motor configuration dictionary
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            frequency (int): PWM frequency in Hz (default: 1000Hz for motors)
        """
        try:
            print(f"Initializing Motor Controller at I2C address {hex(i2c_address)}...")
            
            # Initialize I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685 for motors
            self.pca = PCA9685(self.i2c, address=i2c_address)
            self.pca.frequency = frequency
            
            self.motors = motor_config
            
            # Initialize all motors to stopped state
            self.stop_all_motors()
            
            print(f"Motor controller initialized with {len(self.motors)} motors at {frequency}Hz")
            
        except Exception as e:
            print(f"Error initializing motor controller: {e}")
            raise
    
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
        self.pca.channels[motor["channel"]].duty_cycle = duty_cycle
        
        # Set direction pins
        if direction == "forward":
            self.pca.channels[motor["in1"]].duty_cycle = 65535  # High
            self.pca.channels[motor["in2"]].duty_cycle = 0      # Low
        elif direction == "backward":
            self.pca.channels[motor["in1"]].duty_cycle = 0      # Low
            self.pca.channels[motor["in2"]].duty_cycle = 65535  # High
        else:
            raise ValueError(f"Invalid direction: {direction}. Use 'forward' or 'backward'")
    
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
        self.pca.channels[motor["channel"]].duty_cycle = 0
        self.pca.channels[motor["in1"]].duty_cycle = 0
        self.pca.channels[motor["in2"]].duty_cycle = 0
    
    def stop_all_motors(self):
        """Stop all motors"""
        for motor_name in self.motors:
            self.stop_motor(motor_name)
    
    def move_forward(self, speed=50):
        """Move robot forward"""
        for motor_name in self.motors:
            self.set_motor_speed(motor_name, speed, "forward")
    
    def move_backward(self, speed=50):
        """Move robot backward"""
        for motor_name in self.motors:
            self.set_motor_speed(motor_name, speed, "backward")
    
    def strafe_left(self, speed=50):
        """Strafe left using mecanum wheel kinematics"""
        self.set_motor_speed("front_left", speed, "forward")
        self.set_motor_speed("rear_right", speed, "forward")
        self.set_motor_speed("front_right", speed, "backward")
        self.set_motor_speed("rear_left", speed, "backward")
    
    def strafe_right(self, speed=50):
        """Strafe right using mecanum wheel kinematics"""
        self.set_motor_speed("front_right", speed, "forward")
        self.set_motor_speed("rear_left", speed, "forward")
        self.set_motor_speed("front_left", speed, "backward")
        self.set_motor_speed("rear_right", speed, "backward")
    
    def turn_left(self, speed=50):
        """Turn left by rotating motors in opposite directions"""
        # Right motors forward, left motors backward
        self.set_motor_speed("rear_right", speed, "forward")
        self.set_motor_speed("front_right", speed, "forward")
        self.set_motor_speed("rear_left", speed, "backward")
        self.set_motor_speed("front_left", speed, "backward")
    
    def turn_right(self, speed=50):
        """Turn right by rotating motors in opposite directions"""
        # Left motors forward, right motors backward
        self.set_motor_speed("rear_left", speed, "forward")
        self.set_motor_speed("front_left", speed, "forward")
        self.set_motor_speed("rear_right", speed, "backward")
        self.set_motor_speed("front_right", speed, "backward")
    
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
    
    def follow_ball(self, ball_x, ball_y, frame_width, frame_height, speed=40):
        """
        Move robot to follow the ball based on ball position
        
        Args:
            ball_x (int): Ball X position in pixels
            ball_y (int): Ball Y position in pixels
            frame_width (int): Frame width in pixels
            frame_height (int): Frame height in pixels
            speed (int): Movement speed (0-100)
        """
        # Calculate center positions
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        # Calculate position error
        error_x = ball_x - center_x
        error_y = ball_y - center_y
        
        # Define deadzone to prevent jitter
        deadzone_x = frame_width * 0.1  # 10% of frame width
        deadzone_y = frame_height * 0.1  # 10% of frame height
        
        # Calculate movement speeds based on error
        move_x = 0
        move_y = 0
        
        # Horizontal movement (strafe left/right)
        if abs(error_x) > deadzone_x:
            move_x = int((error_x / center_x) * speed)
            move_x = max(-speed, min(speed, move_x))
        
        # Vertical movement (forward/backward)
        # Note: If ball is higher in frame (lower y), move forward
        if abs(error_y) > deadzone_y:
            move_y = -int((error_y / center_y) * speed)  # Negative because y is inverted
            move_y = max(-speed, min(speed, move_y))
        
        # Use mecanum movement to follow the ball
        self.mecanum_move(move_x, move_y, 0)
        
        return move_x, move_y
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_all_motors()
        if hasattr(self, 'pca'):
            self.pca.deinit()
