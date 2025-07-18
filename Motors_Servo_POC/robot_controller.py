"""
Robot Controller Module
Main controller class that combines motor and servo control
"""

import time
import signal
import sys
from pca9685_controller_gpiozero import PCA9685Controller
from motor_controller import MotorController
from camera_pan_tilt_controller import CameraPanTiltController


class RobotController:
    """Main robot controller combining motor and servo control"""
    
    def __init__(self, motor_config, servo_config, i2c_address=0x40):
        """
        Initialize robot controller
        
        Args:
            motor_config (dict): Motor configuration dictionary
            servo_config (dict): Servo configuration dictionary
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
        """
        print("Initializing Robot Controller...")
        
        # Store configurations
        self.motor_config = motor_config
        self.servo_config = servo_config
        
        # Initialize PCA9685 controller
        self.pca_controller = PCA9685Controller(i2c_address=i2c_address, frequency=50)
        
        # Initialize motor controller
        self.motor_controller = MotorController(self.pca_controller, motor_config)
        
        # Initialize servo controller
        self.servo_controller = CameraPanTiltController(self.pca_controller, servo_config)
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("Robot Controller initialized successfully!")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\nReceived shutdown signal. Cleaning up...")
        self.cleanup()
        sys.exit(0)
    
    # Motor control methods
    def move_forward(self, speed=50, duration=None):
        """
        Move robot forward
        
        Args:
            speed (int): Speed percentage (0-100)
            duration (float): Duration in seconds (None for continuous)
        """
        self.motor_controller.move_forward(speed)
        if duration:
            time.sleep(duration)
            self.stop_movement()
    
    def move_backward(self, speed=50, duration=None):
        """
        Move robot backward
        
        Args:
            speed (int): Speed percentage (0-100)
            duration (float): Duration in seconds (None for continuous)
        """
        self.motor_controller.move_backward(speed)
        if duration:
            time.sleep(duration)
            self.stop_movement()
    
    def turn_left(self, speed=50, duration=None):
        """
        Turn robot left
        
        Args:
            speed (int): Speed percentage (0-100)
            duration (float): Duration in seconds (None for continuous)
        """
        self.motor_controller.turn_left(speed)
        if duration:
            time.sleep(duration)
            self.stop_movement()
    
    def turn_right(self, speed=50, duration=None):
        """
        Turn robot right
        
        Args:
            speed (int): Speed percentage (0-100)
            duration (float): Duration in seconds (None for continuous)
        """
        self.motor_controller.turn_right(speed)
        if duration:
            time.sleep(duration)
            self.stop_movement()
    
    def pivot_left(self, speed=50, duration=None):
        """
        Pivot robot left
        
        Args:
            speed (int): Speed percentage (0-100)
            duration (float): Duration in seconds (None for continuous)
        """
        self.motor_controller.pivot_left(speed)
        if duration:
            time.sleep(duration)
            self.stop_movement()
    
    def pivot_right(self, speed=50, duration=None):
        """
        Pivot robot right
        
        Args:
            speed (int): Speed percentage (0-100)
            duration (float): Duration in seconds (None for continuous)
        """
        self.motor_controller.pivot_right(speed)
        if duration:
            time.sleep(duration)
            self.stop_movement()
    
    def stop_movement(self):
        """Stop all motor movement"""
        self.motor_controller.stop_all_motors()
    
    def set_motor_speed(self, motor_name, speed, direction="forward"):
        """
        Set individual motor speed and direction
        
        Args:
            motor_name (str): Motor name
            speed (int): Speed percentage (0-100)
            direction (str): Direction ("forward" or "backward")
        """
        self.motor_controller.set_motor_speed(motor_name, speed, direction)
    
    # Servo control methods
    def set_camera_position(self, tilt_angle=90, pan_angle=90):
        """
        Set camera position
        
        Args:
            tilt_angle (int): Tilt angle (0-180)
            pan_angle (int): Pan angle (0-180)
        """
        self.servo_controller.set_camera_position(tilt_angle, pan_angle)
    
    def look_up(self, angle=45):
        """Look up by specified angle"""
        self.servo_controller.look_up(angle)
    
    def look_down(self, angle=45):
        """Look down by specified angle"""
        self.servo_controller.look_down(angle)
    
    def look_left(self, angle=45):
        """Look left by specified angle"""
        self.servo_controller.look_left(angle)
    
    def look_right(self, angle=45):
        """Look right by specified angle"""
        self.servo_controller.look_right(angle)
    
    def center_camera(self):
        """Center the camera"""
        self.servo_controller.center_all_servos()
    
    def set_servo_angle(self, servo_name, angle):
        """
        Set servo to specific angle
        
        Args:
            servo_name (str): Servo name
            angle (int): Angle in degrees (0-180)
        """
        self.servo_controller.set_servo_angle(servo_name, angle)
    
    # Combined movement methods
    def scan_and_move(self, movement_func, scan_angles=None, scan_delay=0.5):
        """
        Move while scanning with camera
        
        Args:
            movement_func (callable): Movement function to execute
            scan_angles (list): List of pan angles to scan
            scan_delay (float): Delay between scan positions
        """
        if scan_angles is None:
            scan_angles = [45, 90, 135]  # Left, center, right
        
        movement_func()
        
        for angle in scan_angles:
            self.set_servo_angle("camera_pan", angle)
            time.sleep(scan_delay)
        
        # Return to center
        self.set_servo_angle("camera_pan", 90)
    
    def patrol_mode(self, speed=30, turn_duration=1, scan_duration=2):
        """
        Simple patrol mode - move forward, turn, scan
        
        Args:
            speed (int): Movement speed (0-100)
            turn_duration (float): Duration of turns
            scan_duration (float): Duration of scanning
        """
        print("Starting patrol mode...")
        
        try:
            while True:
                # Move forward
                self.move_forward(speed, duration=3)
                
                # Turn right
                self.turn_right(speed, duration=turn_duration)
                
                # Scan area
                self.scan_and_move(lambda: None, scan_angles=[45, 90, 135], scan_delay=scan_duration/3)
                
                # Move forward
                self.move_forward(speed, duration=3)
                
                # Turn left
                self.turn_left(speed, duration=turn_duration)
                
                # Scan area
                self.scan_and_move(lambda: None, scan_angles=[135, 90, 45], scan_delay=scan_duration/3)
                
        except KeyboardInterrupt:
            print("\nPatrol mode stopped")
            self.stop_movement()
    
    # Status and diagnostic methods
    def get_status(self):
        """
        Get complete robot status
        
        Returns:
            dict: Complete robot status
        """
        return {
            "motors": self.motor_controller.get_motor_status(),
            "servos": self.servo_controller.get_servo_status(),
            "camera_position": self.servo_controller.get_camera_position()
        }
    
    def test_all_motors(self, speed=30, duration=1):
        """
        Test all motors individually
        
        Args:
            speed (int): Test speed (0-100)
            duration (float): Test duration per motor
        """
        print("Testing all motors...")
        
        for motor_name in self.motor_config:
            print(f"Testing {motor_name}...")
            
            # Test forward
            self.set_motor_speed(motor_name, speed, "forward")
            time.sleep(duration)
            
            # Test backward
            self.set_motor_speed(motor_name, speed, "backward")
            time.sleep(duration)
            
            # Stop
            self.motor_controller.stop_motor(motor_name)
            time.sleep(0.5)
        
        print("Motor test completed")
    
    def test_all_servos(self, sweep_delay=0.1):
        """
        Test all servos with sweep
        
        Args:
            sweep_delay (float): Delay between servo positions
        """
        print("Testing all servos...")
        
        for servo_name in self.servo_config:
            print(f"Testing {servo_name}...")
            self.servo_controller.sweep_servo(servo_name, delay=sweep_delay)
            time.sleep(0.5)
        
        # Center all servos
        self.servo_controller.center_all_servos()
        print("Servo test completed")
    
    def demo_mode(self):
        """Run a demonstration of robot capabilities"""
        print("Starting demo mode...")
        
        try:
            # Test servos
            print("1. Testing servos...")
            self.test_all_servos()
            time.sleep(2)
            
            # Test motors
            print("2. Testing motors...")
            self.test_all_motors()
            time.sleep(2)
            
            # Movement demo
            print("3. Movement demonstration...")
            movements = [
                ("Forward", lambda: self.move_forward(40, 2)),
                ("Backward", lambda: self.move_backward(40, 2)),
                ("Turn Left", lambda: self.turn_left(40, 1)),
                ("Turn Right", lambda: self.turn_right(40, 1)),
                ("Pivot Left", lambda: self.pivot_left(40, 1)),
                ("Pivot Right", lambda: self.pivot_right(40, 1)),
            ]
            
            for movement_name, movement_func in movements:
                print(f"Executing: {movement_name}")
                movement_func()
                time.sleep(1)
            
            # Camera demo
            print("4. Camera positioning demo...")
            camera_positions = [
                ("Look Up", lambda: self.look_up(45)),
                ("Look Down", lambda: self.look_down(45)),
                ("Look Left", lambda: self.look_left(45)),
                ("Look Right", lambda: self.look_right(45)),
                ("Center", lambda: self.center_camera()),
            ]
            
            for position_name, position_func in camera_positions:
                print(f"Camera: {position_name}")
                position_func()
                time.sleep(1)
            
            print("Demo completed successfully!")
            
        except KeyboardInterrupt:
            print("\nDemo stopped by user")
        finally:
            self.stop_movement()
            self.center_camera()
    
    def cleanup(self):
        """Clean up all resources"""
        print("Cleaning up robot controller...")
        
        # Stop all motors
        self.motor_controller.stop_all_motors()
        
        # Center and disable servos
        self.servo_controller.center_all_servos()
        time.sleep(0.5)
        self.servo_controller.disable_all_servos()
        
        # Clean up PCA9685
        self.pca_controller.cleanup()
        
        print("Robot controller cleanup completed")
