"""
Enhanced Ball Tracker with Robot Movement
Integrates servo-based camera tracking with robot movement to follow the ball
"""

import time
import threading
from servo_controller import BallTrackingServoController
from motor_controller import MotorController
import config


class EnhancedBallTracker:
    """Enhanced ball tracker with both camera servo control and robot movement"""
    
    def __init__(self):
        """Initialize the enhanced ball tracker"""
        print("Initializing Enhanced Ball Tracker...")
        
        # Initialize servo controller for camera tracking
        self.servo_controller = BallTrackingServoController()
        
        # Initialize motor controller for robot movement (if enabled)
        self.motor_controller = None
        if config.ENABLE_MOTOR_FOLLOWING:
            try:
                self.motor_controller = MotorController(
                    motor_config=config.MOTOR_CONFIG,
                    pca_controller=self.servo_controller.pca  # Share the PCA9685 instance!
                )
                print("Motor controller initialized - robot will follow ball")
            except Exception as e:
                print(f"Warning: Could not initialize motor controller: {e}")
                print("Camera tracking will work, but robot won't move")
                config.ENABLE_MOTOR_FOLLOWING = False
        
        # Tracking state
        self.tracking_active = False
        self.last_ball_position = None
        self.last_ball_area = 0
        self.movement_timer = None
        self.movement_active = False
        
        # Center the camera
        self.servo_controller.center_camera()
        
        print("Enhanced Ball Tracker initialized successfully")
    
    def track_target(self, ball_x, ball_y, ball_area, frame_width, frame_height):
        """
        Track the ball using both camera servos and robot movement
        
        Args:
            ball_x (int): Ball center X coordinate
            ball_y (int): Ball center Y coordinate  
            ball_area (int): Ball area in pixels
            frame_width (int): Frame width
            frame_height (int): Frame height
        """
        if not self.tracking_active:
            return
        
        # Update last known position
        self.last_ball_position = (ball_x, ball_y)
        self.last_ball_area = ball_area
        
        # 1. Camera servo tracking (always active)
        self._track_with_servos(ball_x, ball_y, frame_width, frame_height)
        
        # 2. Robot movement (if enabled and ball is large enough)
        if (config.ENABLE_MOTOR_FOLLOWING and 
            self.motor_controller and 
            ball_area > config.MOTOR_MIN_BALL_SIZE):
            self._track_with_movement(ball_x, ball_y, ball_area, frame_width, frame_height)
    
    def _track_with_servos(self, ball_x, ball_y, frame_width, frame_height):
        """Handle camera servo tracking"""
        # Calculate frame center
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        # Calculate position errors
        error_x = ball_x - center_x
        error_y = ball_y - center_y
        
        # Apply deadzone
        if abs(error_x) > config.TRACKING_DEADZONE:
            # Pan adjustment (negative because servo direction is inverted)
            pan_adjustment = -error_x * config.PAN_SENSITIVITY / center_x
            current_pan = self.servo_controller.get_pan_angle()
            new_pan = current_pan + pan_adjustment
            self.servo_controller.set_pan_angle(new_pan)
        
        if abs(error_y) > config.TRACKING_DEADZONE:
            # Tilt adjustment
            tilt_adjustment = error_y * config.TILT_SENSITIVITY / center_y
            current_tilt = self.servo_controller.get_tilt_angle()
            new_tilt = current_tilt + tilt_adjustment
            self.servo_controller.set_tilt_angle(new_tilt)
    
    def _track_with_movement(self, ball_x, ball_y, ball_area, frame_width, frame_height):
        """Handle robot movement to follow ball"""
        # Calculate frame center
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        # Calculate position errors
        error_x = ball_x - center_x
        error_y = ball_y - center_y
        
        # Calculate deadzone pixels
        deadzone_x = frame_width * config.MOTOR_DEADZONE_X
        deadzone_y = frame_height * config.MOTOR_DEADZONE_Y
        
        # Determine movement speeds
        move_x = 0
        move_y = 0
        
        # Horizontal movement (strafe left/right)
        if abs(error_x) > deadzone_x:
            move_x = int((error_x / center_x) * config.MOTOR_FOLLOW_SPEED)
            move_x = max(-config.MOTOR_MAX_SPEED, min(config.MOTOR_MAX_SPEED, move_x))
        
        # Vertical movement (forward/backward based on ball size)
        ball_size_ratio = ball_area / (frame_width * frame_height)
        
        if ball_size_ratio < config.FOLLOW_DISTANCE_THRESHOLD:
            # Ball is small/far - move forward
            if abs(error_y) > deadzone_y:
                move_y = config.MOTOR_FOLLOW_SPEED
            else:
                move_y = config.MOTOR_FOLLOW_SPEED // 2  # Slow forward movement
        elif ball_size_ratio > config.FOLLOW_DISTANCE_THRESHOLD * 2:
            # Ball is large/close - move backward
            move_y = -config.MOTOR_FOLLOW_SPEED // 2
        
        # Execute movement if needed
        if move_x != 0 or move_y != 0:
            self._execute_movement(move_x, move_y)
        else:
            self._stop_movement_after_delay()
    
    def _execute_movement(self, move_x, move_y):
        """Execute robot movement with timeout"""
        if self.motor_controller:
            self.motor_controller.mecanum_move(move_x, move_y, 0)
            self.movement_active = True
            
            # Cancel existing timer
            if self.movement_timer:
                self.movement_timer.cancel()
            
            # Set new timer to stop movement after short delay
            self.movement_timer = threading.Timer(0.5, self._stop_movement)
            self.movement_timer.start()
    
    def _stop_movement_after_delay(self):
        """Stop movement after a delay if no new commands"""
        if not self.movement_timer:
            self.movement_timer = threading.Timer(0.2, self._stop_movement)
            self.movement_timer.start()
    
    def _stop_movement(self):
        """Stop robot movement"""
        if self.motor_controller and self.movement_active:
            self.motor_controller.stop_all_motors()
            self.movement_active = False
        if self.movement_timer:
            self.movement_timer.cancel()
            self.movement_timer = None
    
    def start_tracking(self):
        """Start ball tracking"""
        self.tracking_active = True
        print("Enhanced ball tracking started")
    
    def stop_tracking(self):
        """Stop ball tracking"""
        self.tracking_active = False
        self._stop_movement()
        print("Enhanced ball tracking stopped")
    
    def center_camera(self):
        """Center the camera"""
        self.servo_controller.center_camera()
    
    def is_tracking(self):
        """Check if tracking is active"""
        return self.tracking_active
    
    def get_status(self):
        """Get tracker status"""
        status = {
            "tracking_active": self.tracking_active,
            "servo_pan": self.servo_controller.get_pan_angle(),
            "servo_tilt": self.servo_controller.get_tilt_angle(),
            "motor_following": config.ENABLE_MOTOR_FOLLOWING,
            "movement_active": self.movement_active,
            "last_ball_position": self.last_ball_position,
            "last_ball_area": self.last_ball_area
        }
        return status
    
    def emergency_stop(self):
        """Emergency stop all movement"""
        self.stop_tracking()
        if self.motor_controller:
            self.motor_controller.stop_all_motors()
        print("EMERGENCY STOP - All movement halted")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_tracking()
        if self.motor_controller:
            self.motor_controller.cleanup()
        if self.servo_controller:
            self.servo_controller.cleanup()
        print("Enhanced Ball Tracker cleaned up")
