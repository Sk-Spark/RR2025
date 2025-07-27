#!/usr/bin/env python3
"""
Ping Pong Ball Tracking System
Real-time ball tracking using RPi AI Hat, camera, and servo-controlled pan-tilt mechanism

This system integrates:
- Hailo NPU for object detection via RPi AI Hat
- Color-based ball detection as fallback
- SG90 servo control for pan-tilt camera movement
- Flask web interface for monitoring and control
- Real-time video streaming with overlays

Author: Ball Tracking System
Date: 2025
Optimized for: Raspberry Pi 5 with RPi AI Hat
"""

import sys
import os
import signal
import time
import logging
import argparse
from typing import Optional

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'HailoNPU_POC'))

# Import configuration first
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import our modules
from camera_manager import CameraManager
from servo_controller import BallTrackingServoController
from ball_detector import HailoBallDetector, BallDetector
from ball_tracker import BallTracker
from web_interface import WebServer
from motor_controller import MotorController

# Global system components
camera_manager: Optional[CameraManager] = None
servo_controller: Optional[BallTrackingServoController] = None
motor_controller: Optional[MotorController] = None
ball_detector: Optional[BallDetector] = None
ball_tracker: Optional[BallTracker] = None
web_server: Optional[WebServer] = None


def initialize_system():
    """Initialize all system components"""
    global camera_manager, servo_controller, motor_controller, ball_detector, ball_tracker, web_server
    
    logger.info("Initializing ping pong ball tracking system...")
    
    try:
        # Initialize camera manager
        logger.info("Initializing camera...")
        camera_manager = CameraManager()
        
        # Initialize servo controller with real hardware
        logger.info("Initializing servo controller...")
        servo_controller = BallTrackingServoController()
        
        # Initialize motor controller for robot following (if enabled)
        motor_controller = None
        if config.ENABLE_MOTOR_FOLLOWING:
            try:
                logger.info("Initializing motor controller...")
                motor_controller = MotorController(
                    motor_config=config.MOTOR_CONFIG,
                    i2c_address=config.PCA9685_ADDRESS,
                    frequency=config.MOTOR_PWM_FREQUENCY
                )
                logger.info("Motor controller initialized - robot will follow ball")
            except Exception as e:
                logger.warning(f"Could not initialize motor controller: {e}")
                logger.warning("Camera tracking will work, but robot won't move")
                config.ENABLE_MOTOR_FOLLOWING = False
        else:
            logger.info("Motor following disabled in config")
        
        # Initialize ball detector
        logger.info("Initializing ball detector...")
        ball_detector = HailoBallDetector()
        logger.info("Using Hailo NPU ball detection")
        
        # Initialize ball tracker
        logger.info("Initializing ball tracker...")
        ball_tracker = BallTracker(camera_manager, servo_controller, ball_detector, motor_controller)
        
        # Initialize web server
        logger.info("Initializing web server...")
        web_server = WebServer(ball_tracker)
        
        logger.info("System initialization complete!")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        cleanup_system()
        raise


def start_system():
    """Start all system components"""
    global web_server
    
    logger.info("Starting ping pong ball tracking system...")
    
    try:
        # Start web server
        if web_server:
            web_server.start()
            logger.info(f"Web interface available at: {web_server.get_url()}")
        
        logger.info("System started successfully!")
        logger.info("=" * 50)
        logger.info("PING PONG BALL TRACKING SYSTEM READY")
        logger.info("=" * 50)
        logger.info(f"Web Interface: {web_server.get_url() if web_server else 'N/A'}")
        logger.info(f"Camera Resolution: {config.CAMERA_RESOLUTION}")
        logger.info(f"Detection Method: Hailo NPU")
        logger.info(f"Servo Channels: Pan={config.PAN_SERVO_CHANNEL}, Tilt={config.TILT_SERVO_CHANNEL}")
        logger.info(f"Motor Following: {'ENABLED' if config.ENABLE_MOTOR_FOLLOWING else 'DISABLED'}")
        if config.ENABLE_MOTOR_FOLLOWING:
            logger.info(f"Motor Channels: {config.MOTOR_CONFIG}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        cleanup_system()
        raise


def cleanup_system():
    """Cleanup all system components"""
    global camera_manager, servo_controller, motor_controller, ball_tracker, web_server
    
    logger.info("Cleaning up system...")
    
    try:
        # Stop ball tracker first
        if ball_tracker:
            ball_tracker.cleanup()
            ball_tracker = None
        
        # Stop web server
        if web_server:
            web_server.stop()
            web_server = None
        
        # Cleanup motor controller
        if motor_controller:
            motor_controller.cleanup()
            motor_controller = None
        
        # Cleanup servo controller
        if servo_controller:
            servo_controller.cleanup()
            servo_controller = None
        
        # Cleanup camera
        if camera_manager:
            camera_manager.cleanup()
            camera_manager = None
        
        logger.info("System cleanup complete")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down...")
    cleanup_system()
    sys.exit(0)


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Ping Pong Ball Tracking System')
    parser.add_argument('--no-web', action='store_true', 
                       help='Run without web interface (tracking only)')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Update log level if specified
    if args.log_level:
        logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize system
        initialize_system()
        
        # Start system
        if not args.no_web:
            start_system()
            # Auto-start tracking in web mode too
            logger.info("Auto-starting ball tracking...")
            if ball_tracker:
                ball_tracker.start_tracking()
                logger.info("🎯 Ball tracking system AUTO-STARTED!")
        else:
            logger.info("Running in no-web mode")
            # Start tracking immediately in no-web mode
            if ball_tracker:
                ball_tracker.start_tracking()
        
        # Main loop - keep the application running
        try:
            while True:
                time.sleep(1)
                
                # In no-web mode, print status periodically
                if args.no_web and ball_tracker:
                    status = ball_tracker.get_status()
                    if status['detection_count'] > 0:
                        logger.info(f"Detections: {status['detection_count']}, "
                                   f"Pan: {status['servos']['current_pan']:.1f}°, "
                                   f"Tilt: {status['servos']['current_tilt']:.1f}°")
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    finally:
        cleanup_system()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())