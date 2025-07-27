# Configuration file for Ping Pong Ball Tracking System
# Edit these values to customize the system behavior

# Camera configuration - High resolution for better quality
CAMERA_RESOLUTION = (640, 640)  # Full resolution for better quality
CAMERA_FRAMERATE = 30
CAMERA_FORMAT = "RGB888"  # Explicit format specification
CAMERA_ROTATION = 0  # Rotation in degrees (0, 90, 180, 270)

# Performance optimization settings
DETECTION_FPS = 15          # Higher detection frequency for responsiveness
FRAME_SKIP = 1              # Process every frame for minimum latency
JPEG_QUALITY = 25           # JPEG quality for web streaming (lower = faster)
USE_FRAME_SKIPPING = False  # Disable frame skipping for maximum responsiveness

# Ball detection settings - Hailo NPU only
BALL_MIN_RADIUS = 10  # Minimum ball radius in pixels
BALL_MAX_RADIUS = 100  # Maximum ball radius in pixels

# Hailo NPU detection settings
USE_HAILO_DETECTION = True  # Always True - only Hailo NPU detection
HAILO_MODEL_PATH = "resources/models/hailo8/yolov8m.hef"  # Updated to match HailoNPU_POC
MODEL_PATH = "resources/models/hailo8/yolov8m.hef"  # For compatibility with Hailo detector
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detections
HAILO_CONFIDENCE_THRESHOLD = 0.5  # Legacy compatibility
NMS_THRESHOLD = 0.4  # Non-maximum suppression threshold
INPUT_SIZE = (640, 640)  # Model input size
MAX_DETECTIONS = 100  # Maximum detections per frame
HAILO_BALL_CLASS_NAME = "sports ball"  # COCO class name for sports ball

# PCA9685 control settings
PCA9685_ADDRESS = 0x40  # I2C address of PCA9685
PCA9685_FREQUENCY = 50  # PWM frequency in Hz for servos
MOTOR_PWM_FREQUENCY = 1000  # PWM frequency in Hz for motors
PAN_SERVO_CHANNEL = 2  # PCA9685 channel for pan servo
TILT_SERVO_CHANNEL = 3  # PCA9685 channel for tilt servo

# Motor configuration for ball following robot
ENABLE_MOTOR_FOLLOWING = True  # Enable robot movement to follow ball
MOTOR_CONFIG = {
    "front_right": {"channel": 15, "in1": 14, "in2": 13},
    "front_left": {"channel": 4, "in1": 5, "in2": 6},
    "rear_right": {"channel": 10, "in1": 12, "in2": 11},
    "rear_left": {"channel": 9, "in1": 7, "in2": 8},
}

# Servo angle limits
PAN_MIN_ANGLE = 0      # Minimum pan angle
PAN_MAX_ANGLE = 180    # Maximum pan angle
PAN_CENTER_ANGLE = 90  # Center pan angle
TILT_MIN_ANGLE = 45    # Minimum tilt angle (looking down)
TILT_MAX_ANGLE = 135   # Maximum tilt angle (looking up)
TILT_CENTER_ANGLE = 90 # Center tilt angle

# Tracking control settings
TRACKING_DEADZONE = 50  # Pixels from center to ignore (reduces jitter)
PAN_GAIN = 0.1         # Proportional gain for pan control
TILT_GAIN = 0.1        # Proportional gain for tilt control
PAN_SENSITIVITY = 15   # Degrees per full frame width
TILT_SENSITIVITY = 10  # Degrees per full frame height

# Motor control settings for ball following
MOTOR_FOLLOW_SPEED = 40        # Default speed for following movements (0-100)
MOTOR_DEADZONE_X = 0.15        # Horizontal deadzone as fraction of frame width
MOTOR_DEADZONE_Y = 0.15        # Vertical deadzone as fraction of frame height
MOTOR_MAX_SPEED = 60           # Maximum motor speed (0-100)
MOTOR_MIN_BALL_SIZE = 500      # Minimum ball area to start following
FOLLOW_DISTANCE_THRESHOLD = 0.3  # Ball size threshold to stop moving forward
MAX_SERVO_STEP = 5     # Maximum servo movement per frame (degrees)
SERVO_SMOOTHING = 0.3  # Smoothing factor for servo movement (0-1)
TRACKING_SMOOTH_TIME = 0.3  # Seconds for smooth tracking movements

# Web server settings
WEB_HOST = "0.0.0.0"  # Host address (0.0.0.0 for all interfaces)
WEB_PORT = 5000       # Port number
DEBUG_MODE = False    # Enable Flask debug mode

# Performance settings
STREAM_QUALITY = 85   # JPEG quality for streaming (1-100) - matched to HailoNPU_POC
PROCESSING_THREADS = 2  # Number of processing threads
BUFFER_SIZE = 2  # Number of frames to buffer
CPU_THREADS = 4  # Number of CPU threads for fallback processing

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "ball_tracking.log"  # Log file name
LOG_MAX_SIZE = 10  # Maximum log file size in MB
LOG_BACKUP_COUNT = 5  # Number of backup log files

# Hardware settings
ENABLE_HAILO = True  # Enable Hailo NPU acceleration
HAILO_DEVICE_ID = 0  # Hailo device ID (if multiple devices)

# Display settings
SHOW_DETECTION_INFO = True  # Show detection information on stream
DRAW_CENTER_CROSSHAIR = True  # Draw center crosshair
DRAW_DEADZONE = True         # Draw tracking deadzone
DETECTION_COLOR = (0, 255, 0)  # Green for ball detection
CROSSHAIR_COLOR = (255, 255, 255)  # White for crosshair
DEADZONE_COLOR = (255, 0, 0)    # Red for deadzone

# Detection classes to filter (empty list means all classes)
# Example: FILTER_CLASSES = ["person", "car", "bicycle"]
FILTER_CLASSES = []

# Color scheme for bounding boxes (RGB values) - from HailoNPU_POC
DETECTION_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
]
