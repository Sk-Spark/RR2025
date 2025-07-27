#!/usr/bin/env python3
"""
Simple Pi Camera Streaming
Lightweight camera streaming with minimal web UI
"""

from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time
import threading

# Camera Configuration Parameters
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 320
CAMERA_FORMAT = "RGB888"
CAMERA_FPS = 30

# Performance Optimization Parameters
DETECTION_FPS = 5           # Reduce detection frequency from 10 to 5 FPS
FRAME_SKIP = 3              # Process every 3rd frame for detection
JPEG_QUALITY = 40           # Lower JPEG quality for faster encoding

# Hailo Configuration - will be set dynamically from model
HAILO_INPUT_SIZE = 640  # Default fallback

# Import Hailo detector
try:
    from hailo_detector import HailoObjectDetector
    HAILO_AVAILABLE = True
    print("Hailo detector available")
except ImportError as e:
    print(f"Hailo detector not available: {e}")
    HAILO_AVAILABLE = False

app = Flask(__name__)

# Global variables for detection
current_frame = None
detections = []
frame_lock = threading.Lock()
fps_counter = 0
fps_start_time = time.time()
current_fps = 0
detection_frame_count = 0  # For frame skipping

# Initialize Hailo detector
hailo_detector = None
hailo_input_width = HAILO_INPUT_SIZE
hailo_input_height = HAILO_INPUT_SIZE

if HAILO_AVAILABLE:
    try:
        hailo_detector = HailoObjectDetector()
        if hailo_detector.initialize():
            print("Hailo detector initialized successfully")
            # Get actual input size from the model
            if hasattr(hailo_detector, 'model_w') and hasattr(hailo_detector, 'model_h'):
                hailo_input_width = hailo_detector.model_w
                hailo_input_height = hailo_detector.model_h
                print(f"Hailo model input size: {hailo_input_width}x{hailo_input_height}")
                
                # Show additional model info
                if hasattr(hailo_detector, 'hailo') and hailo_detector.hailo:
                    try:
                        input_shape = hailo_detector.hailo.get_input_shape()
                        print(f"Full input shape: {input_shape}")
                        print(f"Model path: {hailo_detector.model_path}")
                    except Exception as e:
                        print(f"Could not get additional model info: {e}")
            else:
                print(f"Using default Hailo input size: {HAILO_INPUT_SIZE}x{HAILO_INPUT_SIZE}")
        else:
            print("Failed to initialize Hailo detector")
            hailo_detector = None
    except Exception as e:
        print(f"Hailo initialization error: {e}")
        hailo_detector = None

# Initialize camera
def init_camera():
    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(
            main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT), "format": CAMERA_FORMAT},
            controls={"FrameRate": CAMERA_FPS}
        )
        picam2.configure(config)
        picam2.start()
        print(f"Camera initialized: {CAMERA_WIDTH}x{CAMERA_HEIGHT} {CAMERA_FORMAT} at {CAMERA_FPS} FPS")
        return picam2
    except Exception as e:
        print(f"Camera initialization failed: {e}")
        return None

picam2 = init_camera()

