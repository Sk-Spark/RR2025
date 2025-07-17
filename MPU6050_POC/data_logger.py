#!/usr/bin/env python3
"""
MPU6050 Data Logger Example
This script demonstrates how to log MPU6050 sensor data to a CSV file.
"""

import csv
import time
import signal
import sys
from datetime import datetime
from mpu6050 import MPU6050

class MPU6050Logger:
    """Class for logging MPU6050 data to CSV file"""
    
    def __init__(self, filename=None):
        """Initialize logger with optional filename"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mpu6050_data_{timestamp}.csv"
        
        self.filename = filename
        self.mpu = MPU6050()
        self.running = False
        
        # CSV headers
        self.headers = [
            'timestamp', 'accel_x', 'accel_y', 'accel_z',
            'gyro_x', 'gyro_y', 'gyro_z', 'temperature',
            'roll', 'pitch'
        ]
        
        self.setup_csv()
    
    def setup_csv(self):
        """Create CSV file and write headers"""
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)
        print(f"Logging data to: {self.filename}")
    
    def log_data(self, duration=60, sample_rate=10):
        """
        Log sensor data for specified duration
        
        Args:
            duration (int): Logging duration in seconds
            sample_rate (int): Samples per second
        """
        self.running = True
        sample_interval = 1.0 / sample_rate
        start_time = time.time()
        sample_count = 0
        
        print(f"Logging for {duration} seconds at {sample_rate}Hz...")
        print("Press Ctrl+C to stop early")
        
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            while self.running and (time.time() - start_time) < duration:
                try:
                    # Get sensor data
                    data = self.mpu.get_all_data()
                    
                    # Extract values
                    ax = data['accelerometer']['x']
                    ay = data['accelerometer']['y']
                    az = data['accelerometer']['z']
                    
                    gx = data['gyroscope']['x']
                    gy = data['gyroscope']['y']
                    gz = data['gyroscope']['z']
                    
                    temp = data['temperature']
                    
                    # Calculate angles
                    roll, pitch = self.mpu.calculate_angles(ax, ay, az)
                    
                    # Create timestamp
                    timestamp = datetime.now().isoformat()
                    
                    # Write to CSV
                    row = [timestamp, ax, ay, az, gx, gy, gz, temp, roll, pitch]
                    writer.writerow(row)
                    
                    sample_count += 1
                    
                    # Display progress
                    elapsed = time.time() - start_time
                    if sample_count % (sample_rate * 5) == 0:  # Every 5 seconds
                        print(f"Logged {sample_count} samples ({elapsed:.1f}s)")
                    
                    time.sleep(sample_interval)
                    
                except KeyboardInterrupt:
                    break
        
        elapsed = time.time() - start_time
        print(f"\nLogging complete: {sample_count} samples in {elapsed:.1f}s")
        print(f"Data saved to: {self.filename}")
    
    def stop(self):
        """Stop logging"""
        self.running = False
        self.mpu.close()

def signal_handler(sig, frame, logger=None):
    """Handle Ctrl+C gracefully"""
    print('\nStopping logger...')
    if logger:
        logger.stop()
    sys.exit(0)

def main():
    """Main function for data logging example"""
    print("MPU6050 Data Logger")
    print("===================")
    
    try:
        # Create logger
        logger = MPU6050Logger()
        
        # Set up signal handler
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, logger))
        
        # Log data for 30 seconds at 10Hz
        logger.log_data(duration=30, sample_rate=10)
        
        logger.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        if 'logger' in locals():
            logger.stop()

if __name__ == "__main__":
    main()
