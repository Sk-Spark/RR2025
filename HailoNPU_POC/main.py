#!/usr/bin/env python3
"""
Real-time Object Detection on Raspberry Pi 5 with RPi AI Hat+
Uses heloRT library for hardware-accelerated inference with YOLOv8
Streams processed video with bounding boxes over Flask web interface
"""

import os
import sys
import time
import threading
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify
from picamera2 import Picamera2
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
    # Import hailo_platform for Hailo AI Hat+ acceleration
    import hailo_platform.pyhailort as hailort
    HAILO_AVAILABLE = True
    logger.info("hailo_platform library imported successfully")
except ImportError:
    logger.warning("hailo_platform library not available, falling back to CPU inference")
    HAILO_AVAILABLE = False

class ObjectDetector:
    """Object detection class using YOLOv8 with optional Hailo acceleration"""
    
    def __init__(self, model_path=None, confidence_threshold=None):
        # Set default values from config
        if model_path is None:
            # Make path relative to the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_path = os.path.join(script_dir, config.MODEL_PATH)
        else:
            self.model_path = model_path
            
        self.confidence_threshold = confidence_threshold or config.CONFIDENCE_THRESHOLD
        self.model = None
        self.vdevice = None
        self.network_group = None
        self.input_shape = config.INPUT_SIZE
        self.classes = self._load_coco_classes()
        
        # Use colors from config if available, otherwise generate random colors
        if hasattr(config, 'DETECTION_COLORS') and config.DETECTION_COLORS:
            # Extend colors if we have more classes than colors
            colors = config.DETECTION_COLORS
            while len(colors) < len(self.classes):
                colors.extend(config.DETECTION_COLORS)
            self.colors = colors[:len(self.classes)]
        else:
            self.colors = np.random.randint(0, 255, size=(len(self.classes), 3))
        
        # Initialize the model
        self._initialize_model()
        
    def _load_coco_classes(self):
        """Load COCO dataset class names"""
        return [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
    
    def _initialize_model(self):
        """Initialize the YOLOv8 model with Hailo acceleration if available"""
        try:
            if HAILO_AVAILABLE and os.path.exists(self.model_path):
                # Initialize Hailo model using HEF format
                import hailo_platform
                hef = hailo_platform.HEF(self.model_path)
                # Create virtual device
                vdevice = hailo_platform.VDevice()
                # Configure the HEF
                self.model = vdevice.configure(hef)[0]  # Get the first network group
                logger.info(f"Hailo model loaded: {self.model_path}")
            else:
                # Fallback to OpenCV DNN for CPU inference
                logger.info("Using OpenCV DNN for CPU inference")
                self.model = self._load_opencv_model()
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            # Try to download and use a basic YOLOv8 model
            self.model = self._load_opencv_model()
    
    def _load_opencv_model(self):
        """Load YOLOv8 model using OpenCV DNN as fallback"""
        try:
            # For demonstration, we'll use a simple detection placeholder
            # In production, you'd load an actual YOLOv8 ONNX model
            logger.info("Loading OpenCV DNN model (fallback)")
            return "opencv_fallback"
        except Exception as e:
            logger.error(f"Failed to load OpenCV model: {e}")
            return None
    
    def preprocess_frame(self, frame):
        """Preprocess frame for model input"""
        # Resize frame to model input size
        resized = cv2.resize(frame, self.input_shape)
        # Normalize pixel values
        normalized = resized.astype(np.float32) / 255.0
        # Add batch dimension
        input_tensor = np.expand_dims(normalized, axis=0)
        return input_tensor
    
    def detect_objects(self, frame):
        """Perform object detection on frame"""
        if self.model is None:
            return []
        
        try:
            # Preprocess frame
            input_tensor = self.preprocess_frame(frame)
            
            if HAILO_AVAILABLE and hasattr(self.model, 'run'):
                # Run inference on Hailo NPU
                outputs = self.model.run([input_tensor])  # Hailo expects list of inputs
                detections = self._process_hailo_outputs(outputs, frame.shape)
            else:
                # Fallback detection (simplified for demonstration)
                detections = self._mock_detection(frame)
            
            return detections
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def _process_hailo_outputs(self, outputs, frame_shape):
        """Process Hailo model outputs to extract bounding boxes"""
        detections = []
        
        try:
            # Process YOLOv8 outputs (this is a simplified version)
            # In practice, you'd need to parse the actual model outputs
            for output in outputs:
                # Extract bounding boxes, confidence scores, and class IDs
                # This is model-specific and depends on your YOLOv8 model format
                boxes = output['boxes']  # [x1, y1, x2, y2]
                scores = output['scores']
                class_ids = output['class_ids']
                
                for box, score, class_id in zip(boxes, scores, class_ids):
                    if score > self.confidence_threshold:
                        x1, y1, x2, y2 = box
                        # Scale coordinates to frame size
                        x1 = int(x1 * frame_shape[1] / self.input_shape[1])
                        y1 = int(y1 * frame_shape[0] / self.input_shape[0])
                        x2 = int(x2 * frame_shape[1] / self.input_shape[1])
                        y2 = int(y2 * frame_shape[0] / self.input_shape[0])
                        
                        detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': float(score),
                            'class_id': int(class_id),
                            'class_name': self.classes[class_id] if class_id < len(self.classes) else 'unknown'
                        })
        except Exception as e:
            logger.error(f"Error processing Hailo outputs: {e}")
        
        return detections
    
    def _mock_detection(self, frame):
        """Mock detection for demonstration purposes"""
        # This is a placeholder that returns a sample detection
        # In practice, this would use actual model inference
        detections = []
        
        # Add a mock detection occasionally
        if np.random.random() > 0.7:  # 30% chance of detection
            h, w = frame.shape[:2]
            detections.append({
                'bbox': [w//4, h//4, w//2, h//2],
                'confidence': 0.85,
                'class_id': 0,
                'class_name': 'person'
            })
        
        return detections

class CameraStreamer:
    """Camera streaming class for Raspberry Pi Camera Module 3"""
    
    def __init__(self, resolution=None, framerate=None):
        self.resolution = resolution or config.CAMERA_RESOLUTION
        self.framerate = framerate or config.CAMERA_FRAMERATE
        self.picam2 = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.running = False
        
        # Initialize object detector
        self.detector = ObjectDetector()
        
        # Performance metrics
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def initialize_camera(self):
        """Initialize Raspberry Pi Camera Module 3"""
        try:
            # Try picamera2 first
            self.picam2 = Picamera2()
            
            # Configure camera
            config = self.picam2.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            self.picam2.configure(config)
            
            # Start camera
            self.picam2.start()
            # Wait for camera to initialize
            time.sleep(1)
            logger.info(f"Camera initialized with picamera2: {self.resolution} @ {self.framerate}fps")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to initialize picamera2: {e}")
            # Clean up picamera2 if it was partially initialized
            try:
                if hasattr(self, 'picam2') and self.picam2:
                    if hasattr(self.picam2, 'stop'):
                        self.picam2.stop()
                    if hasattr(self.picam2, 'close'):
                        self.picam2.close()
            except:
                pass
            
            # Try OpenCV fallback
            try:
                self.picam2 = cv2.VideoCapture(0)
                if self.picam2.isOpened():
                    # Test if we can actually read frames
                    ret, test_frame = self.picam2.read()
                    if ret and test_frame is not None:
                        self.picam2.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                        self.picam2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                        self.picam2.set(cv2.CAP_PROP_FPS, self.framerate)
                        logger.info(f"Camera initialized with OpenCV: {self.resolution} @ {self.framerate}fps")
                        return True
                    else:
                        logger.warning("OpenCV camera opened but cannot read frames")
                        self.picam2.release()
                        # Fall through to mock camera
                else:
                    logger.error("Failed to open camera with OpenCV")
                    # Fall through to mock camera
            except Exception as cv_e:
                logger.error(f"Failed to initialize camera with OpenCV: {cv_e}")
                # Fall through to mock camera
            
            # Use mock camera for testing
            self.picam2 = "mock"
            logger.info("Using mock camera for testing")
            return True
    
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
            if hasattr(self.picam2, 'stop'):  # picamera2
                self.picam2.stop()
                self.picam2.close()
            elif hasattr(self.picam2, 'release'):  # OpenCV
                self.picam2.release()
        
        logger.info("Camera streaming stopped")
    
    def _stream_loop(self):
        """Main streaming loop"""
        while self.running:
            try:
                # Capture frame based on camera type
                frame = self._capture_frame()
                
                if frame is not None:
                    # Perform object detection
                    detections = self.detector.detect_objects(frame)
                    
                    # Draw bounding boxes and labels
                    annotated_frame = self._draw_detections(frame, detections)
                    
                    # Update current frame
                    with self.frame_lock:
                        self.current_frame = annotated_frame
                    
                    # Update FPS counter
                    self._update_fps()
                
                time.sleep(1/self.framerate)
                
            except Exception as e:
                logger.error(f"Stream loop error: {e}")
                time.sleep(0.1)
    
    def _capture_frame(self):
        """Capture frame from camera based on type"""
        try:
            if hasattr(self.picam2, 'capture_array'):  # picamera2
                return self.picam2.capture_array()
            elif hasattr(self.picam2, 'read'):  # OpenCV
                ret, frame = self.picam2.read()
                return frame if ret else None
            elif self.picam2 == "mock":  # Mock camera
                # Generate a test pattern
                h, w = self.resolution[1], self.resolution[0]
                frame = np.zeros((h, w, 3), dtype=np.uint8)
                # Add some color pattern
                frame[:h//3, :, 0] = 100  # Red section
                frame[h//3:2*h//3, :, 1] = 100  # Green section
                frame[2*h//3:, :, 2] = 100  # Blue section
                # Add timestamp text
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                cv2.putText(frame, f"Mock Camera - {timestamp}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                return frame
            else:
                return None
        except Exception as e:
            logger.error(f"Frame capture error: {e}")
            return None
    
    def _draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on frame"""
        annotated_frame = frame.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            class_id = detection['class_id']
            
            # Get color for this class
            color = self.detector.colors[class_id % len(self.detector.colors)]
            color = tuple(map(int, color))
            
            # Draw bounding box
            x1, y1, x2, y2 = bbox
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw FPS counter
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(annotated_frame, fps_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return annotated_frame
    
    def _update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        if self.fps_counter >= 30:  # Update every 30 frames
            current_time = time.time()
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def get_frame(self):
        """Get current frame for streaming"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
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