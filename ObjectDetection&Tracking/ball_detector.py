"""
Ball Detection Module
Provides multiple methods for detecting ping pong balls:
1. Color-based detection using HSV filtering
2. Hailo NPU-based detection for sports balls
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional
import config

# Import the Hailo detector
try:
    from hailo_detector import HailoObjectDetector
    HAILO_DETECTOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Hailo detector not available: {e}")
    HAILO_DETECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class BallDetector:
    """Base class for ball detection"""
    
    def __init__(self):
        self.last_detection = None
        self.detection_count = 0
    
    def detect(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Detect ball in frame
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Tuple of (x, y, radius) if ball detected, None otherwise
        """
        raise NotImplementedError
    
    def draw_detection(self, frame: np.ndarray, detection: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw detection on frame
        
        Args:
            frame: Input frame
            detection: Tuple of (x, y, radius)
            
        Returns:
            Frame with detection drawn
        """
        if detection:
            x, y, radius = detection
            # Draw circle around ball
            cv2.circle(frame, (x, y), radius, config.DETECTION_COLOR, 2)
            # Draw center point
            cv2.circle(frame, (x, y), 3, config.DETECTION_COLOR, -1)
            # Draw ball info
            if config.SHOW_DETECTION_INFO:
                cv2.putText(frame, f"Ball: ({x},{y}) r={radius}", 
                           (x-50, y-radius-10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, config.DETECTION_COLOR, 1)
        return frame


class ColorBasedBallDetector(BallDetector):
    """Color-based ball detection using HSV filtering"""
    
    def __init__(self):
        super().__init__()
        self.hsv_lower = np.array(config.BALL_COLOR_HSV_LOWER)
        self.hsv_upper = np.array(config.BALL_COLOR_HSV_UPPER)
        logger.info(f"Color-based detector initialized. HSV range: {self.hsv_lower} - {self.hsv_upper}")
    
    def detect(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Detect orange ping pong ball using color filtering
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Tuple of (x, y, radius) if ball detected, None otherwise
        """
        try:
            # Convert BGR to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create mask for orange color
            mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
            
            # Apply Gaussian blur to reduce noise
            mask = cv2.GaussianBlur(mask, (config.BLUR_KERNEL_SIZE, config.BLUR_KERNEL_SIZE), 0)
            
            # Apply morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, 
                                             (config.MORPHOLOGY_KERNEL_SIZE, config.MORPHOLOGY_KERNEL_SIZE))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest contour (assumed to be the ball)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Calculate minimum enclosing circle
                (x, y), radius = cv2.minEnclosingCircle(largest_contour)
                
                # Check if the detected object is within reasonable size limits
                if config.BALL_MIN_RADIUS <= radius <= config.BALL_MAX_RADIUS:
                    detection = (int(x), int(y), int(radius))
                    self.last_detection = detection
                    self.detection_count += 1
                    return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Error in color-based detection: {e}")
            return None


class HailoBallDetector(BallDetector):
    """Hailo NPU-based ball detection using sports ball class"""
    
    def __init__(self):
        super().__init__()
        self.target_class = config.HAILO_BALL_CLASS_NAME
        self.hailo_detector = None
        
        if HAILO_DETECTOR_AVAILABLE:
            try:
                self.hailo_detector = HailoObjectDetector()
                if not self.hailo_detector.initialize():
                    self.hailo_detector = None
                    logger.error("Failed to initialize Hailo detector")
                else:
                    logger.info(f"Hailo-based detector initialized. Target class: {self.target_class}")
            except Exception as e:
                logger.error(f"Error initializing Hailo detector: {e}")
                self.hailo_detector = None
        else:
            logger.warning("Hailo detector not available")
    
    def detect(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Detect ball using Hailo NPU object detection
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Tuple of (x, y, radius) if ball detected, None otherwise
        """
        if not self.hailo_detector:
            logger.warning("Hailo detector not available")
            return None
        
        try:
            # Get detections from Hailo
            detections = self.hailo_detector.detect(frame)
            
            # Filter for sports ball detections
            ball_detections = [
                det for det in detections 
                if det['class_name'] == self.target_class and 
                   det['confidence'] >= config.HAILO_CONFIDENCE_THRESHOLD
            ]
            
            if ball_detections:
                # Use the detection with highest confidence
                best_detection = max(ball_detections, key=lambda x: x['confidence'])
                bbox = best_detection['bbox']
                
                # Calculate center and radius from bounding box
                x1, y1, x2, y2 = bbox
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                radius = max((x2 - x1), (y2 - y1)) // 2
                
                # Check size limits
                if config.BALL_MIN_RADIUS <= radius <= config.BALL_MAX_RADIUS:
                    detection = (center_x, center_y, radius)
                    self.last_detection = detection
                    self.detection_count += 1
                    return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Error in Hailo-based detection: {e}")
            return None


class HybridBallDetector(BallDetector):
    """Hybrid detector that uses both color and Hailo detection"""
    
    def __init__(self):
        super().__init__()
        self.color_detector = ColorBasedBallDetector()
        self.hailo_detector = HailoBallDetector() if HAILO_DETECTOR_AVAILABLE else None
        self.use_hailo = config.USE_HAILO_DETECTION and self.hailo_detector is not None and self.hailo_detector.hailo_detector is not None
        logger.info(f"Hybrid detector initialized. Use Hailo: {self.use_hailo}")
    
    def detect(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Detect ball using hybrid approach
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Tuple of (x, y, radius) if ball detected, None otherwise
        """
        detection = None
        
        # Try Hailo detection first if available
        if self.use_hailo and self.hailo_detector:
            detection = self.hailo_detector.detect(frame)
            if detection:
                logger.debug("Ball detected using Hailo NPU")
                self.last_detection = detection
                self.detection_count += 1
                return detection
        
        # Fallback to color-based detection
        detection = self.color_detector.detect(frame)
        if detection:
            logger.debug("Ball detected using color detection")
            self.last_detection = detection
            self.detection_count += 1
        
        return detection
