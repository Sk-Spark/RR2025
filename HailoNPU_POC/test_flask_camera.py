from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize camera with error handling
def init_camera():
    try:
        picam2 = Picamera2()
        
        # Configure camera for RGB888 output explicitly
        try:
            # Create video configuration with explicit RGB888 format
            config = picam2.create_video_configuration(
                main={"size": (640, 480), "format": "BGR888"}
            )
            picam2.configure(config)
            logger.info("Camera configured with RGB888 format")
        except (AttributeError, TypeError) as e:
            # Fallback for older versions - use preview configuration
            logger.info(f"Using fallback configuration for older picamera2 version: {e}")
            config = picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            picam2.configure(config)
        
        picam2.start()
        logger.info("Camera initialized successfully")
        return picam2
        
    except Exception as e:
        logger.error(f"Failed to initialize camera: {e}")
        return None

picam2 = init_camera()

def generate_frames():
    if picam2 is None:
        logger.error("Camera not initialized")
        return
    
    while True:
        try:
            # Capture frame from camera
            frame = picam2.capture_array()
            
            # picamera2 outputs RGB format by default
            # OpenCV's imencode expects BGR format for correct color encoding in JPEG
            # Convert RGB to BGR for proper color representation
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Encode frame as JPEG with BGR format
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not ret:
                logger.error("Failed to encode frame")
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
        except Exception as e:
            logger.error(f"Error generating frame: {e}")
            time.sleep(0.1)  # Small delay to prevent tight error loop

@app.route('/')
def index():
    camera_status = "✅ Camera Ready" if picam2 is not None else "❌ Camera Error"
    return f"""
    <html>
        <head>
            <title>RPi5 Camera Stream</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin: 20px; }}
                .status {{ padding: 10px; margin: 10px; border-radius: 5px; }}
                .ready {{ background-color: #d4edda; color: #155724; }}
                .error {{ background-color: #f8d7da; color: #721c24; }}
                img {{ border: 2px solid #ccc; border-radius: 10px; max-width: 90%; }}
            </style>
        </head>
        <body>
            <h1>Raspberry Pi 5 Camera Stream</h1>
            <div class="status {'ready' if picam2 else 'error'}">
                Status: {camera_status}
            </div>
            {f'<img src="/video_feed" alt="Camera Stream">' if picam2 else '<p>Camera not available</p>'}
        </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    if picam2 is None:
        return "Camera not available", 503
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """API endpoint to check camera status"""
    if picam2 is None:
        return {"status": "error", "message": "Camera not initialized"}, 503
    return {"status": "ok", "message": "Camera is running"}

if __name__ == "__main__":
    logger.info("Starting Flask camera server...")
    logger.info("Access the stream at: http://[RPi-IP]:5000")
    logger.info("Press Ctrl+C to stop")
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if picam2 is not None:
            picam2.stop()
            logger.info("Camera stopped")
