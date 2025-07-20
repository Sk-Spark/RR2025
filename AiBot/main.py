#!/usr/bin/env python3
"""
AI Bot Web Controller for Raspberry Pi 5
Integrates Hailo NPU object detection, motor control, servo control, and MPU6050 sensor

Features:
- Real-time object detection with Hailo NPU
- 4-wheel mecanum motor control
- Camera pan/tilt servo control
- MPU6050 accelerometer/gyroscope data
- Web-based control interface
- Live video streaming with detection overlays

Author: GitHub Copilot
Date: July 19, 2025
"""

import os
import sys
import time
import threading
import json
import cv2
import numpy as np
from datetime import datetime
import logging
from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO, emit

# Add paths for other modules
sys.path.append('/home/spark/RR2025/HailoNPU_POC')
sys.path.append('/home/spark/RR2025/Motors_Servo_POC')
sys.path.append('/home/spark/RR2025/MPU6050_POC')

try:
    from picamera2 import MappedArray, Picamera2
    from picamera2.devices import Hailo
    HAILO_AVAILABLE = True
except ImportError as e:
    print(f"Hailo NPU not available: {e}")
    HAILO_AVAILABLE = False

try:
    from robot_controller import RobotController
    MOTORS_AVAILABLE = True
except ImportError as e:
    print(f"Motor controller not available: {e}")
    MOTORS_AVAILABLE = False

try:
    from mpu6050 import MPU6050
    MPU6050_AVAILABLE = True
except ImportError as e:
    print(f"MPU6050 sensor not available: {e}")
    MPU6050_AVAILABLE = False

# Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'aibot.log'
DETECTION_THRESHOLD = 0.5
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
FPS = 30

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aibot_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class AIBotController:
    def __init__(self):
        """Initialize AI Bot Controller with all subsystems"""
        logger.info("Initializing AI Bot Controller...")
        
        # State variables
        self.running = False
        self.detection_enabled = True
        self.streaming = False
        self.current_detections = []
        self.sensor_data = {}
        self.robot_status = {
            'connected': False,
            'moving': False,
            'camera_pan': 90,
            'camera_tilt': 90
        }
        
        # Initialize subsystems
        self._init_camera()
        self._init_robot()
        self._init_sensor()
        self._load_class_names()
        
        # Start background threads
        self._start_background_threads()
        
        logger.info("AI Bot Controller initialized successfully!")
    
    def _init_camera(self):
        """Initialize camera and Hailo NPU"""
        self.camera = None
        self.hailo = None
        
        if HAILO_AVAILABLE:
            try:
                self.camera = Picamera2()
                
                # Configure camera
                camera_config = self.camera.create_video_configuration(
                    main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT), "format": "RGB888"},
                    raw={"size": (1640, 1232)},
                    buffer_count=4
                )
                self.camera.configure(camera_config)
                self.camera.start()
                
                # Initialize Hailo NPU (without hef_path for now)
                # self.hailo = Hailo()  # Comment out until HEF model is available
                
                logger.info("Camera initialized (Hailo NPU disabled - no HEF model)")
            except Exception as e:
                logger.error(f"Failed to initialize camera/Hailo: {e}")
                self.camera = None
                self.hailo = None
    
    def _init_robot(self):
        """Initialize robot motor and servo controllers"""
        self.robot = None
        
        if MOTORS_AVAILABLE:
            try:
                # Motor configuration
                motors = {
                    "front_right": {"channel": 15, "in1": 14, "in2": 13},
                    "front_left": {"channel": 4, "in1": 5, "in2": 6},
                    "rear_right": {"channel": 10, "in1": 12, "in2": 11},
                    "rear_left": {"channel": 9, "in1": 7, "in2": 8},
                }
                
                # Servo configuration
                servos = {
                    "camera_tilt": 3,
                    "camera_pan": 2,
                }
                
                self.robot = RobotController(motors, servos, i2c_address=0x40)
                self.robot_status['connected'] = True
                logger.info("Robot controller initialized")
            except Exception as e:
                logger.error(f"Failed to initialize robot controller: {e}")
                self.robot = None
    
    def _init_sensor(self):
        """Initialize MPU6050 sensor"""
        self.mpu = None
        
        if MPU6050_AVAILABLE:
            try:
                self.mpu = MPU6050()
                logger.info("MPU6050 sensor initialized")
            except Exception as e:
                logger.error(f"Failed to initialize MPU6050: {e}")
                self.mpu = None
    
    def _load_class_names(self):
        """Load COCO class names for object detection"""
        self.class_names = [
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
    
    def _start_background_threads(self):
        """Start background threads for sensors and status updates"""
        if self.mpu:
            sensor_thread = threading.Thread(target=self._sensor_loop, daemon=True)
            sensor_thread.start()
        
        status_thread = threading.Thread(target=self._status_loop, daemon=True)
        status_thread.start()
    
    def _sensor_loop(self):
        """Background loop to read sensor data"""
        while True:
            try:
                if self.mpu:
                    accel_data = self.mpu.get_accelerometer_data()
                    gyro_data = self.mpu.get_gyroscope_data()
                    temp = self.mpu.get_temperature()
                    
                    self.sensor_data = {
                        'accelerometer': {
                            'x': round(accel_data[0], 2),
                            'y': round(accel_data[1], 2),
                            'z': round(accel_data[2], 2)
                        },
                        'gyroscope': {
                            'x': round(gyro_data[0], 2),
                            'y': round(gyro_data[1], 2),
                            'z': round(gyro_data[2], 2)
                        },
                        'temperature': round(temp, 1),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Emit sensor data via WebSocket
                    socketio.emit('sensor_data', self.sensor_data)
                
                time.sleep(0.1)  # 10Hz update rate
            except Exception as e:
                logger.error(f"Sensor loop error: {e}")
                time.sleep(1)
    
    def _status_loop(self):
        """Background loop to emit status updates"""
        while True:
            try:
                status = {
                    'robot': self.robot_status,
                    'detection_count': len(self.current_detections),
                    'streaming': self.streaming,
                    'timestamp': datetime.now().isoformat()
                }
                socketio.emit('status_update', status)
                time.sleep(1)  # 1Hz update rate
            except Exception as e:
                logger.error(f"Status loop error: {e}")
                time.sleep(1)
    
    def extract_detections(self, hailo_output, w, h, threshold=DETECTION_THRESHOLD):
        """Extract detections from Hailo output"""
        results = []
        try:
            for class_id, detections in enumerate(hailo_output):
                for detection in detections:
                    score = detection[4]
                    if score >= threshold:
                        y0, x0, y1, x1 = detection[:4]
                        
                        # Convert to pixel coordinates
                        x0 = int(x0 * w)
                        y0 = int(y0 * h)
                        x1 = int(x1 * w)
                        y1 = int(y1 * h)
                        
                        # Get class name
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"Class {class_id}"
                        
                        results.append({
                            'class_name': class_name,
                            'confidence': float(score),
                            'bbox': [x0, y0, x1, y1]
                        })
        except Exception as e:
            logger.error(f"Detection extraction error: {e}")
        
        return results
    
    def draw_detections(self, frame, detections):
        """Draw detection boxes and labels on frame"""
        for detection in detections:
            x0, y0, x1, y1 = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Draw bounding box
            cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x0, y0 - label_size[1] - 10), 
                         (x0 + label_size[0], y0), (0, 255, 0), -1)
            cv2.putText(frame, label, (x0, y0 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame
    
    def generate_frames(self):
        """Generate video frames with detections"""
        self.streaming = True
        
        try:
            while self.streaming and self.camera:
                # Capture frame
                frame = self.camera.capture_array()
                
                if self.detection_enabled and self.hailo:
                    try:
                        # Run inference
                        hailo_output = self.hailo.run(frame)
                        
                        # Extract detections
                        self.current_detections = self.extract_detections(
                            hailo_output, frame.shape[1], frame.shape[0]
                        )
                        
                        # Draw detections
                        frame = self.draw_detections(frame, self.current_detections)
                        
                        # Emit detections via WebSocket
                        socketio.emit('detections', self.current_detections)
                        
                    except Exception as e:
                        logger.error(f"Detection error: {e}")
                
                # Convert to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
        except Exception as e:
            logger.error(f"Frame generation error: {e}")
        finally:
            self.streaming = False
    
    # Robot control methods
    def move_forward(self, speed=50, duration=None):
        """Move robot forward"""
        if self.robot:
            self.robot.move_forward(speed, duration)
            self.robot_status['moving'] = True
    
    def move_backward(self, speed=50, duration=None):
        """Move robot backward"""
        if self.robot:
            self.robot.move_backward(speed, duration)
            self.robot_status['moving'] = True
    
    def turn_left(self, speed=50, duration=None):
        """Turn robot left"""
        if self.robot:
            self.robot.turn_left(speed, duration)
            self.robot_status['moving'] = True
    
    def turn_right(self, speed=50, duration=None):
        """Turn robot right"""
        if self.robot:
            self.robot.turn_right(speed, duration)
            self.robot_status['moving'] = True
    
    def strafe_left(self, speed=50, duration=None):
        """Strafe robot left (mecanum wheels)"""
        if self.robot:
            self.robot.strafe_left(speed, duration)
            self.robot_status['moving'] = True
    
    def strafe_right(self, speed=50, duration=None):
        """Strafe robot right (mecanum wheels)"""
        if self.robot:
            self.robot.strafe_right(speed, duration)
            self.robot_status['moving'] = True
    
    def stop_movement(self):
        """Stop all robot movement"""
        if self.robot:
            self.robot.stop_movement()
            self.robot_status['moving'] = False
    
    def set_camera_pan(self, angle, smooth=True, duration=1.0):
        """Set camera pan angle (0-180 degrees)"""
        if self.robot:
            if smooth:
                self.robot.servo_controller.smooth_move_servo('camera_pan', angle, duration, "ease_in_out")
            else:
                self.robot.set_servo_angle('camera_pan', angle)
            self.robot_status['camera_pan'] = angle
    
    def set_camera_tilt(self, angle, smooth=True, duration=1.0):
        """Set camera tilt angle (0-180 degrees)"""
        if self.robot:
            if smooth:
                self.robot.servo_controller.smooth_move_servo('camera_tilt', angle, duration, "ease_in_out")
            else:
                self.robot.set_servo_angle('camera_tilt', angle)
            self.robot_status['camera_tilt'] = angle
    
    def set_camera_position(self, pan_angle, tilt_angle, smooth=True, duration=1.0):
        """Set both camera pan and tilt angles simultaneously"""
        if self.robot:
            if smooth:
                self.robot.servo_controller.smooth_set_camera_position(tilt_angle, pan_angle, duration, "ease_in_out")
            else:
                self.robot.set_servo_angle('camera_pan', pan_angle)
                self.robot.set_servo_angle('camera_tilt', tilt_angle)
            self.robot_status['camera_pan'] = pan_angle
            self.robot_status['camera_tilt'] = tilt_angle
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up AI Bot Controller...")
        self.streaming = False
        
        if self.camera:
            self.camera.stop()
        
        if self.robot:
            self.robot.cleanup()
        
        if self.mpu:
            self.mpu.close()

# Global controller instance
bot_controller = AIBotController()

# Flask routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(bot_controller.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'robot': bot_controller.robot_status,
        'detection_count': len(bot_controller.current_detections),
        'streaming': bot_controller.streaming,
        'sensor_data': bot_controller.sensor_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/detections')
def get_detections():
    """Get current detections"""
    return jsonify(bot_controller.current_detections)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

@socketio.on('robot_command')
def handle_robot_command(data):
    """Handle robot movement commands"""
    command = data.get('command')
    speed = data.get('speed', 50)
    duration = data.get('duration')
    
    logger.info(f"Robot command: {command}, speed: {speed}")
    
    if command == 'forward':
        bot_controller.move_forward(speed, duration)
    elif command == 'backward':
        bot_controller.move_backward(speed, duration)
    elif command == 'left':
        bot_controller.turn_left(speed, duration)
    elif command == 'right':
        bot_controller.turn_right(speed, duration)
    elif command == 'strafe_left':
        bot_controller.strafe_left(speed, duration)
    elif command == 'strafe_right':
        bot_controller.strafe_right(speed, duration)
    elif command == 'stop':
        bot_controller.stop_movement()
    
    emit('command_response', {'status': 'executed', 'command': command})

@socketio.on('camera_command')
def handle_camera_command(data):
    """Handle camera pan/tilt commands"""
    command = data.get('command')
    angle = data.get('angle', 90)
    smooth = data.get('smooth', True)
    duration = data.get('duration', 1.0)
    
    logger.info(f"Camera command: {command}, angle: {angle}, smooth: {smooth}")
    
    if command == 'pan':
        bot_controller.set_camera_pan(angle, smooth, duration)
    elif command == 'tilt':
        bot_controller.set_camera_tilt(angle, smooth, duration)
    elif command == 'position':
        pan_angle = data.get('pan_angle', 90)
        tilt_angle = data.get('tilt_angle', 90)
        bot_controller.set_camera_position(pan_angle, tilt_angle, smooth, duration)
    
    emit('command_response', {'status': 'executed', 'command': command})

@socketio.on('detection_toggle')
def handle_detection_toggle(data):
    """Toggle object detection on/off"""
    bot_controller.detection_enabled = data.get('enabled', True)
    logger.info(f"Detection {'enabled' if bot_controller.detection_enabled else 'disabled'}")
    emit('detection_status', {'enabled': bot_controller.detection_enabled})

if __name__ == '__main__':
    try:
        logger.info("Starting AI Bot Web Controller...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        bot_controller.cleanup()
