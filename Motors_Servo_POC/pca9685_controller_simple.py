"""
PCA9685 Controller Module (Simple I2C Implementation)
Direct I2C implementation for Raspberry Pi 5 compatibility
"""

import board
import busio
from adafruit_pca9685 import PCA9685


class PCA9685Controller:
    """Simple PCA9685 controller using direct I2C without gpiozero"""
    
    def __init__(self, i2c_address=0x40, frequency=50):
        """
        Initialize PCA9685 controller
        
        Args:
            i2c_address (int): I2C address of PCA9685 (default: 0x40)
            frequency (int): PWM frequency in Hz (default: 50Hz for servos)
        """
        try:
            print(f"Initializing PCA9685 at I2C address {hex(i2c_address)}...")
            
            # Initialize I2C bus directly
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685
            self.pca = PCA9685(self.i2c, address=i2c_address)
            self.pca.frequency = frequency
            
            print(f"PCA9685 initialized successfully at {frequency}Hz")
            
        except Exception as e:
            print(f"Error initializing PCA9685: {e}")
            raise
    
    def set_pwm(self, channel, duty_cycle):
        """
        Set PWM duty cycle for a channel
        
        Args:
            channel (int): PWM channel (0-15)
            duty_cycle (int): Duty cycle (0-65535)
        """
        try:
            self.pca.channels[channel].duty_cycle = duty_cycle
        except Exception as e:
            print(f"Error setting PWM on channel {channel}: {e}")
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
            return self.pca.channels[channel].duty_cycle
        except Exception as e:
            print(f"Error getting PWM on channel {channel}: {e}")
            return 0
    
    def set_pwm_pulse(self, channel, pulse_ms):
        """
        Set PWM pulse width in milliseconds
        
        Args:
            channel (int): PWM channel (0-15)
            pulse_ms (float): Pulse width in milliseconds
        """
        # Convert milliseconds to duty cycle
        # For 50Hz (20ms period), duty_cycle = (pulse_ms / 20) * 65535
        duty_cycle = int((pulse_ms / (1000 / self.pca.frequency)) * 65535)
        duty_cycle = max(0, min(65535, duty_cycle))  # Clamp to valid range
        self.set_pwm(channel, duty_cycle)
    
    def set_servo_angle(self, channel, angle):
        """
        Set servo angle (0-180 degrees)
        
        Args:
            channel (int): PWM channel (0-15)
            angle (float): Angle in degrees (0-180)
        """
        # Standard servo pulse widths: 0.5ms (0°) to 2.5ms (180°)
        angle = max(0, min(180, angle))  # Clamp angle
        pulse_ms = 0.5 + (angle / 180.0) * 2.0
        self.set_pwm_pulse(channel, pulse_ms)
    
    def set_motor_speed(self, channel, speed_percent):
        """
        Set motor speed (-100 to 100 percent)
        
        Args:
            channel (int): PWM channel (0-15)
            speed_percent (float): Speed percentage (-100 to 100)
        """
        # For motor controllers, typical range is 1ms to 2ms
        # 1.5ms = stop, 1ms = full reverse, 2ms = full forward
        speed_percent = max(-100, min(100, speed_percent))  # Clamp speed
        pulse_ms = 1.5 + (speed_percent / 100.0) * 0.5
        self.set_pwm_pulse(channel, pulse_ms)
    
    def stop_channel(self, channel):
        """Stop PWM output on a channel"""
        self.set_pwm(channel, 0)
    
    def stop_all(self):
        """Stop PWM output on all channels"""
        for channel in range(16):
            self.stop_channel(channel)
    
    def cleanup(self):
        """Cleanup PCA9685 controller"""
        try:
            self.stop_all()
            self.i2c.deinit()
            print("PCA9685 controller cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {e}")
