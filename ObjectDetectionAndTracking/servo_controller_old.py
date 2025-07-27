"""
Pan-Tilt Servo Controller Module
Controls SG90 servos for camera pan and tilt movements
Integrated with ball tracking for real-time adjustments
"""

import time
import threading
import logging
from typing import Tuple, Optional
import config

logger = logging.getLogger(__name__)

# Import servo controller from Motors_Servo_POC
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../Motors_Servo_POC'))

try:
    from pca9685_controller_simple import PCA9685Controller
    from camera_pan_tilt_controller import CameraPanTiltController
except ImportError as e:
    logger.error(f"Failed to import servo controllers: {e}")
    raise


class BallTrackingServoController:
    """Servo controller specifically designed for ball tracking"""
    
    def __init__(self):
        """Initialize the servo controller"""
        self.pca_controller = None
        self.servo_controller = None
        self.current_pan = config.PAN_CENTER_ANGLE
        self.current_tilt = config.TILT_CENTER_ANGLE
        self.target_pan = config.PAN_CENTER_ANGLE
        self.target_tilt = config.TILT_CENTER_ANGLE
        
        # Tracking state
        self.tracking_active = False
        self.last_ball_position = None
        self.tracking_thread = None
        self.stop_tracking = False
        
        # Performance tracking
        self.movement_count = 0
        self.last_movement_time = time.time()
        
        self._initialize_hardware()
        logger.info("Ball tracking servo controller initialized")
    
    def _initialize_hardware(self):
        """Initialize PCA9685 and servo controllers"""
        try:
            # Initialize PCA9685 controller
            self.pca_controller = PCA9685Controller(
                i2c_address=config.PCA9685_ADDRESS,
                frequency=config.PCA9685_FREQUENCY
            )
            
            # Setup servo configuration
            servo_config = {
                'pan': config.PAN_SERVO_CHANNEL,
                'tilt': config.TILT_SERVO_CHANNEL
            }
            
            # Initialize camera pan-tilt controller
            self.servo_controller = CameraPanTiltController(
                self.pca_controller, 
                servo_config
            )
            
            # Move to center position
            self.center_camera()
            
            logger.info("Servo hardware initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize servo hardware: {e}")
            raise
    
    def center_camera(self):
        """Move camera to center position"""
        try:
            self.servo_controller.set_servo_angle('pan', config.PAN_CENTER_ANGLE)
            self.servo_controller.set_servo_angle('tilt', config.TILT_CENTER_ANGLE)
            self.current_pan = config.PAN_CENTER_ANGLE
            self.current_tilt = config.TILT_CENTER_ANGLE
            self.target_pan = config.PAN_CENTER_ANGLE
            self.target_tilt = config.TILT_CENTER_ANGLE
            logger.info("Camera centered")
        except Exception as e:
            logger.error(f"Failed to center camera: {e}")
    
    def calculate_servo_adjustments(self, ball_position: Tuple[int, int], 
                                  frame_size: Tuple[int, int]) -> Tuple[float, float]:
        """
        Calculate servo adjustments needed to center the ball
        
        Args:
            ball_position: Tuple of (x, y) ball center coordinates
            frame_size: Tuple of (width, height) frame dimensions
            
        Returns:
            Tuple of (pan_adjustment, tilt_adjustment) in degrees
        """
        frame_width, frame_height = frame_size
        ball_x, ball_y = ball_position
        
        # Calculate center offsets
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        offset_x = ball_x - center_x
        offset_y = ball_y - center_y
        
        # Check if ball is within deadzone
        if abs(offset_x) < config.TRACKING_DEADZONE and abs(offset_y) < config.TRACKING_DEADZONE:
            return 0.0, 0.0
        
        # Calculate proportional adjustments
        # Note: Pan moves opposite to x offset (positive x offset means pan left)
        pan_adjustment = -offset_x * config.PAN_GAIN
        # Tilt moves same direction as y offset (positive y offset means tilt down)
        tilt_adjustment = offset_y * config.TILT_GAIN
        
        # Limit maximum step size
        pan_adjustment = max(-config.MAX_SERVO_STEP, min(config.MAX_SERVO_STEP, pan_adjustment))
        tilt_adjustment = max(-config.MAX_SERVO_STEP, min(config.MAX_SERVO_STEP, tilt_adjustment))
        
        return pan_adjustment, tilt_adjustment
    
    def update_target_position(self, ball_position: Tuple[int, int], 
                             frame_size: Tuple[int, int]):
        """
        Update target servo positions based on ball position
        
        Args:
            ball_position: Tuple of (x, y) ball center coordinates
            frame_size: Tuple of (width, height) frame dimensions
        """
        try:
            pan_adj, tilt_adj = self.calculate_servo_adjustments(ball_position, frame_size)
            
            if pan_adj != 0 or tilt_adj != 0:
                # Apply smoothing and calculate new target positions
                self.target_pan += pan_adj * config.SERVO_SMOOTHING
                self.target_tilt += tilt_adj * config.SERVO_SMOOTHING
                
                # Clamp to servo limits
                self.target_pan = max(config.PAN_MIN_ANGLE, 
                                    min(config.PAN_MAX_ANGLE, self.target_pan))
                self.target_tilt = max(config.TILT_MIN_ANGLE, 
                                     min(config.TILT_MAX_ANGLE, self.target_tilt))
                
                self.last_ball_position = ball_position
                
                logger.debug(f"Target updated: Pan={self.target_pan:.1f}, Tilt={self.target_tilt:.1f}")
                
        except Exception as e:
            logger.error(f"Error updating target position: {e}")
    
    def move_to_target(self):
        """Move servos to target positions"""
        try:
            # Check if movement is needed
            pan_diff = abs(self.target_pan - self.current_pan)
            tilt_diff = abs(self.target_tilt - self.current_tilt)
            
            if pan_diff > 0.5 or tilt_diff > 0.5:  # Minimum movement threshold
                # Move servos
                self.servo_controller.set_servo_angle('pan', int(self.target_pan))
                self.servo_controller.set_servo_angle('tilt', int(self.target_tilt))
                
                # Update current positions
                self.current_pan = self.target_pan
                self.current_tilt = self.target_tilt
                
                # Update statistics
                self.movement_count += 1
                self.last_movement_time = time.time()
                
                logger.debug(f"Servos moved: Pan={self.current_pan:.1f}, Tilt={self.current_tilt:.1f}")
                
        except Exception as e:
            logger.error(f"Error moving servos: {e}")
    
    def start_tracking(self):
        """Start the tracking thread"""
        if not self.tracking_active:
            self.tracking_active = True
            self.stop_tracking = False
            self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
            self.tracking_thread.start()
            logger.info("Ball tracking started")
    
    def stop_tracking_mode(self):
        """Stop the tracking thread"""
        if self.tracking_active:
            self.stop_tracking = True
            self.tracking_active = False
            if self.tracking_thread:
                self.tracking_thread.join(timeout=1.0)
            logger.info("Ball tracking stopped")
    
    def _tracking_loop(self):
        """Main tracking loop running in separate thread"""
        while not self.stop_tracking and self.tracking_active:
            try:
                # Move to target position
                self.move_to_target()
                
                # Small delay to prevent excessive servo updates
                time.sleep(0.05)  # 20Hz update rate
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(0.1)
    
    def get_status(self) -> dict:
        """Get current servo status"""
        return {
            'current_pan': self.current_pan,
            'current_tilt': self.current_tilt,
            'target_pan': self.target_pan,
            'target_tilt': self.target_tilt,
            'tracking_active': self.tracking_active,
            'movement_count': self.movement_count,
            'last_ball_position': self.last_ball_position
        }
    
    def cleanup(self):
        """Cleanup servo controller"""
        try:
            self.stop_tracking_mode()
            if self.servo_controller:
                self.center_camera()
            logger.info("Servo controller cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