def detection_thread():
    """Background thread for Hailo detection with frame skipping"""
    global current_frame, detections, detection_frame_count
    
    while True:
        try:
            if hailo_detector and current_frame is not None:
                # Skip frames for better performance
                detection_frame_count += 1
                if detection_frame_count % FRAME_SKIP != 0:
                    time.sleep(1/DETECTION_FPS)
                    continue
                
                with frame_lock:
                    frame = current_frame.copy()
                
                # Convert RGB to BGR for Hailo (only once)
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Resize to Hailo input size if needed
                if (CAMERA_WIDTH, CAMERA_HEIGHT) != (hailo_input_width, hailo_input_height):
                    hailo_frame = cv2.resize(bgr_frame, (hailo_input_width, hailo_input_height))
                    needs_scaling = True
                else:
                    hailo_frame = bgr_frame
                    needs_scaling = False
                
                # Run detection
                new_detections = hailo_detector.detect(hailo_frame)
                
                # Filter for sports ball only - optimized
                filtered_detections = []
                if new_detections:
                    for det in new_detections:
                        class_name = det['class_name'].lower()
                        if 'ball' in class_name:  # Simplified check
                            filtered_detections.append(det)
                            print(f"Ball detected: {det['class_name']} ({det['confidence']:.2f})")
                    
                    # Scale detections back to camera resolution if needed
                    if needs_scaling and filtered_detections:
                        scale_x = CAMERA_WIDTH / hailo_input_width
                        scale_y = CAMERA_HEIGHT / hailo_input_height
                        
                        for det in filtered_detections:
                            bbox = det['bbox']
                            x1, y1, x2, y2 = bbox
                            det['bbox'] = (
                                int(x1 * scale_x),
                                int(y1 * scale_y),
                                int(x2 * scale_x),
                                int(y2 * scale_y)
                            )
                
                with frame_lock:
                    detections = filtered_detections
                    
            time.sleep(1/DETECTION_FPS)  # Reduced detection frequency
        except Exception as e:
            print(f"Detection error: {e}")
            time.sleep(0.1)

# Start detection thread
if hailo_detector:
    detection_thread = threading.Thread(target=detection_thread, daemon=True)
    detection_thread.start()
    print("Detection thread started")

def generate_frames():
    global current_frame, detections, fps_counter, fps_start_time, current_fps
    
    if picam2 is None:
        return
    
    while True:
        try:
            frame = picam2.capture_array()
            
            # Calculate FPS
            fps_counter += 1
            if time.time() - fps_start_time >= 1.0:
                current_fps = fps_counter / (time.time() - fps_start_time)
                fps_counter = 0
                fps_start_time = time.time()
            
            # Store frame for detection thread
            with frame_lock:
                current_frame = frame.copy()
                current_detections = detections.copy()
            
            # Draw detections on frame
            display_frame = frame.copy()
            for det in current_detections:
                bbox = det['bbox']
                class_name = det['class_name']
                confidence = det['confidence']
                
                x1, y1, x2, y2 = bbox
                
                # Draw bounding box (green)
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(display_frame, label, (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw FPS overlay (top-left corner)
            fps_text = f"FPS: {current_fps:.1f}"
            cv2.putText(display_frame, fps_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Encode frame as JPEG with optimized settings
            ret, buffer = cv2.imencode('.jpg', display_frame, [
                cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY,    # Lower quality for speed
                cv2.IMWRITE_JPEG_OPTIMIZE, 1,              # Optimize for size
                cv2.IMWRITE_JPEG_PROGRESSIVE, 0            # Disable progressive for speed
            ])
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
        except Exception as e:
            print(f"Error generating frame: {e}")
            time.sleep(0.01)  # Shorter delay

@app.route('/')
def index():
    hailo_status = "✅ Hailo Ready" if hailo_detector else "❌ Hailo Disabled"
    return f'''
    <html>
        <head><title>Sports Ball Detection</title></head>
        <body style="margin:0;text-align:center;background:#000;color:#fff;">
            <h2>🏓 Sports Ball Detection</h2>
            <p>{hailo_status}</p>
            <p style="color:#888;">Only detecting: Sports Ball, Ball objects</p>
            <img src="/video_feed" style="max-width:100%;height:auto;border:2px solid #333;">
        </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    if picam2 is None:
        return "Camera not available", 503
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("🚀 Starting Optimized Sports Ball Detection")
    print("=" * 50)
    print(f"Camera: {CAMERA_WIDTH}x{CAMERA_HEIGHT} @ {CAMERA_FPS} FPS")
    print(f"Detection: Every {FRAME_SKIP} frames @ {DETECTION_FPS} FPS")
    print(f"JPEG Quality: {JPEG_QUALITY}%")
    print("=" * 50)
    print("Access at: http://localhost:5000")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if picam2 is not None:
            picam2.stop()
        print("Camera stopped")
