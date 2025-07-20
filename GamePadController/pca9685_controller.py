"""
PCA9685 Controller Module for Robot Control
Base class for managing PCA9685 16-channel PWM driver
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
try:
    from gpiozero import Device
    from gpiozero.pins.lgpio import LGPIOFactory
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False


class PCA9685Controller:
    """Base controller for PCA9685 PWM driver"""
    
    def __init__(self, i2c_address=0x40, frequency=50):
        """
        Initialize PCA9685 controller
        
        Args:
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            frequency (int): PWM frequency in Hz (default: 50Hz for servos)
        """
        try:
            # Set GPIO Zero to use lgpio for Raspberry Pi 5 if available
            if GPIOZERO_AVAILABLE:
                Device.pin_factory = LGPIOFactory()
                print("Using GPIO Zero with LGPIO for Raspberry Pi 5")
            
            # Initialize I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685
            self.pca = PCA9685(i2c, address=i2c_address)
            self.pca.frequency = frequency
            
            print(f"PCA9685 initialized at address {hex(i2c_address)} with frequency {frequency}Hz")
            
        except Exception as e:
            print(f"Error initializing PCA9685: {e}")
            raise
    
    def set_pwm(self, channel, duty_cycle):
        """
        Set PWM duty cycle for a specific channel
        
        Args:
            channel (int): Channel number (0-15)
            duty_cycle (int): Duty cycle value (0-65535)
        """
        if 0 <= channel <= 15:
            self.pca.channels[channel].duty_cycle = duty_cycle
        else:
            raise ValueError(f"Channel {channel} out of range (0-15)")
    
    def set_pulse_width(self, channel, pulse_width_us):
        """
        Set pulse width in microseconds for a specific channel
        
        Args:
            channel (int): Channel number (0-15)
            pulse_width_us (int): Pulse width in microseconds
        """
        # Convert microseconds to duty cycle
        # PCA9685 has 12-bit resolution (4096 steps)
        # At 50Hz, each step is 4.88us (20ms / 4096)
        pulse_length = 1000000 / self.pca.frequency  # Pulse length in microseconds
        duty_cycle = int((pulse_width_us / pulse_length) * 65535)
        self.set_pwm(channel, duty_cycle)
    
    def cleanup(self):
        """Cleanup PCA9685 - set all channels to 0"""
        for channel in range(16):
            self.set_pwm(channel, 0)
        print("PCA9685 cleanup completed")
