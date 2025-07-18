#!/usr/bin/env python3
"""
Simple MPU6050 Test Script for Raspberry Pi 5
Author: GitHub Copilot
Date: July 18, 2025

This script provides a simple test to verify MPU6050 sensor connectivity
and basic functionality without GUI dependencies.

Requirements:
- Enable I2C interface using raspi-config
- Install required packages: pip install smbus2
"""

import time
import sys
from mpu6050 import MPU6050

def test_mpu6050_connection():
    """Test MPU6050 sensor connection and basic functionality"""
    print("MPU6050 Connection Test")
    print("======================")
    
    try:
        # Initialize MPU6050
        print("Initializing MPU6050...")
        mpu = MPU6050()
        print("✓ MPU6050 initialized successfully")
        
        # Test reading sensor data
        print("\nTesting sensor readings...")
        
        for i in range(10):
            try:
                # Read all sensor data
                data = mpu.get_all_data()
                
                # Extract values
                ax = data['accelerometer']['x']
                ay = data['accelerometer']['y']
                az = data['accelerometer']['z']
                
                gx = data['gyroscope']['x']
                gy = data['gyroscope']['y']
                gz = data['gyroscope']['z']
                
                temp = data['temperature']
                
                # Calculate angles
                roll, pitch = mpu.calculate_angles(ax, ay, az)
                
                # Display data
                print(f"\nReading {i+1}/10:")
                print(f"  Accelerometer: X={ax:6.3f}g, Y={ay:6.3f}g, Z={az:6.3f}g")
                print(f"  Gyroscope:     X={gx:6.1f}°/s, Y={gy:6.1f}°/s, Z={gz:6.1f}°/s")
                print(f"  Temperature:   {temp:6.2f}°C")
                print(f"  Angles:        Roll={roll:6.1f}°, Pitch={pitch:6.1f}°")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"✗ Error reading sensor data: {e}")
                return False
        
        print("\n✓ All sensor readings successful!")
        
        # Test data validity
        print("\nValidating sensor data...")
        
        # Check if accelerometer magnitude is reasonable (should be ~1g when stationary)
        accel_magnitude = (ax**2 + ay**2 + az**2)**0.5
        if 0.8 <= accel_magnitude <= 1.2:
            print(f"✓ Accelerometer magnitude: {accel_magnitude:.3f}g (normal)")
        else:
            print(f"⚠ Accelerometer magnitude: {accel_magnitude:.3f}g (check sensor orientation)")
        
        # Check temperature range
        if -40 <= temp <= 85:
            print(f"✓ Temperature: {temp:.2f}°C (within valid range)")
        else:
            print(f"⚠ Temperature: {temp:.2f}°C (unusual value)")
        
        # Close connection
        mpu.close()
        print("\n✓ MPU6050 test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ MPU6050 test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
        print("2. Check wiring:")
        print("   - VCC -> 3.3V or 5V")
        print("   - GND -> GND")
        print("   - SCL -> GPIO 3 (Pin 5)")
        print("   - SDA -> GPIO 2 (Pin 3)")
        print("3. Install dependencies: pip install smbus2")
        print("4. Check I2C devices: i2cdetect -y 1")
        return False

def check_i2c_devices():
    """Check available I2C devices"""
    print("Checking I2C devices...")
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        if result.returncode == 0:
            print("I2C devices detected:")
            print(result.stdout)
            if "68" in result.stdout:
                print("✓ MPU6050 found at address 0x68")
            else:
                print("✗ MPU6050 not found at address 0x68")
        else:
            print("✗ Failed to run i2cdetect")
    except FileNotFoundError:
        print("✗ i2cdetect not found. Install with: sudo apt-get install i2c-tools")
    except Exception as e:
        print(f"✗ Error checking I2C devices: {e}")

def main():
    """Main function"""
    print("MPU6050 Simple Test Script")
    print("==========================")
    
    # Check I2C devices first
    check_i2c_devices()
    print()
    
    # Test MPU6050 connection
    success = test_mpu6050_connection()
    
    if success:
        print("\n🎉 MPU6050 is working correctly!")
        print("You can now run the data visualizer: python3 MpuDataVisualiser.py")
    else:
        print("\n❌ MPU6050 test failed. Please check your setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
