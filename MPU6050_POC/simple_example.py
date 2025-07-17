#!/usr/bin/env python3
"""
Simple MPU6050 Usage Example
This script demonstrates basic usage of the MPU6050 class.
"""

from mpu6050 import MPU6050
import time

def main():
    """Simple example of using MPU6050 class"""
    print("Simple MPU6050 Example")
    print("======================")
    
    try:
        # Initialize the sensor
        sensor = MPU6050()
        
        # Read data 10 times
        for i in range(10):
            print(f"\nReading {i+1}/10:")
            
            # Get individual sensor readings
            ax, ay, az = sensor.get_accelerometer_data()
            gx, gy, gz = sensor.get_gyroscope_data()
            temp = sensor.get_temperature()
            
            # Calculate angles
            roll, pitch = sensor.calculate_angles(ax, ay, az)
            
            print(f"  Accelerometer: X={ax:6.3f}g, Y={ay:6.3f}g, Z={az:6.3f}g")
            print(f"  Gyroscope:     X={gx:6.2f}°/s, Y={gy:6.2f}°/s, Z={gz:6.2f}°/s")
            print(f"  Temperature:   {temp:6.2f}°C")
            print(f"  Angles:        Roll={roll:6.2f}°, Pitch={pitch:6.2f}°")
            
            time.sleep(1)
        
        # Alternative: Get all data at once
        print(f"\nAll data at once:")
        data = sensor.get_all_data()
        print(f"  Data structure: {data}")
        
        # Close the connection
        sensor.close()
        print("\nSensor connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
