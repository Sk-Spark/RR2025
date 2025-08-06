#!/usr/bin/env python3
"""
PCA9685 Controller Module for AiBot
Simplified I2C implementation for Raspberry Pi 5 compatibility
"""

import logging

logger = logging.getLogger(__name__)

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    PCA9685_AVAILABLE = True
except ImportError:
    PCA9685_AVAILABLE = False
    logger.warning("PCA9685 libraries not available - running in simulation mode")


class PCA9685Controller:
    """PCA9685 controller using direct I2C for motor and servo control"""
    
    def __init__(self, i2c_address=0x40, frequency=50):
        """
        Initialize PCA9685 controller
        
        Args:
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            frequency (int): PWM frequency in Hz (default: 50Hz)
        """
        self.i2c_address = i2c_address
        self.frequency = frequency
        self.pca = None
        self.is_simulated = not PCA9685_AVAILABLE
        
        try:
            if not self.is_simulated:
                logger.info(f"Initializing PCA9685 at I2C address {hex(i2c_address)}...")
                
                # Initialize I2C bus directly
                self.i2c = busio.I2C(board.SCL, board.SDA)
                
                # Initialize PCA9685
                self.pca = PCA9685(self.i2c, address=i2c_address)
                self.pca.frequency = frequency
                
                logger.info(f"PCA9685 initialized successfully at {frequency}Hz")
            else:
                logger.warning("Running in simulation mode - no actual PCA9685 control")
            
        except Exception as e:
            logger.error(f"Failed to initialize PCA9685: {e}")
            logger.warning("Falling back to simulation mode")
            self.is_simulated = True
    
    def set_pwm(self, channel, duty_cycle):
        """
        Set PWM duty cycle for a channel
        
        Args:
            channel (int): PWM channel (0-15)
            duty_cycle (int): Duty cycle (0-65535)
        """
        try:
            if not self.is_simulated and self.pca:
                self.pca.channels[channel].duty_cycle = duty_cycle
                logger.debug(f"Channel {channel}: duty_cycle={duty_cycle}")
            else:
                logger.info(f"PCA9685 Channel {channel}: duty_cycle={duty_cycle} (simulated)")
        except Exception as e:
            logger.error(f"Error setting PWM on channel {channel}: {e}")
            raise
    
    def get_pwm(self, channel):
        """
        Get PWM duty cycle for a channel
        
        Args:
            channel (int): PWM channel (0-15)
            
        Returns:
            int: Current duty cycle (0-65535)
        """
        try:
            if not self.is_simulated and self.pca:
                return self.pca.channels[channel].duty_cycle
            else:
                logger.debug(f"Get PWM Channel {channel} (simulated)")
                return 0
        except Exception as e:
            logger.error(f"Error getting PWM on channel {channel}: {e}")
            return 0
    
    def cleanup(self):
        """Clean up PCA9685 resources"""
        try:
            if not self.is_simulated and self.pca:
                # Set all channels to 0
                for channel in range(16):
                    self.pca.channels[channel].duty_cycle = 0
                logger.info("PCA9685 channels reset to 0")
        except Exception as e:
            logger.error(f"Error during PCA9685 cleanup: {e}")
