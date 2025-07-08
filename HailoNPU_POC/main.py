#!/usr/bin/env python3
"""
Real-time Object Detection on Raspberry Pi 5 with RPi AI Hat+
Uses Hailo NPU through picamera2 for hardware-accelerated inference
Streams processed video with bounding boxes over Flask web interface
"""

import os
import sys
import time
import threading
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify
from picamera2 import MappedArray, Picamera2
from picamera2.devices import Hailo
import json
from datetime import datetime
import logging
import config

# Set up logging using config
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    # Test Hailo availability by trying to import
    from picamera2.devices import Hailo
    HAILO_AVAILABLE = True
    logger.info("Hailo NPU available through picamera2")
except ImportError as e:
    logger.error(f"Hailo NPU not available: {e}")
    HAILO_AVAILABLE = False
    sys.exit(1)  # Exit if Hailo is not available since this is required

def extract_detections(hailo_output, w, h, class_names, threshold=0.5):
    """Extract detections from the HailoRT-postprocess output."""
    results = []
    for class_id, detections in enumerate(hailo_output):
        for detection in detections:
            score = detection[4]
            if score >= threshold:
                y0, x0, y1, x1 = detection[:4]
                bbox = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
                results.append({
                    'class_name': class_names[class_id] if class_id < len(class_names) else 'unknown',
                    'bbox': bbox,
                    'confidence': float(score),
                    'class_id': class_id
                })
    return results


class HailoObjectDetector:
    """Hailo-based object detector using picamera2"""
    
    def __init__(self, model_path=None, confidence_threshold=None):
        # Set default values from config
        self.model_path = model_path or self._get_default_model_path()
        self.confidence_threshold = confidence_threshold or config.CONFIDENCE_THRESHOLD
        self.class_names = self._load_class_names()
        self.hailo = None
        self.model_w = None
        self.model_h = None
        
        # Initialize colors for drawing
        self.colors = self._generate_colors()
        
        logger.info(f"Initializing Hailo detector with model: {self.model_path}")
        
    def _get_default_model_path(self):
        """Get the default model path"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try config first
        if hasattr(config, 'MODEL_PATH') and config.MODEL_PATH:
            model_path = os.path.join(script_dir, config.MODEL_PATH)
            if os.path.exists(model_path):
                return model_path
        
        # Try local resources directory first (priority order)
        models_dir = os.path.join(script_dir, "resources", "models", "hailo8")
        preferred_models = [
            "yolov8m.hef",      # YOLOv8 medium - good balance of speed/accuracy
            "yolov6n.hef",      # YOLOv6 nano - fastest
            "yolov5m_seg.hef",  # YOLOv5 medium with segmentation
            "yolov8m_pose.hef"  # YOLOv8 with pose estimation
        ]
        
        for model_name in preferred_models:
            model_path = os.path.join(models_dir, model_name)
            if os.path.exists(model_path):
                logger.info(f"Using Hailo model: {model_name}")
                return model_path
        
        # Try any .hef file in the models directory
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith('.hef'):
                    model_path = os.path.join(models_dir, file)
                    logger.info(f"Using available Hailo model: {file}")
                    return model_path
        
        # Try standard Hailo model location
        default_path = "/usr/share/hailo-models/yolov8s_h8l.hef"
        if os.path.exists(default_path):
            return default_path
            
        logger.error("No Hailo model found!")
        raise FileNotFoundError("Hailo model file not found")
        
    def _load_class_names(self):
        """Load class names from labels file or use COCO classes"""
        # Try to load from coco.txt file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        labels_path = os.path.join(script_dir, "coco.txt")
        
        if os.path.exists(labels_path):
            try:
                with open(labels_path, 'r', encoding="utf-8") as f:
                    return f.read().splitlines()
            except Exception as e:
                logger.warning(f"Could not load labels from {labels_path}: {e}")
        
        # Fallback to hardcoded COCO classes
        return ['person','bottle', 'fan', 'pencil', 'book', 'laptop', 'mouse', 'keyboard']
    
    def _generate_colors(self):
        """Generate colors for different classes"""
        if hasattr(config, 'DETECTION_COLORS') and config.DETECTION_COLORS:
            return config.DETECTION_COLORS
        else:
            # Generate random colors for each class
            np.random.seed(42)  # For consistent colors
            return np.random.randint(0, 255, size=(len(self.class_names), 3)).tolist()
    
    def initialize(self):
        """Initialize the Hailo model"""
        try:
            self.hailo = Hailo(self.model_path)
            self.model_h, self.model_w, _ = self.hailo.get_input_shape()
            logger.info(f"Hailo model initialized. Input shape: {self.model_w}x{self.model_h}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Hailo model: {e}")
            return False
    
    def detect_objects(self, frame):
        """Run inference on a frame"""
        if self.hailo is None:
            logger.error("Hailo model not initialized")
            return []
            
        try:
            # Run inference
            results = self.hailo.run(frame)
            
            # Extract detections - we need to get the original frame dimensions
            # for proper scaling
            h, w = frame.shape[:2] if len(frame.shape) > 2 else frame.shape
            
            detections = extract_detections(
                results, w, h, self.class_names, self.confidence_threshold
            )
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources"""
        if self.hailo:
            # Hailo context manager should handle cleanup
            pass

