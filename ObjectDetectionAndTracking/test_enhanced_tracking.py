#!/usr/bin/env python3
"""
Enhanced Ball Tracking Test with Robot Movement
Test script for ball detection, camera tracking, and robot following
"""

from flask import Flask, Response, render_template_string, jsonify, request
from picamera2 import Picamera2
import cv2
import time
import threading
import json

# Import our enhanced components
try:
    from enhanced_ball_tracker import EnhancedBallTracker
    TRACKER_AVAILABLE = True
    print("Enhanced ball tracker available")
except ImportError as e:
    print(f"Enhanced ball tracker not available: {e}")
    TRACKER_AVAILABLE = False

try:
    from hailo_detector import HailoObjectDetector
    HAILO_AVAILABLE = True
    print("Hailo detector available")
except ImportError as e:
    print(f"Hailo detector not available: {e}")
    HAILO_AVAILABLE = False

import config

app = Flask(__name__)

# Global variables for tracking
current_frame = None
detections = []
frame_lock = threading.Lock()
fps_counter = 0
fps_start_time = time.time()
current_fps = 0

# Initialize components
camera = None
hailo_detector = None
ball_tracker = None

def initialize_camera():
    """Initialize Pi Camera"""
    global camera
    try:
        camera = Picamera2()
        
        # Configure camera - using config settings
        config_dict = camera.create_preview_configuration(
            main={"size": config.CAMERA_RESOLUTION, "format": config.CAMERA_FORMAT}
        )
        camera.configure(config_dict)
        
        # Set camera controls
        camera.set_controls({
            "FrameRate": config.CAMERA_FRAMERATE,
            "ExposureTime": 10000,  # Fast exposure for better tracking
            "AnalogueGain": 2.0
        })
        
        camera.start()
        time.sleep(2)  # Let camera warm up
        
        print(f"Camera initialized: {config.CAMERA_RESOLUTION[0]}x{config.CAMERA_RESOLUTION[1]} @ {config.CAMERA_FRAMERATE}fps")
        return True
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False

def initialize_hailo():
    """Initialize Hailo detector"""
    global hailo_detector
    if not HAILO_AVAILABLE:
        return False
    
    try:
        hailo_detector = HailoObjectDetector(
            model_path=config.MODEL_PATH,
            input_size=config.INPUT_SIZE,
            confidence_threshold=config.CONFIDENCE_THRESHOLD,
            nms_threshold=config.NMS_THRESHOLD,
            max_detections=config.MAX_DETECTIONS
        )
        print("Hailo detector initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing Hailo detector: {e}")
        return False

def initialize_tracker():
    """Initialize enhanced ball tracker"""
    global ball_tracker
    if not TRACKER_AVAILABLE:
        return False
    
    try:
        ball_tracker = EnhancedBallTracker()
        print("Enhanced ball tracker initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing ball tracker: {e}")
        return False

def camera_thread():
    """Camera capture thread"""
    global current_frame, fps_counter, fps_start_time, current_fps
    
    while camera:
        try:
            # Capture frame
            frame = camera.capture_array()
            
            with frame_lock:
                current_frame = frame.copy()
            
            # Calculate FPS
            fps_counter += 1
            if fps_counter % 30 == 0:
                elapsed = time.time() - fps_start_time
                if elapsed > 0:
                    current_fps = 30 / elapsed
                fps_start_time = time.time()
            
            time.sleep(1.0 / config.CAMERA_FRAMERATE)
            
        except Exception as e:
            print(f"Camera thread error: {e}")
            time.sleep(0.1)

