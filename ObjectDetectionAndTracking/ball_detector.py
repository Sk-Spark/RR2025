"""
Ball Detection Module - Hailo NPU Only
Provides Hailo NPU-based detection for ping pong balls using sports ball class
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
    logging.error(f"Hailo detector not available: {e}")
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
            cv2.circle(frame, (x, y), radius, (0, 255, 0), 2)
            # Draw center point
            cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
            # Add label
            cv2.putText(frame, f"Ball ({radius}px)", (x-30, y-radius-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame


class HailoBallDetector(BallDetector):
    """Hailo NPU-based ball detection using sports ball class"""
    
    def __init__(self):
        super().__init__()
        self.target_class = config.HAILO_BALL_CLASS_NAME
        self.hailo_detector = None
        
        if not HAILO_DETECTOR_AVAILABLE:
            raise RuntimeError("Hailo detector not available - required for ball detection")
        
        try:
            self.hailo_detector = HailoObjectDetector()
            if not self.hailo_detector.initialize():
                raise RuntimeError("Failed to initialize Hailo detector")
            
            logger.info(f"Hailo-based detector initialized. Target class: {self.target_class}")
        except Exception as e:
            logger.error(f"Error initializing Hailo detector: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Detect ball using Hailo NPU object detection
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Tuple of (x, y, radius) if ball detected, None otherwise
        """
        if not self.hailo_detector:
            logger.error("Hailo detector not available")
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
                    logger.debug(f"Ball detected: center=({center_x}, {center_y}), radius={radius}, confidence={best_detection['confidence']:.2f}")
                    return detection
                else:
                    logger.debug(f"Ball detected but size out of range: radius={radius}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in Hailo-based detection: {e}")
            return None
    
    def cleanup(self):
        """Clean up Hailo detector resources"""
        if self.hailo_detector:
            self.hailo_detector.cleanup()
            self.hailo_detector = None


# For backward compatibility, provide a factory function
def create_ball_detector() -> BallDetector:
    """
    Create and return the ball detector instance
    
    Returns:
        HailoBallDetector instance
    """
    return HailoBallDetector()