class CameraStreamer:
    """Camera streaming class for Raspberry Pi Camera Module 3 with Hailo detection"""
    
    def __init__(self, resolution=None, framerate=None):
        self.video_w = resolution[0] if resolution else config.CAMERA_RESOLUTION[0]
        self.video_h = resolution[1] if resolution else config.CAMERA_RESOLUTION[1]
        self.framerate = framerate or config.CAMERA_FRAMERATE
        self.picam2 = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.running = False
        
        # Initialize Hailo object detector
        self.detector = HailoObjectDetector()
        if not self.detector.initialize():
            logger.error("Failed to initialize Hailo detector")
            raise RuntimeError("Hailo detector initialization failed")
        
        # Get model input size for low-res stream
        self.model_w = self.detector.model_w
        self.model_h = self.detector.model_h
        
        # Current detections for drawing
        self.current_detections = []
        
        # Performance metrics
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def initialize_camera(self):
        """Initialize Raspberry Pi Camera Module 3"""
        try:
            self.picam2 = Picamera2()
            
            # Configure camera with main stream for display and lores for inference
            main = {'size': (self.video_w, self.video_h), 'format': 'XRGB8888'}
            lores = {'size': (self.model_w, self.model_h), 'format': 'RGB888'}
            controls = {'FrameRate': self.framerate}
            
            config_cam = self.picam2.create_preview_configuration(
                main, lores=lores, controls=controls
            )
            self.picam2.configure(config_cam)
            
            # Set the drawing callback
            self.picam2.pre_callback = self._draw_detections_callback
            
            # Start camera
            self.picam2.start()
            time.sleep(1)  # Wait for camera to initialize
            
            logger.info(f"Camera initialized: main={self.video_w}x{self.video_h}, model={self.model_w}x{self.model_h}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def start_streaming(self):
        """Start the camera streaming thread"""
        if not self.initialize_camera():
            return False
        
        self.running = True
        self.stream_thread = threading.Thread(target=self._stream_loop)
        self.stream_thread.daemon = True
        self.stream_thread.start()
        
        logger.info("Camera streaming started")
        return True
    
    def stop_streaming(self):
        """Stop camera streaming"""
        self.running = False
        if hasattr(self, 'stream_thread'):
            self.stream_thread.join()
        
        if self.picam2:
            try:
                self.picam2.stop()
                self.picam2.close()
            except:
                pass
        
        if self.detector:
            self.detector.cleanup()
        
        logger.info("Camera streaming stopped")
    
    def _stream_loop(self):
        """Main streaming loop - processes low-res frames for inference"""
        while self.running:
            try:
                # Capture low-resolution frame for inference
                lores_frame = self.picam2.capture_array('lores')
                
                if lores_frame is not None:
                    # Perform object detection on low-res frame
                    detections = self.detector.detect_objects(lores_frame)
                    
                    # Update current detections for drawing
                    with self.frame_lock:
                        self.current_detections = detections
                    
                    # Update FPS counter
                    self._update_fps()
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Stream loop error: {e}")
                time.sleep(0.1)
    
    def _draw_detections_callback(self, request):
        """Callback to draw detections on the main camera stream"""
        try:
            objectsDetected = []
            with self.frame_lock:
                current_detections = self.current_detections.copy()
            
            if current_detections:
                with MappedArray(request, "main") as m:
                    for detection in current_detections:
                        class_name = detection['class_name']
                        bbox = detection['bbox']
                        confidence = detection['confidence']
                        class_id = detection['class_id']
                        
                        x0, y0, x1, y1 = bbox
                        x0 = x0*2
                        y0 = y0*2
                        x1 = x1*2
                        y1 = y1*2
                        
                        # Get color for this class
                        color_idx = class_id % len(self.detector.colors)
                        color = self.detector.colors[color_idx]
                        color = (int(color[2]), int(color[1]), int(color[0]), 255)  # BGRA format
                        
                        # Draw bounding box
                        cv2.rectangle(m.array, (x0 , y0), (x1, y1), color, 2)
                        
                        # Draw label
                        label = f"{class_name} {int(confidence * 100)}%"
                        objectsDetected.append(label)
                        cv2.putText(m.array, label, (x0 + 5, y0 + 15),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
                    
                    # Draw FPS counter
                    fps_text = f"FPS: {self.current_fps:.1f}"
                    cv2.putText(m.array, fps_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0, 255), 2)
                    print(f"Objects detected: {objectsDetected}\n")
                               
        except Exception as e:
            logger.error(f"Error drawing detections: {e}")
    
    def _update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        if self.fps_counter >= 30:  # Update every 30 frames
            current_time = time.time()
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def get_frame(self):
        """Get current frame for web streaming"""
        try:
            # Capture the main stream frame
            frame = self.picam2.capture_array('main')
            if frame is not None:
                # Convert XRGB8888 to RGB for JPEG encoding
                if frame.shape[2] == 4:  # XRGB8888
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
                return frame
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
        return None

# Flask web application
app = Flask(__name__)
camera_streamer = CameraStreamer()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """Status endpoint"""
    return jsonify({
        'status': 'running' if camera_streamer.running else 'stopped',
        'fps': camera_streamer.current_fps,
        'hailo_available': HAILO_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

def generate_frames():
    """Generate video frames for streaming"""
    while True:
        frame = camera_streamer.get_frame()
        if frame is not None:
            # Encode frame as JPEG with configured quality
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, config.STREAM_QUALITY])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

def main():
    """Main function"""
    logger.info("Starting Raspberry Pi 5 Object Detection System")
    logger.info(f"Hailo NPU available: {HAILO_AVAILABLE}")
    
    try:
        # Start camera streaming
        if not camera_streamer.start_streaming():
            logger.error("Failed to start camera streaming")
            sys.exit(1)
        
        # Start Flask web server
        logger.info(f"Starting Flask web server on http://{config.WEB_HOST}:{config.WEB_PORT}")
        app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=config.DEBUG_MODE, threaded=True)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        camera_streamer.stop_streaming()
        logger.info("System shutdown complete")

if __name__ == '__main__':
    main()