def detection_thread():
    """Ball detection and tracking thread"""
    global current_frame, detections
    
    while True:
        try:
            if hailo_detector and current_frame is not None and ball_tracker:
                with frame_lock:
                    frame = current_frame.copy()
                
                # Convert RGB to BGR for Hailo
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Resize for Hailo if needed
                frame_height, frame_width = bgr_frame.shape[:2]
                if (frame_width, frame_height) != config.INPUT_SIZE:
                    hailo_frame = cv2.resize(bgr_frame, config.INPUT_SIZE)
                    needs_scaling = True
                    scale_x = frame_width / config.INPUT_SIZE[0]
                    scale_y = frame_height / config.INPUT_SIZE[1]
                else:
                    hailo_frame = bgr_frame
                    needs_scaling = False
                
                # Run detection
                new_detections = hailo_detector.detect(hailo_frame)
                
                # Filter for sports ball and find best detection
                best_ball = None
                filtered_detections = []
                
                if new_detections:
                    for det in new_detections:
                        class_name = det['class_name'].lower()
                        if 'ball' in class_name and det['confidence'] >= config.CONFIDENCE_THRESHOLD:
                            # Scale detection back to camera resolution if needed
                            if needs_scaling:
                                bbox = det['bbox']
                                x1, y1, x2, y2 = bbox
                                det['bbox'] = (
                                    int(x1 * scale_x),
                                    int(y1 * scale_y),
                                    int(x2 * scale_x),
                                    int(y2 * scale_y)
                                )
                            
                            filtered_detections.append(det)
                            
                            # Find the largest/most confident ball
                            bbox = det['bbox']
                            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                            if best_ball is None or area > best_ball['area']:
                                ball_x = (bbox[0] + bbox[2]) // 2
                                ball_y = (bbox[1] + bbox[3]) // 2
                                best_ball = {
                                    'x': ball_x,
                                    'y': ball_y,
                                    'area': area,
                                    'confidence': det['confidence'],
                                    'bbox': bbox
                                }
                
                # Update detections
                with frame_lock:
                    detections = filtered_detections
                
                # Track the best ball
                if best_ball and ball_tracker.is_tracking():
                    ball_tracker.track_target(
                        best_ball['x'], 
                        best_ball['y'], 
                        best_ball['area'],
                        frame_width, 
                        frame_height
                    )
                    print(f"Tracking ball at ({best_ball['x']}, {best_ball['y']}) "
                          f"area={best_ball['area']} conf={best_ball['confidence']:.2f}")
            
            time.sleep(1.0 / config.DETECTION_FPS)
            
        except Exception as e:
            print(f"Detection thread error: {e}")
            time.sleep(0.1)

def generate_frames():
    """Generate video frames for streaming"""
    global current_frame, detections
    
    while True:
        if current_frame is not None:
            with frame_lock:
                frame = current_frame.copy()
                current_detections = detections.copy()
            
            # Draw detections
            for det in current_detections:
                bbox = det['bbox']
                x1, y1, x2, y2 = bbox
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{det['class_name']}: {det['confidence']:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Draw center point
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
            
            # Draw frame center crosshair
            height, width = frame.shape[:2]
            center_x = width // 2
            center_y = height // 2
            cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (255, 255, 255), 1)
            cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (255, 255, 255), 1)
            
            # Add status text
            status_text = f"FPS: {current_fps:.1f}"
            if ball_tracker:
                if ball_tracker.is_tracking():
                    status_text += " | TRACKING: ON"
                    if config.ENABLE_MOTOR_FOLLOWING:
                        status_text += " | FOLLOWING: ON"
                else:
                    status_text += " | TRACKING: OFF"
            
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame, 
                                     [cv2.IMWRITE_JPEG_QUALITY, config.JPEG_QUALITY])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        time.sleep(1.0 / 30)  # Limit streaming FPS

# Web interface
@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Ball Tracking Robot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .video-container { text-align: center; margin-bottom: 20px; }
        .controls { display: flex; gap: 10px; justify-content: center; margin: 20px 0; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .status { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .settings { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
        input[type="range"] { width: 200px; }
        .emergency { background: #ff4444; color: white; font-weight: bold; padding: 15px; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏓 Enhanced Ball Tracking Robot</h1>
        
        <div class="video-container">
            <img src="{{ url_for('video_feed') }}" style="max-width: 100%; border: 2px solid #ddd; border-radius: 5px;">
        </div>
        
        <div class="controls">
            <button class="btn btn-success" onclick="startTracking()">Start Tracking</button>
            <button class="btn btn-danger" onclick="stopTracking()">Stop Tracking</button>
            <button class="btn btn-primary" onclick="centerCamera()">Center Camera</button>
            <button class="btn btn-warning" onclick="toggleMotors()">Toggle Motors</button>
        </div>
        
        <div class="emergency">
            <button class="btn btn-danger" onclick="emergencyStop()" style="font-size: 20px; padding: 15px 30px;">
                🛑 EMERGENCY STOP
            </button>
        </div>
        
        <div class="status" id="status">
            <h3>System Status</h3>
            <div id="status-content">Loading...</div>
        </div>
        
        <div class="settings">
            <h3>Settings</h3>
            <label>Motor Speed: <input type="range" id="motorSpeed" min="20" max="80" value="40" onchange="updateMotorSpeed()"> <span id="motorSpeedValue">40</span>%</label><br><br>
            <label>Detection Threshold: <input type="range" id="confidence" min="0.1" max="0.9" step="0.1" value="0.5" onchange="updateConfidence()"> <span id="confidenceValue">0.5</span></label>
        </div>
    </div>

    <script>
        function startTracking() {
            fetch('/start_tracking', {method: 'POST'})
                .then(response => response.json())
                .then(data => console.log('Start tracking:', data));
        }

        function stopTracking() {
            fetch('/stop_tracking', {method: 'POST'})
                .then(response => response.json())
                .then(data => console.log('Stop tracking:', data));
        }

        function centerCamera() {
            fetch('/center_camera', {method: 'POST'})
                .then(response => response.json())
                .then(data => console.log('Center camera:', data));
        }

        function toggleMotors() {
            fetch('/toggle_motors', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log('Toggle motors:', data);
                    updateStatus();
                });
        }

        function emergencyStop() {
            fetch('/emergency_stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log('Emergency stop:', data);
                    alert('EMERGENCY STOP ACTIVATED');
                    updateStatus();
                });
        }

        function updateMotorSpeed() {
            const speed = document.getElementById('motorSpeed').value;
            document.getElementById('motorSpeedValue').textContent = speed;
            fetch('/set_motor_speed', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({speed: parseInt(speed)})
            });
        }

        function updateConfidence() {
            const confidence = document.getElementById('confidence').value;
            document.getElementById('confidenceValue').textContent = confidence;
            fetch('/set_confidence', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({confidence: parseFloat(confidence)})
            });
        }

        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status-content');
                    statusDiv.innerHTML = `
                        <strong>Tracking:</strong> ${data.tracking_active ? 'ACTIVE' : 'INACTIVE'}<br>
                        <strong>Motor Following:</strong> ${data.motor_following ? 'ENABLED' : 'DISABLED'}<br>
                        <strong>Movement:</strong> ${data.movement_active ? 'ACTIVE' : 'STOPPED'}<br>
                        <strong>Camera Pan:</strong> ${data.servo_pan}°<br>
                        <strong>Camera Tilt:</strong> ${data.servo_tilt}°<br>
                        <strong>Last Ball:</strong> ${data.last_ball_position ? `(${data.last_ball_position[0]}, ${data.last_ball_position[1]})` : 'None'}<br>
                        <strong>Ball Area:</strong> ${data.last_ball_area} pixels
                    `;
                })
                .catch(error => console.error('Status update error:', error));
        }

        // Update status every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_tracking', methods=['POST'])
