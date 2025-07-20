"""
Robot Controller Module
Main controller class that integrates Xbox controller with motor and servo control
"""

import time
import signal
import sys
from pca9685_controller import PCA9685Controller
from motor_controller import MotorController
from servo_controller import ServoController
from xbox_controller import XboxGamepadController


class RobotController:
    """Main robot controller integrating gamepad control with motor and servo systems"""
    
    def __init__(self, motor_config, servo_config, i2c_address=0x40, controller_config=None):
        """
        Initialize robot controller
        
        Args:
            motor_config (dict): Motor configuration dictionary
            servo_config (dict): Servo configuration dictionary
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            controller_config (dict): Controller configuration options
        """
        print("Initializing Robot Controller...")
        
        # Store configurations
        self.motor_config = motor_config
        self.servo_config = servo_config
        self.controller_config = controller_config or {}
        
        # Control parameters
        self.motor_speed = self.controller_config.get('default_speed', 50)
        self.servo_increment = self.controller_config.get('servo_increment', 5)
        self.speed_increment = self.controller_config.get('speed_increment', 10)
        self.max_speed = self.controller_config.get('max_speed', 100)
        self.min_speed = self.controller_config.get('min_speed', 20)
        
        # Initialize PCA9685 controller
        self.pca_controller = PCA9685Controller(i2c_address=i2c_address, frequency=50)
        
        # Initialize motor controller
        self.motor_controller = MotorController(self.pca_controller, motor_config)
        
        # Initialize servo controller
        self.servo_controller = ServoController(self.pca_controller, servo_config)
        
        # Initialize Xbox controller
        self.gamepad_controller = XboxGamepadController()
        
        # Robot state
        self.is_running = False
        self.current_movement = None
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("Robot Controller initialized successfully!")
        print(f"Default motor speed: {self.motor_speed}%")
        print(f"Servo increment: {self.servo_increment}°")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\\nReceived shutdown signal. Cleaning up...")
        self.cleanup()
        sys.exit(0)
    
    def setup_controller_callbacks(self):
        """Setup Xbox controller button and analog callbacks"""
        print("Setting up controller callbacks...")
        
        # Movement controls (D-pad and left stick)
        self.gamepad_controller.register_button_callback('dpad_up', self._move_forward, 'press')
        self.gamepad_controller.register_button_callback('dpad_up', self._stop_movement, 'release')
        
        self.gamepad_controller.register_button_callback('dpad_down', self._move_backward, 'press')
        self.gamepad_controller.register_button_callback('dpad_down', self._stop_movement, 'release')
        
        self.gamepad_controller.register_button_callback('dpad_left', self._turn_left, 'press')
        self.gamepad_controller.register_button_callback('dpad_left', self._stop_movement, 'release')
        
        self.gamepad_controller.register_button_callback('dpad_right', self._turn_right, 'press')
        self.gamepad_controller.register_button_callback('dpad_right', self._stop_movement, 'release')
        
        # Strafing controls (shoulder buttons)
        self.gamepad_controller.register_button_callback('lb', self._strafe_left, 'press')
        self.gamepad_controller.register_button_callback('lb', self._stop_movement, 'release')
        
        self.gamepad_controller.register_button_callback('rb', self._strafe_right, 'press')
        self.gamepad_controller.register_button_callback('rb', self._stop_movement, 'release')
        
        # Speed controls (face buttons)
        self.gamepad_controller.register_button_callback('a', self._decrease_speed, 'press')
        self.gamepad_controller.register_button_callback('b', self._increase_speed, 'press')
        self.gamepad_controller.register_button_callback('x', self._emergency_stop, 'press')
        self.gamepad_controller.register_button_callback('y', self._center_servos, 'press')
        
        # Analog stick controls
        self.gamepad_controller.register_analog_callback('left_stick', self._handle_left_stick)
        self.gamepad_controller.register_analog_callback('right_stick', self._handle_right_stick)
        
        # Trigger controls for fine servo adjustment
        self.gamepad_controller.register_analog_callback('left_trigger', self._handle_left_trigger)
        self.gamepad_controller.register_analog_callback('right_trigger', self._handle_right_trigger)
        
        print("Controller callbacks configured!")
    
    # Movement callback methods
    def _move_forward(self):
        """Move robot forward"""
        self.current_movement = "forward"
        self.motor_controller.move_forward(self.motor_speed)
    
    def _move_backward(self):
        """Move robot backward"""
        self.current_movement = "backward"
        self.motor_controller.move_backward(self.motor_speed)
    
    def _turn_left(self):
        """Turn robot left"""
        self.current_movement = "turn_left"
        self.motor_controller.turn_left(self.motor_speed)
    
    def _turn_right(self):
        """Turn robot right"""
        self.current_movement = "turn_right"
        self.motor_controller.turn_right(self.motor_speed)
    
    def _strafe_left(self):
        """Strafe robot left"""
        self.current_movement = "strafe_left"
        self.motor_controller.strafe_left(self.motor_speed)
    
    def _strafe_right(self):
        """Strafe robot right"""
        self.current_movement = "strafe_right"
        self.motor_controller.strafe_right(self.motor_speed)
    
    def _stop_movement(self):
        """Stop all movement"""
        self.current_movement = None
        self.motor_controller.stop_all_motors()
    
    def _emergency_stop(self):
        """Emergency stop - stop all motors and center servos"""
        print("🚨 EMERGENCY STOP!")
        self.motor_controller.stop_all_motors()
        self.servo_controller.center_all_servos()
        self.current_movement = None
    
    def _center_servos(self):
        """Center all servos"""
        print("🎯 Centering all servos")
        self.servo_controller.center_all_servos()
    
    # Speed control methods
    def _increase_speed(self):
        """Increase motor speed"""
        old_speed = self.motor_speed
        self.motor_speed = min(self.max_speed, self.motor_speed + self.speed_increment)
        print(f"🔺 Speed increased: {old_speed}% → {self.motor_speed}%")
    
    def _decrease_speed(self):
        """Decrease motor speed"""
        old_speed = self.motor_speed
        self.motor_speed = max(self.min_speed, self.motor_speed - self.speed_increment)
        print(f"🔻 Speed decreased: {old_speed}% → {self.motor_speed}%")
    
    # Analog stick handlers
    def _handle_left_stick(self, value):
        """Handle left stick input for movement control"""
        x, y = value
        
        # Apply deadzone
        if abs(x) < 0.15 and abs(y) < 0.15:
            if self.current_movement and "stick" in self.current_movement:
                self._stop_movement()
            return
        
        # Calculate movement based on stick position
        speed = int(abs(y) * self.motor_speed)
        
        if abs(y) > abs(x):  # Forward/backward movement
            if y > 0.15:  # Forward
                self.current_movement = "stick_forward"
                self.motor_controller.move_backward(speed)
            elif y < -0.15:  # Backward
                self.current_movement = "stick_backward"
                self.motor_controller.move_forward(speed)
        else:  # Left/right turning
            speed = int(abs(x) * self.motor_speed)
            if x > 0.15:  # Turn right
                self.current_movement = "stick_turn_right"
                self.motor_controller.turn_right(speed)
            elif x < -0.15:  # Turn left
                self.current_movement = "stick_turn_left"
                self.motor_controller.turn_left(speed)
    
    def _handle_right_stick(self, value):
        """Handle right stick input for camera control"""
        x, y = value
        
        # Apply deadzone
        if abs(x) < 0.15 and abs(y) < 0.15:
            return
        
        # Calculate servo adjustments
        pan_delta = int(-x * self.servo_increment)
        tilt_delta = int(y * self.servo_increment)  # Invert Y for intuitive control
        
        # Apply adjustments
        if "camera_pan" in self.servo_config:
            self.servo_controller.adjust_servo_relative("camera_pan", pan_delta)
        
        if "camera_tilt" in self.servo_config:
            self.servo_controller.adjust_servo_relative("camera_tilt", tilt_delta)
    
    def _handle_left_trigger(self, value):
        """Handle left trigger for fine servo control"""
        if value > 0.5:  # Only respond to significant trigger press
            if "camera_tilt" in self.servo_config:
                self.servo_controller.adjust_servo_relative("camera_tilt", -2)
    
    def _handle_right_trigger(self, value):
        """Handle right trigger for fine servo control"""
        if value > 0.5:  # Only respond to significant trigger press
            if "camera_tilt" in self.servo_config:
                self.servo_controller.adjust_servo_relative("camera_tilt", 2)
    
    def start(self):
        """Start the robot controller"""
        print("\\n🚀 Starting Robot Controller...")
        
        # Connect to gamepad
        if not self.gamepad_controller.connect():
            print("❌ Failed to connect to controller!")
            return False
        
        # Setup callbacks
        self.setup_controller_callbacks()
        
        print("\\n🎮 Controller Controls:")
        print("D-Pad: Basic movement (Forward/Back/Left/Right)")
        print("LB/RB: Strafe left/right")
        print("Left Stick: Analog movement control")
        print("Right Stick: Camera pan/tilt")
        print("A: Decrease speed | B: Increase speed")
        print("X: Emergency stop | Y: Center servos")
        print("Triggers: Fine camera tilt adjustment")
        print("\\nPress Ctrl+C to exit\\n")
        
        # Start listening
        self.is_running = True
        try:
            self.gamepad_controller.listen()
        except KeyboardInterrupt:
            print("\\n👋 Shutting down...")
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Cleanup all controllers and stop robot"""
        print("🧹 Cleaning up...")
        
        if hasattr(self, 'motor_controller'):
            self.motor_controller.stop_all_motors()
        
        if hasattr(self, 'servo_controller'):
            self.servo_controller.center_all_servos()
        
        if hasattr(self, 'pca_controller'):
            self.pca_controller.cleanup()
        
        if hasattr(self, 'gamepad_controller'):
            self.gamepad_controller.stop()
        
        self.is_running = False
        print("✅ Cleanup completed")
    
    # Manual control methods for testing
    def test_movement(self):
        """Test basic movement functions"""
        print("\\n🧪 Testing movement functions...")
        
        movements = [
            ("Forward", lambda: self.motor_controller.move_forward(30)),
            ("Backward", lambda: self.motor_controller.move_backward(30)),
            ("Turn Left", lambda: self.motor_controller.turn_left(30)),
            ("Turn Right", lambda: self.motor_controller.turn_right(30)),
            ("Strafe Left", lambda: self.motor_controller.strafe_left(30)),
            ("Strafe Right", lambda: self.motor_controller.strafe_right(30)),
        ]
        
        for name, func in movements:
            print(f"Testing {name}...")
            func()
            time.sleep(1)
            self.motor_controller.stop_all_motors()
            time.sleep(0.5)
        
        print("✅ Movement test completed")
    
    def test_servos(self):
        """Test servo functions"""
        print("\\n🧪 Testing servo functions...")
        
        # Test each servo
        for servo_name in self.servo_config:
            print(f"Testing {servo_name}...")
            self.servo_controller.sweep_servo(servo_name, 45, 135, 5, 0.3)
            self.servo_controller.center_servo(servo_name)
            time.sleep(0.5)
        
        print("✅ Servo test completed")
