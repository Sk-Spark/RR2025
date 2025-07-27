"""
Web Interface Module
Flask-based web server for streaming video and controlling the tracking system
Lightweight interface optimized for real-time performance
"""

from flask import Flask, render_template, Response, jsonify, request
import logging
import threading
import time
import config

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ball_tracking_system'

# Global tracker instance
tracker = None


def create_app(ball_tracker):
    """Create Flask app with ball tracker instance"""
    global tracker
    tracker = ball_tracker
    return app


@app.route('/')
def index():
    """Main page with video stream and controls"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_frames():
    """Generate video frames for streaming"""
    while True:
        try:
            if tracker and tracker.camera_manager:
                # Get frame with overlays
                frame_bytes = tracker.camera_manager.get_frame_for_streaming()
                
                if frame_bytes:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    # Send a placeholder frame if no camera data
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error generating frame: {e}")
            time.sleep(0.1)


@app.route('/api/start_tracking', methods=['POST'])
def start_tracking():
    """Start ball tracking"""
    try:
        if tracker:
            tracker.start_tracking()
            return jsonify({'status': 'success', 'message': 'Tracking started'})
        else:
            return jsonify({'status': 'error', 'message': 'Tracker not initialized'}), 500
    except Exception as e:
        logger.error(f"Error starting tracking: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/stop_tracking', methods=['POST'])
def stop_tracking():
    """Stop ball tracking"""
    try:
        if tracker:
            tracker.stop_tracking_system()
            return jsonify({'status': 'success', 'message': 'Tracking stopped'})
        else:
            return jsonify({'status': 'error', 'message': 'Tracker not initialized'}), 500
    except Exception as e:
        logger.error(f"Error stopping tracking: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/center_camera', methods=['POST'])
def center_camera():
    """Center the camera servos"""
    try:
        if tracker and tracker.servo_controller:
            tracker.servo_controller.center_camera()
            return jsonify({'status': 'success', 'message': 'Camera centered'})
        else:
            return jsonify({'status': 'error', 'message': 'Servo controller not available'}), 500
    except Exception as e:
        logger.error(f"Error centering camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        if tracker:
            status = tracker.get_status()
            return jsonify({'status': 'success', 'data': status})
        else:
            return jsonify({'status': 'error', 'message': 'Tracker not initialized'}), 500
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        try:
            # Return current configuration
            config_data = {
                'camera_resolution': config.CAMERA_RESOLUTION,
                'camera_framerate': config.CAMERA_FRAMERATE,
                'tracking_deadzone': config.TRACKING_DEADZONE,
                'pan_gain': config.PAN_GAIN,
                'tilt_gain': config.TILT_GAIN,
                'max_servo_step': config.MAX_SERVO_STEP,
                'servo_smoothing': config.SERVO_SMOOTHING,
                'use_hailo_detection': config.USE_HAILO_DETECTION,
                'ball_min_radius': config.BALL_MIN_RADIUS,
                'ball_max_radius': config.BALL_MAX_RADIUS
            }
            return jsonify({'status': 'success', 'data': config_data})
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            # Update configuration (limited subset for safety)
            data = request.get_json()
            
            if 'tracking_deadzone' in data:
                config.TRACKING_DEADZONE = int(data['tracking_deadzone'])
            if 'pan_gain' in data:
                config.PAN_GAIN = float(data['pan_gain'])
            if 'tilt_gain' in data:
                config.TILT_GAIN = float(data['tilt_gain'])
            if 'max_servo_step' in data:
                config.MAX_SERVO_STEP = int(data['max_servo_step'])
            if 'servo_smoothing' in data:
                config.SERVO_SMOOTHING = float(data['servo_smoothing'])
            
            return jsonify({'status': 'success', 'message': 'Configuration updated'})
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500


class WebServer:
    """Web server manager"""
    
    def __init__(self, ball_tracker):
        """Initialize web server"""
        self.app = create_app(ball_tracker)
        self.server_thread = None
        self.running = False
        logger.info("Web server initialized")
    
    def start(self):
        """Start the web server"""
        if not self.running:
            self.running = True
            self.server_thread = threading.Thread(
                target=self._run_server, 
                daemon=True
            )
            self.server_thread.start()
            logger.info(f"Web server started on http://{config.WEB_HOST}:{config.WEB_PORT}")
    
    def _run_server(self):
        """Run the Flask server"""
        try:
            self.app.run(
                host=config.WEB_HOST,
                port=config.WEB_PORT,
                debug=config.DEBUG_MODE,
                threaded=True,
                use_reloader=False  # Disable reloader in production
            )
        except Exception as e:
            logger.error(f"Error running web server: {e}")
    
    def stop(self):
        """Stop the web server"""
        self.running = False
        if self.server_thread:
            # Note: Flask doesn't have a clean shutdown method
            # In production, you might want to use a proper WSGI server
            logger.info("Web server shutdown requested")
    
    def get_url(self):
        """Get the web server URL"""
        return f"http://{config.WEB_HOST}:{config.WEB_PORT}"