def start_tracking():
    if ball_tracker:
        ball_tracker.start_tracking()
        return jsonify({"status": "success", "message": "Tracking started"})
    return jsonify({"status": "error", "message": "Tracker not available"})

@app.route('/stop_tracking', methods=['POST'])
def stop_tracking():
    if ball_tracker:
        ball_tracker.stop_tracking()
        return jsonify({"status": "success", "message": "Tracking stopped"})
    return jsonify({"status": "error", "message": "Tracker not available"})

@app.route('/center_camera', methods=['POST'])
def center_camera():
    if ball_tracker:
        ball_tracker.center_camera()
        return jsonify({"status": "success", "message": "Camera centered"})
    return jsonify({"status": "error", "message": "Tracker not available"})

@app.route('/toggle_motors', methods=['POST'])
def toggle_motors():
    global config
    config.ENABLE_MOTOR_FOLLOWING = not config.ENABLE_MOTOR_FOLLOWING
    status = "enabled" if config.ENABLE_MOTOR_FOLLOWING else "disabled"
    return jsonify({"status": "success", "message": f"Motor following {status}", "enabled": config.ENABLE_MOTOR_FOLLOWING})

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    if ball_tracker:
        ball_tracker.emergency_stop()
        return jsonify({"status": "success", "message": "Emergency stop activated"})
    return jsonify({"status": "error", "message": "Tracker not available"})

@app.route('/set_motor_speed', methods=['POST'])
def set_motor_speed():
    data = request.get_json()
    config.MOTOR_FOLLOW_SPEED = data['speed']
    return jsonify({"status": "success", "speed": config.MOTOR_FOLLOW_SPEED})

@app.route('/set_confidence', methods=['POST'])
def set_confidence():
    data = request.get_json()
    config.CONFIDENCE_THRESHOLD = data['confidence']
    return jsonify({"status": "success", "confidence": config.CONFIDENCE_THRESHOLD})

@app.route('/status')
def status():
    if ball_tracker:
        return jsonify(ball_tracker.get_status())
    return jsonify({"error": "Tracker not available"})

def main():
    """Main function"""
    print("=== Enhanced Ball Tracking Robot ===")
    print("Features:")
    print("- Hailo NPU ball detection")
    print("- Camera servo tracking")
    print("- Robot movement following")
    print("- Web interface control")
    print()
    
    # Initialize components
    if not initialize_camera():
        print("Failed to initialize camera")
        return
    
    if not initialize_hailo():
        print("Warning: Hailo detector not available")
    
    if not initialize_tracker():
        print("Warning: Enhanced tracker not available")
    
    # Start threads
    camera_thread_obj = threading.Thread(target=camera_thread, daemon=True)
    detection_thread_obj = threading.Thread(target=detection_thread, daemon=True)
    
    camera_thread_obj.start()
    detection_thread_obj.start()
    
    print("System initialized successfully!")
    print("Web interface: http://localhost:5000")
    print("Press Ctrl+C to exit")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        if ball_tracker:
            ball_tracker.cleanup()
        if camera:
            camera.stop()

if __name__ == "__main__":
    main()
