#!/usr/bin/env python3
"""
Configuration file for AI Bot Controller
"""

import os

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'aibot.log')

# Video configuration
VIDEO_WIDTH = int(os.getenv('VIDEO_WIDTH', '640'))
VIDEO_HEIGHT = int(os.getenv('VIDEO_HEIGHT', '480'))
FPS = int(os.getenv('FPS', '30'))

# Detection configuration
DETECTION_THRESHOLD = float(os.getenv('DETECTION_THRESHOLD', '0.5'))

# Network configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))

# Hardware configuration
HAILO_MODEL_PATH = os.getenv('HAILO_MODEL_PATH', '/usr/share/hailo-models/yolov5m.hef')

# Motor configuration
MOTOR_CONFIG = {
    "front_right": {"channel": 15, "in1": 14, "in2": 13},
    "front_left": {"channel": 4, "in1": 5, "in2": 6},
    "rear_right": {"channel": 10, "in1": 12, "in2": 11},
    "rear_left": {"channel": 9, "in1": 7, "in2": 8},
}

# Servo configuration
SERVO_CONFIG = {
    "camera_tilt": 3,
    "camera_pan": 2,
}

# I2C configuration
I2C_ADDRESS = int(os.getenv('I2C_ADDRESS', '0x40'), 16)

# MPU6050 configuration
MPU6050_ADDRESS = int(os.getenv('MPU6050_ADDRESS', '0x68'), 16)

# Default servo positions
DEFAULT_PAN_ANGLE = 90
DEFAULT_TILT_ANGLE = 90

# Movement parameters
DEFAULT_SPEED = 50
MAX_SPEED = 100
MIN_SPEED = 10

# Sensor update rates (Hz)
SENSOR_UPDATE_RATE = 10
STATUS_UPDATE_RATE = 1
