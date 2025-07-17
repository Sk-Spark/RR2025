#!/usr/bin/env python3
"""
MPU6050 Sensor Reader for Raspberry Pi 5
Author: GitHub Copilot
Date: July 17, 2025

This script reads accelerometer and gyroscope data from an MPU6050 sensor
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

import time
import signal
import sys
from mpu6050 import MPU6050

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\nShutting down...')
    if 'mpu' in globals():
        mpu.close()
    sys.exit(0)

def main():
    """Main function to demonstrate MPU6050 reading"""
    global mpu
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("MPU6050 Sensor Reader")
    print("====================")
    print("Press Ctrl+C to exit\n")
    
    try:
        # Initialize MPU6050
        mpu = MPU6050()
        
        # Continuous reading loop
        while True:
            # Get all sensor data
            data = mpu.get_all_data()
            
            # Extract values
            ax = data['accelerometer']['x']
            ay = data['accelerometer']['y']
            az = data['accelerometer']['z']
            
            gx = data['gyroscope']['x']
            gy = data['gyroscope']['y']
            gz = data['gyroscope']['z']
            
            temp = data['temperature']
            
            # Calculate roll and pitch
            roll, pitch = mpu.calculate_angles(ax, ay, az)
            
            # Clear screen and display data
            print("\033[H\033[J", end="")  # Clear screen
            print("MPU6050 Sensor Readings")
            print("========================")
            print(f"Accelerometer (g):")
            print(f"  X: {ax:7.3f}  Y: {ay:7.3f}  Z: {az:7.3f}")
            print()
            print(f"Gyroscope (°/s):")
            print(f"  X: {gx:7.2f}  Y: {gy:7.2f}  Z: {gz:7.2f}")
            print()
            print(f"Temperature: {temp:6.2f}°C")
            print()
            print(f"Calculated Angles:")
            print(f"  Roll:  {roll:7.2f}°")
            print(f"  Pitch: {pitch:7.2f}°")
            print()
            print("Press Ctrl+C to exit")
            
            time.sleep(0.1)  # 10Hz update rate
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"Error: {e}")
        if 'mpu' in globals():
            mpu.close()

if __name__ == "__main__":
    main()
