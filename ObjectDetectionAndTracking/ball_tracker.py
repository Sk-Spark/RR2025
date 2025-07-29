"""
Ball Tracking Core Module
Integrates ball detection, servo control, and camera management
Main tracking logic and coordination
"""

import time
import threading
import logging
import numpy as np
import cv2
from typing import Optional, Tuple
import config

logger = logging.getLogger(__name__)


class BallTracker:
    """Main ball tracking system coordinator"""
    
    def __init__(self, camera_manager, servo_controller, ball_detector, motor_controller=None):
        """
        Initialize ball tracker
        
        Args:
            camera_manager: CameraManager instance
            servo_controller: BallTrackingServoController instance
            ball_detector: BallDetector instance
            motor_controller: MotorController instance (optional)
        """
        self.camera_manager = camera_manager
        self.servo_controller = servo_controller
        self.ball_detector = ball_detector
        self.motor_controller = motor_controller
        
        # Tracking state
        self.tracking_active = False
        self.tracking_thread = None
        self.stop_tracking = False
        
        # Statistics
        self.detection_count = 0
        self.tracking_start_time = None
        self.last_detection_time = None
        self.detection_history = []
        self.max_history_length = 10
        
        # Performance monitoring
        self.processing_times = []
        self.max_processing_times = 100
        
        # Frame skipping optimization
        self.frame_skip_counter = 0
        
        # Motor control state
        self.movement_timer = None
        self.movement_active = False
        self.frame_skip_interval = getattr(config, 'FRAME_SKIP', 1) if getattr(config, 'USE_FRAME_SKIPPING', False) else 1
        
        logger.info(f"Ball tracker initialized with frame skip interval: {self.frame_skip_interval} (skipping {'enabled' if config.USE_FRAME_SKIPPING else 'disabled'})")
    
    def start_tracking(self):
        """Start the ball tracking system"""
        if not self.tracking_active:
            try:
                # Start camera continuous capture
                self.camera_manager.start_continuous_capture()
                
                # Start main tracking thread
                self.tracking_active = True
                self.stop_tracking = False
                self.tracking_start_time = time.time()
                self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
                self.tracking_thread.start()
                
                logger.info("Ball tracking system started")
                
            except Exception as e:
                logger.error(f"Failed to start tracking: {e}")
                self.stop_tracking_system()
                raise
    
    def stop_tracking_system(self):
        """Stop the ball tracking system"""
        if self.tracking_active:
            try:
                # Stop tracking thread
                self.stop_tracking = True
                self.tracking_active = False
                
                if self.tracking_thread:
                    self.tracking_thread.join(timeout=2.0)
                
                # Stop servo tracking
                self.servo_controller.stop_tracking_mode()
                
                # Stop camera capture
                self.camera_manager.stop_continuous_capture()
                
                logger.info("Ball tracking system stopped")
                
            except Exception as e:
                logger.error(f"Error stopping tracking: {e}")
    
    def _tracking_loop(self):
        """Main tracking loop with configurable frame skipping optimization"""
        logger.info("Tracking loop started")
        
        while not self.stop_tracking and self.tracking_active:
            try:
                start_time = time.time()
                
                # Get latest frame
                frame = self.camera_manager.get_latest_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # Apply frame skipping for detection (if enabled)
                detection = None
                should_detect = True
                
                if config.USE_FRAME_SKIPPING and self.frame_skip_interval > 1:
                    self.frame_skip_counter += 1
                    if self.frame_skip_counter >= self.frame_skip_interval:
                        # Reset counter and run detection
                        self.frame_skip_counter = 0
                        should_detect = True
                    else:
                        should_detect = False
                        # Use last detection for tracking continuity
                        if hasattr(self.ball_detector, 'last_detection') and self.ball_detector.last_detection:
                            detection = self.ball_detector.last_detection
                
                if should_detect:
                    detection = self.ball_detector.detect(frame) # return value (center_x, center_y, radius)

                if detection:
                    self._process_detection(detection, frame.shape)
                else:
                    self._handle_no_detection()
                
                # Update performance metrics
                processing_time = time.time() - start_time
                self._update_performance_metrics(processing_time)
                
                # Control loop timing - optimized for higher FPS
                self._control_loop_timing(start_time)
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(0.1)
        
        logger.info("Tracking loop ended")
    
    def _process_detection(self, detection: Tuple[int, int, int], frame_shape: Tuple[int, int, int]):
        """
        Process a ball detection
        
        Args:
            detection: Tuple of (x, y, radius)
            frame_shape: Shape of the frame (height, width, channels)
        """
        x, y, radius = detection
        frame_height, frame_width = frame_shape[:2]
        
        # Update detection statistics
        self.detection_count += 1
        self.last_detection_time = time.time()
        
        # Add to detection history
        self.detection_history.append({
            'timestamp': time.time(),
            'position': (x, y),
            'radius': radius
        })
        
        # Limit history length
        if len(self.detection_history) > self.max_history_length:
            self.detection_history.pop(0)
        
        # Apply detection filtering/smoothing if needed
        filtered_position = self._filter_detection((x, y))
        
        # Log the ball detection and tracking command
        logger.info(f"🏓 BALL DETECTED: Position=({x},{y}) Radius={radius}px Frame=({frame_width}x{frame_height})")
        
        # Update servo target position using the correct method name
        # self.servo_controller.track_target(
        #     filtered_position[0], 
        #     filtered_position[1],
        #     frame_width, 
        #     frame_height
        # )
        
        # Add motor control for robot following (if enabled)
        if config.ENABLE_MOTOR_FOLLOWING and self.motor_controller:
            self._track_with_motors(filtered_position[0], filtered_position[1], radius, frame_width, frame_height)
        
        logger.debug(f"Ball detected at ({x}, {y}) radius={radius}")
    
    def _handle_no_detection(self):
        """Handle case when no ball is detected"""
        # Could implement prediction, search patterns, etc.
        pass
    
    def _filter_detection(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """
        Apply filtering to detection to reduce noise
        
        Args:
            position: Raw detection position (x, y)
            
        Returns:
            Filtered position (x, y)
        """
        if len(self.detection_history) < 2:
            return position
        
        # Simple moving average filter
        recent_positions = [det['position'] for det in self.detection_history[-3:]]
        avg_x = sum(pos[0] for pos in recent_positions) / len(recent_positions)
        avg_y = sum(pos[1] for pos in recent_positions) / len(recent_positions)
        
        return (int(avg_x), int(avg_y))
    
    def _track_with_motors(self, ball_x, ball_y, ball_radius, frame_width, frame_height):
        """
        Handle robot movement to follow ball using configurable movement type
        
        Args:
            ball_x (int): Ball center X coordinate
            ball_y (int): Ball center Y coordinate
            ball_radius (int): Ball radius in pixels
            frame_width (int): Frame width
            frame_height (int): Frame height
        """
        if not self.motor_controller:
            return
        
        # Get movement configuration from config
        movement_type = getattr(config, 'MOVEMENT_TYPE', 'mecanum')
        enable_rotation = getattr(config, 'ENABLE_ROTATION_TRACKING', True)
        enable_forward_back = getattr(config, 'ENABLE_FORWARD_BACKWARD', True)
        enable_strafing = getattr(config, 'ENABLE_STRAFING', True)
        
        # Get movement gains from config
        rotation_gain = getattr(config, 'ROTATION_GAIN', 0.8)
        forward_gain = getattr(config, 'FORWARD_GAIN', 0.6)
        strafe_gain = getattr(config, 'STRAFE_GAIN', 0.8)
        
        # Calculate frame center
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        # Calculate position errors
        error_x = ball_x - center_x
        error_y = ball_y - center_y
        
        # Calculate deadzone pixels
        deadzone_x = frame_width * config.MOTOR_DEADZONE_X
        deadzone_y = frame_height * config.MOTOR_DEADZONE_Y
        
        # Determine movement speeds with gains
        move_x = 0
        move_y = 0
        rotation = 0
        
        # Horizontal movement (strafe left/right) - only if strafing enabled
        if enable_strafing and abs(error_x) > deadzone_x:
            move_x = int((error_x / center_x) * config.MOTOR_FOLLOW_SPEED * strafe_gain)
            move_x = max(-config.MOTOR_MAX_SPEED, min(config.MOTOR_MAX_SPEED, move_x))
        
        # Rotation for centering ball horizontally - only if rotation enabled
        if enable_rotation and abs(error_x) > deadzone_x:
            rotation = int((error_x / center_x) * config.MOTOR_FOLLOW_SPEED * rotation_gain)
            rotation = max(-config.MOTOR_MAX_SPEED, min(config.MOTOR_MAX_SPEED, rotation))
        
        # Vertical movement (forward/backward based on ball size) - only if forward/back enabled
        if enable_forward_back:
            ball_area = 3.14159 * ball_radius * ball_radius  # Approximate ball area
            ball_size_ratio = ball_area / (frame_width * frame_height)
            
            if ball_size_ratio < config.FOLLOW_DISTANCE_THRESHOLD:
                # Ball is small/far - move forward
                if abs(error_y) > deadzone_y:
                    move_y = int(config.MOTOR_FOLLOW_SPEED * forward_gain)
                else:
                    move_y = int(config.MOTOR_FOLLOW_SPEED * forward_gain // 2)  # Slow forward movement
            elif ball_size_ratio > config.FOLLOW_DISTANCE_THRESHOLD * 2:
                # Ball is large/close - move backward
                move_y = int(-config.MOTOR_FOLLOW_SPEED * forward_gain // 2)
        
        logger.debug(f"Calculated movement: X={move_x}, Y={move_y}, Rot={rotation}, Size Ratio={ball_size_ratio:.3f} ")
        
        # Execute movement based on configured movement type
        if movement_type == "mecanum" and (move_x != 0 or move_y != 0 or rotation != 0):
            # Use enhanced mecanum movement with all parameters
            self._execute_mecanum_movement(move_x, move_y, rotation)
            
        elif movement_type == "tank" and (move_y != 0 or rotation != 0):
            # Use tank-style movement
            self._execute_tank_movement(move_y, rotation)
            
        elif movement_type == "simple" and (move_x != 0 or move_y != 0):
            # Use simple directional movement
            self._execute_simple_movement(move_x, move_y, error_x, error_y, deadzone_x, deadzone_y)
            
        elif movement_type == "strafe_only" and move_x != 0:
            # Only strafe movement
            self._execute_strafe_movement(move_x)
            
        elif movement_type == "turn_only" and rotation != 0:
            # Only rotation movement
            self._execute_rotation_movement(rotation)
            
        else:
            # No movement needed or invalid configuration
            self._stop_movement_after_delay()
            return
        
        logger.debug(f"Robot movement [{movement_type}]: X={move_x}, Y={move_y}, Rot={rotation} "
                    f"(ball at {ball_x},{ball_y}, size_ratio={ball_area/(frame_width*frame_height):.3f})")
    
    def _execute_mecanum_movement(self, move_x, move_y, rotation):
        """Execute mecanum movement with timeout"""
        logger.debug(f"Executing mecanum movement: X={move_x}, Y={move_y}, Rot={rotation}")
        if self.motor_controller:
            # self.motor_controller.mecanum_move(move_x, move_y, rotation)
            self.motor_controller.mecanum_move(move_x, move_y, rotation)
            self._set_movement_timer()
    
    def _execute_tank_movement(self, forward_speed, rotation_speed):
        """Execute tank-style movement with timeout"""
        if self.motor_controller:
            self.motor_controller.tank_move(forward_speed, rotation_speed)
            self._set_movement_timer()
    
    def _execute_simple_movement(self, move_x, move_y, error_x, error_y, deadzone_x, deadzone_y):
        """Execute simple directional movement with timeout"""
        if self.motor_controller:
            # Prioritize the larger error
            if abs(error_x) > abs(error_y) and abs(error_x) > deadzone_x:
                # Horizontal movement
                direction = "right" if move_x > 0 else "left"
                self.motor_controller.simple_move(direction, abs(move_x))
            elif abs(error_y) > deadzone_y:
                # Vertical movement
                direction = "forward" if move_y > 0 else "backward"
                self.motor_controller.simple_move(direction, abs(move_y))
            self._set_movement_timer()
    
    def _execute_strafe_movement(self, move_x):
        """Execute strafe-only movement with timeout"""
        if self.motor_controller:
            self.motor_controller.mecanum_move(move_x, 0, 0)
            self._set_movement_timer()
    
    def _execute_rotation_movement(self, rotation):
        """Execute rotation-only movement with timeout"""
        if self.motor_controller:
            self.motor_controller.mecanum_move(0, 0, rotation)
            self._set_movement_timer()
    
    def _set_movement_timer(self):
        """Set movement timer and mark movement as active"""
        self.movement_active = True
        
        # Cancel existing timer
        if self.movement_timer:
            self.movement_timer.cancel()
        
        # Set new timer to stop movement after short delay
        movement_timeout = getattr(config, 'MOTOR_MOVEMENT_TIMEOUT', 0.2)
        self.movement_timer = threading.Timer(movement_timeout, self._stop_movement)
        self.movement_timer.start()
            
    def _stop_movement(self):
        """Stop robot movement"""
        if self.motor_controller and self.movement_active:
            self.motor_controller.stop_all_motors()
            self.movement_active = False
        if self.movement_timer:
            self.movement_timer.cancel()
            self.movement_timer = None
    
    def _update_performance_metrics(self, processing_time: float):
        """Update performance tracking metrics"""
        self.processing_times.append(processing_time)
        
        # Limit stored processing times
        if len(self.processing_times) > self.max_processing_times:
            self.processing_times.pop(0)
    
    def _control_loop_timing(self, start_time: float):
        """Control loop timing to maintain consistent rate - optimized for performance"""
        # Use optimized detection FPS from config
        target_fps = getattr(config, 'DETECTION_FPS', 15)
        target_loop_time = 1.0 / target_fps
        elapsed = time.time() - start_time
        
        if elapsed < target_loop_time:
            time.sleep(target_loop_time - elapsed)
    
    def get_current_frame_with_overlay(self) -> Optional[np.ndarray]:
        """
        Get current frame with detection and tracking overlays
        
        Returns:
            Frame with overlays, or None if no frame available
        """
        frame = self.camera_manager.get_latest_frame()
        if frame is None:
            return None
        
        # Draw UI elements
        frame = self.camera_manager.draw_ui_elements(frame)
        
        # Get latest detection and draw it
        if hasattr(self.ball_detector, 'last_detection') and self.ball_detector.last_detection:
            frame = self.ball_detector.draw_detection(frame, self.ball_detector.last_detection)
        
        # Draw servo status
        frame = self._draw_servo_status(frame)
        
        # Draw tracking statistics
        frame = self._draw_tracking_stats(frame)
        
        return frame
    
    def _draw_servo_status(self, frame: np.ndarray) -> np.ndarray:
        """Draw servo status on frame"""
        try:
            servo_status = self.servo_controller.get_status()
            
            # Draw servo positions
            cv2.putText(frame, f"Pan: {servo_status['current_pan']:.1f}°", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"Tilt: {servo_status['current_tilt']:.1f}°", 
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Draw tracking status
            status_color = (0, 255, 0) if servo_status['tracking_active'] else (0, 0, 255)
            cv2.putText(frame, f"Tracking: {'ON' if servo_status['tracking_active'] else 'OFF'}", 
                       (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)
            
            # Draw motor status if enabled
            if config.ENABLE_MOTOR_FOLLOWING and self.motor_controller:
                motor_color = (0, 255, 0) if self.movement_active else (255, 255, 255)
                movement_type = getattr(config, 'MOVEMENT_TYPE', 'mecanum')
                cv2.putText(frame, f"Motors: {'ACTIVE' if self.movement_active else 'READY'} [{movement_type.upper()}]", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, motor_color, 1)
                
                # Show movement capabilities
                capabilities = []
                if getattr(config, 'ENABLE_STRAFING', True):
                    capabilities.append("S")  # Strafing
                if getattr(config, 'ENABLE_FORWARD_BACKWARD', True):
                    capabilities.append("F")  # Forward/Backward
                if getattr(config, 'ENABLE_ROTATION_TRACKING', True):
                    capabilities.append("R")  # Rotation
                
                if capabilities:
                    cv2.putText(frame, f"Modes: {'/'.join(capabilities)}", 
                               (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
        except Exception as e:
            logger.error(f"Error drawing servo status: {e}")
        
        return frame
    
    def _draw_tracking_stats(self, frame: np.ndarray) -> np.ndarray:
        """Draw tracking statistics on frame"""
        try:
            # Draw detection count
            cv2.putText(frame, f"Detections: {self.detection_count}", 
                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Draw average processing time
            if self.processing_times:
                avg_time = sum(self.processing_times) / len(self.processing_times)
                cv2.putText(frame, f"Proc: {avg_time*1000:.1f}ms", 
                           (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Draw time since last detection
            if self.last_detection_time:
                time_since = time.time() - self.last_detection_time
                cv2.putText(frame, f"Last: {time_since:.1f}s", 
                           (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
        except Exception as e:
            logger.error(f"Error drawing tracking stats: {e}")
        
        return frame
    
    def get_status(self) -> dict:
        """Get comprehensive tracking system status"""
        camera_status = self.camera_manager.get_status()
        servo_status = self.servo_controller.get_status()
        
        status = {
            'tracking_active': self.tracking_active,
            'detection_count': self.detection_count,
            'tracking_duration': time.time() - self.tracking_start_time if self.tracking_start_time else 0,
            'camera': camera_status,
            'servos': servo_status,
            'detector_type': type(self.ball_detector).__name__,
            'last_detection_time': self.last_detection_time,
            'detection_history_length': len(self.detection_history),
            'motor_following': config.ENABLE_MOTOR_FOLLOWING,
            'movement_active': self.movement_active,
            'movement_type': getattr(config, 'MOVEMENT_TYPE', 'mecanum'),
            'movement_capabilities': {
                'strafing': getattr(config, 'ENABLE_STRAFING', True),
                'forward_backward': getattr(config, 'ENABLE_FORWARD_BACKWARD', True),
                'rotation': getattr(config, 'ENABLE_ROTATION_TRACKING', True)
            },
            'movement_gains': {
                'strafe': getattr(config, 'STRAFE_GAIN', 0.8),
                'forward': getattr(config, 'FORWARD_GAIN', 0.6),
                'rotation': getattr(config, 'ROTATION_GAIN', 0.8)
            }
        }
        
        if self.processing_times:
            status['avg_processing_time'] = sum(self.processing_times) / len(self.processing_times)
            status['max_processing_time'] = max(self.processing_times)
        
        return status
    
    def cleanup(self):
        """Cleanup tracking system"""
        try:
            self.stop_tracking_system()
            
            # Stop any active motor movement
            if self.motor_controller and self.movement_active:
                self.motor_controller.stop_all_motors()
                self.movement_active = False
            
            # Cancel movement timer
            if self.movement_timer:
                self.movement_timer.cancel()
                self.movement_timer = None
            
            logger.info("Ball tracker cleaned up")
        except Exception as e:
            logger.error(f"Error during tracker cleanup: {e}")
