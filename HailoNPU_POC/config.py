# Configuration file for RPi AI Hat+ Object Detection
# Edit these values to customize the system behavior

# Camera settings
CAMERA_RESOLUTION = (640, 480)  # Width, Height
CAMERA_FRAMERATE = 30  # Frames per second
CAMERA_ROTATION = 0  # Rotation in degrees (0, 90, 180, 270)

# Model settings
MODEL_PATH = "resources/models/hailo8/yolov8m.hef"  # Path to Hailo model file
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detections
NMS_THRESHOLD = 0.4  # Non-maximum suppression threshold
INPUT_SIZE = (640, 640)  # Model input size

# Web server settings
WEB_HOST = "0.0.0.0"  # Host address (0.0.0.0 for all interfaces)
WEB_PORT = 5000  # Port number
DEBUG_MODE = False  # Enable Flask debug mode

# Performance settings
MAX_DETECTIONS = 100  # Maximum detections per frame
STREAM_QUALITY = 85  # JPEG quality for streaming (1-100)
BUFFER_SIZE = 2  # Number of frames to buffer

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "object_detection.log"  # Log file name
LOG_MAX_SIZE = 10  # Maximum log file size in MB
LOG_BACKUP_COUNT = 5  # Number of backup log files

# Hardware settings
ENABLE_HAILO = True  # Enable Hailo NPU acceleration
HAILO_DEVICE_ID = 0  # Hailo device ID (if multiple devices)
CPU_THREADS = 4  # Number of CPU threads for fallback processing

# Detection classes to filter (empty list means all classes)
# Example: FILTER_CLASSES = ["person", "car", "bicycle"]
FILTER_CLASSES = []

# Color scheme for bounding boxes (RGB values)
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
