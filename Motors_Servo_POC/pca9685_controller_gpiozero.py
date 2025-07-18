"""
PCA9685 Controller Module (GPIO Zero Implementation)
Base class for managing PCA9685 16-channel PWM driver using gpiozero
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
from gpiozero import Device, Pin
from gpiozero.pins.lgpio import LGPIOFactory


class PCA9685Controller:
    """Base controller for PCA9685 PWM driver using gpiozero"""
    
    def __init__(self, i2c_address=0x40, frequency=50):
        """
        Initialize PCA9685 controller
        
        Args:
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            frequency (int): PWM frequency in Hz (default: 50Hz for servos)
        """
        try:
            # Set GPIO Zero to use lgpio for Raspberry Pi 5
            Device.pin_factory = LGPIOFactory()
            
            # Initialize I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685
            self.pca = PCA9685(i2c, address=i2c_address)
            self.pca.frequency = frequency
            
            print(f"PCA9685 initialized at address {hex(i2c_address)} with frequency {frequency}Hz")
            print("Using GPIO Zero with LGPIO for Raspberry Pi 5")
            
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
    
    def get_pwm(self, channel):
        """
        Get current PWM duty cycle for a specific channel
        
        Args:
            channel (int): Channel number (0-15)
            
        Returns:
            int: Current duty cycle value
        """
        if 0 <= channel <= 15:
            return self.pca.channels[channel].duty_cycle
        else:
            raise ValueError(f"Channel {channel} out of range (0-15)")
    
    def reset_channel(self, channel):
        """
        Reset a specific channel to 0
        
        Args:
            channel (int): Channel number (0-15)
        """
        self.set_pwm(channel, 0)
    
    def reset_all_channels(self):
        """Reset all channels to 0"""
        for channel in range(16):
            self.reset_channel(channel)
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.reset_all_channels()
            self.pca.deinit()
            print("PCA9685 cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")
