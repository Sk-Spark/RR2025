"""
PCA9685 PWM Controller
Shared PCA9685 controller implementation for servos and motors
Based on proven implementation from Motors_Servo_POC
"""

import logging

logger = logging.getLogger(__name__)

# Hardware dependencies - required for real hardware
import board
import busio
from adafruit_pca9685 import PCA9685


class PCA9685Controller:
    """Real PCA9685 controller implementation based on Motors_Servo_POC"""
    
    def __init__(self, i2c_address=0x40, frequency=50):
        """
        Initialize PCA9685 controller with real hardware
        
        Args:
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            frequency (int): PWM frequency in Hz (default: 50Hz for servos)
        """
        logger.info(f"Initializing PCA9685 at I2C address {hex(i2c_address)}...")
        
        # Initialize I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize PCA9685
        self.pca = PCA9685(self.i2c, address=i2c_address)
        self.pca.frequency = frequency
        
        # Servo configuration for SG90 servos (same as Motors_Servo_POC)
        self.servo_min_pulse = 500   # Minimum pulse width in microseconds
        self.servo_max_pulse = 2500  # Maximum pulse width in microseconds
        self.servo_min_angle = 0     # Minimum angle in degrees
        self.servo_max_angle = 180   # Maximum angle in degrees
        
        # Store current positions
        self.current_positions = {}
        
        logger.info(f"PCA9685 Controller initialized successfully")
    
    def angle_to_pulse_width(self, angle):
        """Convert angle to pulse width in microseconds"""
        angle = max(self.servo_min_angle, min(self.servo_max_angle, angle))
        pulse_width = self.servo_min_pulse + (angle / self.servo_max_angle) * (self.servo_max_pulse - self.servo_min_pulse)
        return int(pulse_width)
    
    def pulse_width_to_duty_cycle(self, pulse_width_us):
        """Convert pulse width in microseconds to duty cycle value"""
        period_us = 1_000_000 / self.pca.frequency  # Period in microseconds
        duty_cycle = int((pulse_width_us / period_us) * 65535)
        return duty_cycle
    
    def set_pwm(self, channel, duty_cycle):
        """Set PWM duty cycle for a channel"""
        if duty_cycle == 0:
            self.pca.channels[channel].duty_cycle = 0
        else:
            self.pca.channels[channel].duty_cycle = duty_cycle
    
    def get_pwm(self, channel):
        """Get current PWM duty cycle for a channel"""
        return self.pca.channels[channel].duty_cycle
    
    def set_servo_angle(self, channel, angle):
        """Set servo to specific angle"""
        # Constrain angle
        angle = max(self.servo_min_angle, min(self.servo_max_angle, angle))
        
        # Convert angle to pulse width and duty cycle
        pulse_width = self.angle_to_pulse_width(angle)
        duty_cycle = self.pulse_width_to_duty_cycle(pulse_width)
        
        # Set PWM
        self.set_pwm(channel, duty_cycle)
        
        # Update position tracking
        self.current_positions[channel] = angle
        
        logger.debug(f"Servo channel {channel} set to {angle}° (pulse {pulse_width}μs)")
        
        return angle
