"""
Camera Module
Handles camera initialization, frame capture, and video streaming
Optimized for Raspberry Pi 5 with RPi AI Hat integration
"""

import cv2
import numpy as np
import threading
import time
import logging
from typing import Optional, Callable
import config

logger = logging.getLogger(__name__)

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
    logger.info("picamera2 available")
except ImportError:
    PICAMERA2_AVAILABLE = False
    logger.warning("picamera2 not available, using cv2 fallback")


class CameraManager:
    """Manages camera operations for ball tracking"""
    
    def __init__(self):
        """Initialize camera manager"""
        self.camera = None
        self.frame_buffer = None
        self.latest_frame = None
        self.capture_thread = None
        self.stop_capture = False
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        
        # Frame processing callbacks
        self.frame_processors = []
        
        self._initialize_camera()
        logger.info("Camera manager initialized")
    
    def _initialize_camera(self):
        """Initialize camera hardware"""
        try:
            self.camera = None
            self.camera_type = None
            
            if PICAMERA2_AVAILABLE:
                self._initialize_picamera2()
            
            if self.camera is None:
                self._initialize_cv2_camera()
                
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            logger.warning("Running in simulation mode")
            self.camera = None
            self.camera_type = None
    
    def _initialize_picamera2(self):
        """Initialize Picamera2 with optimized settings"""
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            
            # Check if camera is available by attempting to configure it
            try:
                # Optimized camera configuration based on test_hailo_detection.py
                # Use video configuration for better performance
                camera_config = picam2.create_video_configuration(
                    main={"size": config.CAMERA_RESOLUTION, "format": config.CAMERA_FORMAT},
                    controls={"FrameRate": config.CAMERA_FRAMERATE}
                )
                picam2.configure(camera_config)
                
                # Start the camera
                picam2.start()
                # Wait for camera to stabilize
                import time
                time.sleep(1)
                
                self.camera = picam2
                self.camera_type = "picamera2"
                logger.info(f"Picamera2 optimized: {config.CAMERA_RESOLUTION} {config.CAMERA_FORMAT} @ {config.CAMERA_FRAMERATE}fps")
                
            except Exception as config_error:
                logger.error(f"Failed to configure camera: {config_error}")
                picam2.close()
            
        except ImportError:
            logger.warning("Picamera2 not available")
        except Exception as e:
            logger.error(f"Failed to initialize Picamera2: {e}")
    
    def _initialize_cv2_camera(self):
        """Initialize OpenCV camera as fallback"""
        try:
            self.camera = cv2.VideoCapture(0)
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_RESOLUTION[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_RESOLUTION[1])
            self.camera.set(cv2.CAP_PROP_FPS, config.CAMERA_FRAMERATE)
            
            # Test camera
            ret, _ = self.camera.read()
            if not ret:
                logger.warning("No camera hardware detected - running in simulation mode")
                self.camera = None  # Set to None to indicate no camera
                return
            
            logger.info(f"OpenCV camera initialized: {config.CAMERA_RESOLUTION} @ {config.CAMERA_FRAMERATE}fps")
            
        except Exception as e:
            logger.warning(f"Camera initialization failed: {e} - running in simulation mode")
            self.camera = None
    
    def is_initialized(self) -> bool:
        """Check if camera is properly initialized"""
        return self.camera is not None
    
    def get_camera_type(self) -> str:
        """Get the type of camera being used"""
        return self.camera_type or "simulation"
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera
        
        Returns:
            Captured frame as numpy array in BGR format, or None if failed
        """
        if self.camera is None:
            # Generate a test frame for simulation mode
            height, width = config.CAMERA_RESOLUTION[1], config.CAMERA_RESOLUTION[0]
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            # Add some pattern to make it clear it's simulated
            cv2.putText(frame, "SIMULATION MODE", (width//4, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return frame
            
        try:
            if self.camera_type == "picamera2":
                # picamera2 method with RGB888 format (needs conversion)
                frame = self.camera.capture_array()
                
                # Convert RGB to BGR for OpenCV compatibility
                # if len(frame.shape) == 3 and frame.shape[2] == 3:
                #     frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                return frame
            else:
                # OpenCV method (already BGR)
                ret, frame = self.camera.read()
                return frame if ret else None
                
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def start_continuous_capture(self):
        """Start continuous frame capture in background thread"""
        if self.capture_thread is None or not self.capture_thread.is_alive():
            self.stop_capture = False
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            logger.info("Continuous capture started")
    
    def stop_continuous_capture(self):
        """Stop continuous frame capture"""
        self.stop_capture = True
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        logger.info("Continuous capture stopped")
    
    def _capture_loop(self):
        """Main capture loop running in background thread"""
        while not self.stop_capture:
            try:
                frame = self.capture_frame()
                if frame is not None:
                    self.latest_frame = frame.copy()
                    self._update_fps()
                    
                    # Process frame with registered processors
                    for processor in self.frame_processors:
                        try:
                            processor(frame)
                        except Exception as e:
                            logger.error(f"Error in frame processor: {e}")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(1 / config.CAMERA_FRAMERATE)
                
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def _update_fps(self):
        """Update FPS calculation"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get the most recent captured frame
        
        Returns:
            Latest frame as numpy array, or None if no frame available
        """
        return self.latest_frame.copy() if self.latest_frame is not None else None
    
    def add_frame_processor(self, processor: Callable[[np.ndarray], None]):
        """
        Add a frame processor callback
        
        Args:
            processor: Callable that takes a frame as input
        """
        self.frame_processors.append(processor)
    
    def remove_frame_processor(self, processor: Callable[[np.ndarray], None]):
        """
        Remove a frame processor callback
        
        Args:
            processor: Processor to remove
        """
        if processor in self.frame_processors:
            self.frame_processors.remove(processor)
    
    def draw_ui_elements(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw UI elements on frame (crosshair, deadzone, etc.)
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with UI elements drawn
        """
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Draw center crosshair
        if config.DRAW_CENTER_CROSSHAIR:
            cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), 
                    config.CROSSHAIR_COLOR, 1)
            cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), 
                    config.CROSSHAIR_COLOR, 1)
        
        # Draw deadzone
        if config.DRAW_DEADZONE:
            cv2.rectangle(frame, 
                         (center_x - config.TRACKING_DEADZONE, center_y - config.TRACKING_DEADZONE),
                         (center_x + config.TRACKING_DEADZONE, center_y + config.TRACKING_DEADZONE),
                         config.DEADZONE_COLOR, 1)
        
        # Draw FPS counter
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def get_frame_for_streaming(self) -> Optional[bytes]:
        """
        Get frame encoded as JPEG for streaming with optimized quality
        
        Returns:
            JPEG encoded frame as bytes, or None if no frame available
        """
        frame = self.get_latest_frame()
        if frame is not None:
            # Draw UI elements
            frame = self.draw_ui_elements(frame)
            
            # Use optimized JPEG quality for better performance
            jpeg_quality = getattr(config, 'JPEG_QUALITY', 40)
            _, buffer = cv2.imencode('.jpg', frame, 
                                   [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
            return buffer.tobytes()
        return None
    
    def get_status(self) -> dict:
        """Get camera status information"""
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'resolution': config.CAMERA_RESOLUTION,
            'capture_active': self.capture_thread is not None and self.capture_thread.is_alive(),
            'camera_type': self.get_camera_type(),
            'camera_initialized': self.is_initialized()
        }
    
    def cleanup(self):
        """Cleanup camera resources"""
        try:
            self.stop_continuous_capture()
            
            if self.camera:
                if self.camera_type == "picamera2":
                    self.camera.stop()
                    self.camera.close()
                elif self.camera_type == "opencv":
                    self.camera.release()
            
            self.camera = None
            self.camera_type = None
            logger.info("Camera cleaned up")
            
        except Exception as e:
            logger.error(f"Error during camera cleanup: {e}")
