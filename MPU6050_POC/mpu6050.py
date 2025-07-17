#!/usr/bin/env python3
"""
MPU6050 Class for Raspberry Pi 5
Author: GitHub Copilot
Date: July 17, 2025

This module provides a class for interfacing with MPU6050 sensor
connected to a Raspberry Pi 5 via I2C interface.

Connections:
- VCC -> 3.3V or 5V
- GND -> GND
- SCL -> GPIO 3 (Pin 5)
- SDA -> GPIO 2 (Pin 3)

Requirements:
- Enable I2C interface using raspi-config
- Install required packages: pip install smbus2
"""

import smbus2
import math
import sys

class MPU6050:
    """Class for interfacing with MPU6050 sensor"""
    
    # MPU6050 Registers
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    INT_ENABLE = 0x38
    
    # Data Registers
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    TEMP_OUT_H = 0x41
    GYRO_XOUT_H = 0x43
    GYRO_YOUT_H = 0x45
    GYRO_ZOUT_H = 0x47
    
    def __init__(self, bus_number=1, device_address=0x68):
        """
        Initialize MPU6050 sensor
        
        Args:
            bus_number (int): I2C bus number (usually 1 for RPi)
            device_address (int): I2C address of MPU6050 (0x68 or 0x69)
        """
        self.bus_number = bus_number
        self.device_address = device_address
        self.bus = None
        
        # Sensitivity scale factors
        self.accel_scale = 16384.0  # for ±2g range
        self.gyro_scale = 131.0     # for ±250°/s range
        
        self.initialize_sensor()
    
    def initialize_sensor(self):
        """Initialize I2C bus and configure MPU6050"""
        try:
            self.bus = smbus2.SMBus(self.bus_number)
            
            # Wake up the sensor (it starts in sleep mode)
            self.bus.write_byte_data(self.device_address, self.PWR_MGMT_1, 0)
            
            # Set sample rate to 1kHz
            self.bus.write_byte_data(self.device_address, self.SMPLRT_DIV, 7)
            
            # Set accelerometer configuration (±2g)
            self.bus.write_byte_data(self.device_address, self.ACCEL_CONFIG, 0)
            
            # Set gyroscope configuration (±250°/s)
            self.bus.write_byte_data(self.device_address, self.GYRO_CONFIG, 0)
            
            # Set filter configuration
            self.bus.write_byte_data(self.device_address, self.CONFIG, 0)
            
            print(f"MPU6050 initialized successfully on I2C bus {self.bus_number}, address 0x{self.device_address:02X}")
            
        except Exception as e:
            print(f"Error initializing MPU6050: {e}")
            print("Make sure I2C is enabled and MPU6050 is properly connected")
            sys.exit(1)
    
    def read_raw_data(self, register):
        """
        Read 16-bit raw data from specified register
        
        Args:
            register (int): Register address to read from
            
        Returns:
            int: 16-bit signed integer value
        """
        # Read high and low bytes
        high = self.bus.read_byte_data(self.device_address, register)
        low = self.bus.read_byte_data(self.device_address, register + 1)
        
        # Combine bytes and convert to signed integer
        value = (high << 8) + low
        if value > 32768:
            value = value - 65536
        return value
    
    def get_accelerometer_data(self):
        """
        Read accelerometer data
        
        Returns:
            tuple: (ax, ay, az) in g units
        """
        ax_raw = self.read_raw_data(self.ACCEL_XOUT_H)
        ay_raw = self.read_raw_data(self.ACCEL_YOUT_H)
        az_raw = self.read_raw_data(self.ACCEL_ZOUT_H)
        
        # Convert to g units
        ax = ax_raw / self.accel_scale
        ay = ay_raw / self.accel_scale
        az = az_raw / self.accel_scale
        
        return ax, ay, az
    
    def get_gyroscope_data(self):
        """
        Read gyroscope data
        
        Returns:
            tuple: (gx, gy, gz) in degrees per second
        """
        gx_raw = self.read_raw_data(self.GYRO_XOUT_H)
        gy_raw = self.read_raw_data(self.GYRO_YOUT_H)
        gz_raw = self.read_raw_data(self.GYRO_ZOUT_H)
        
        # Convert to degrees per second
        gx = gx_raw / self.gyro_scale
        gy = gy_raw / self.gyro_scale
        gz = gz_raw / self.gyro_scale
        
        return gx, gy, gz
    
    def get_temperature(self):
        """
        Read temperature data
        
        Returns:
            float: Temperature in Celsius
        """
        temp_raw = self.read_raw_data(self.TEMP_OUT_H)
        # Convert to Celsius using MPU6050 formula
        temperature = (temp_raw / 340.0) + 36.53
        return temperature
    
    def get_all_data(self):
        """
        Read all sensor data at once
        
        Returns:
            dict: Dictionary containing all sensor readings
        """
        ax, ay, az = self.get_accelerometer_data()
        gx, gy, gz = self.get_gyroscope_data()
        temp = self.get_temperature()
        
        return {
            'accelerometer': {'x': ax, 'y': ay, 'z': az},
            'gyroscope': {'x': gx, 'y': gy, 'z': gz},
            'temperature': temp
        }
    
    def calculate_angles(self, ax, ay, az):
        """
        Calculate roll and pitch angles from accelerometer data
        
        Args:
            ax, ay, az: Accelerometer readings in g units
            
        Returns:
            tuple: (roll, pitch) in degrees
        """
        roll = math.atan2(ay, az) * 180 / math.pi
        pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az)) * 180 / math.pi
        return roll, pitch
    
    def close(self):
        """Close I2C bus connection"""
        if self.bus:
            self.bus.close()
