#!/usr/bin/env python3
"""
MPU6050 I2C Connection Test
This script tests if the MPU6050 is properly connected and detectable on the I2C bus.
"""

import smbus2
import sys

def scan_i2c_devices(bus_number=1):
    """Scan I2C bus for connected devices"""
    print(f"Scanning I2C bus {bus_number}...")
    
    try:
        bus = smbus2.SMBus(bus_number)
        devices = []
        
        for address in range(0x03, 0x78):
            try:
                bus.read_byte(address)
                devices.append(address)
            except OSError:
                pass
        
        bus.close()
        return devices
        
    except Exception as e:
        print(f"Error accessing I2C bus: {e}")
        return []

def test_mpu6050_connection(bus_number=1, device_address=0x68):
    """Test specific MPU6050 connection"""
    print(f"Testing MPU6050 at address 0x{device_address:02X}...")
    
    try:
        bus = smbus2.SMBus(bus_number)
        
        # Try to read WHO_AM_I register (0x75)
        who_am_i = bus.read_byte_data(device_address, 0x75)
        
        # Wake up the device
        bus.write_byte_data(device_address, 0x6B, 0)
        
        # Read power management register to verify communication
        pwr_mgmt = bus.read_byte_data(device_address, 0x6B)
        
        bus.close()
        
        print(f"✓ MPU6050 found!")
        print(f"  WHO_AM_I: 0x{who_am_i:02X}")
        print(f"  Power Management: 0x{pwr_mgmt:02X}")
        return True
        
    except Exception as e:
        print(f"✗ MPU6050 not found at 0x{device_address:02X}: {e}")
        return False

def main():
    print("MPU6050 I2C Connection Test")
    print("============================\n")
    
    # Check if I2C is available
    try:
        bus = smbus2.SMBus(1)
        bus.close()
        print("✓ I2C bus accessible")
    except Exception as e:
        print(f"✗ Cannot access I2C bus: {e}")
        print("Make sure I2C is enabled using 'sudo raspi-config'")
        sys.exit(1)
    
    # Scan for devices
    devices = scan_i2c_devices()
    
    if devices:
        print(f"Found {len(devices)} I2C device(s):")
        for addr in devices:
            print(f"  0x{addr:02X}")
    else:
        print("No I2C devices found")
        print("Check your wiring:")
        print("  VCC -> 3.3V or 5V")
        print("  GND -> GND")
        print("  SCL -> GPIO 3 (Pin 5)")
        print("  SDA -> GPIO 2 (Pin 3)")
        sys.exit(1)
    
    print()
    
    # Test common MPU6050 addresses
    mpu_found = False
    for addr in [0x68, 0x69]:
        if addr in devices:
            if test_mpu6050_connection(device_address=addr):
                mpu_found = True
                break
    
    if not mpu_found:
        print("MPU6050 not found at standard addresses (0x68, 0x69)")
        if devices:
            print("Try checking these detected devices manually")
    else:
        print("\n✓ MPU6050 connection test passed!")
        print("You can now run mpu6050_reader.py")

if __name__ == "__main__":
    main()
