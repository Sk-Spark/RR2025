#!/usr/bin/env python3
"""
MPU6050 Data Visualizer for Raspberry Pi 5
Author: GitHub Copilot
Date: July 18, 2025

This script creates a real-time visualization of MPU6050 sensor data
including accelerometer, gyroscope, and temperature readings with
interactive plots.

Connections:
- VCC -> 3.3V or 5V
- GND -> GND
- SCL -> GPIO 3 (Pin 5)
- SDA -> GPIO 2 (Pin 3)

Requirements:
- Enable I2C interface using raspi-config
- Install required packages: pip install smbus2 matplotlib numpy
"""

import time
import signal
import sys
import threading
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter as tk
from tkinter import ttk
from mpu6050 import MPU6050

class MPU6050Visualizer:
    """Real-time MPU6050 data visualizer with GUI"""
    
    def __init__(self, max_points=100):
        """
        Initialize the visualizer
        
        Args:
            max_points (int): Maximum number of data points to display
        """
        self.max_points = max_points
        self.running = False
        self.mpu = None
        
        # Data storage
        self.timestamps = deque(maxlen=max_points)
        self.accel_x = deque(maxlen=max_points)
        self.accel_y = deque(maxlen=max_points)
        self.accel_z = deque(maxlen=max_points)
        self.gyro_x = deque(maxlen=max_points)
        self.gyro_y = deque(maxlen=max_points)
        self.gyro_z = deque(maxlen=max_points)
        self.temperature = deque(maxlen=max_points)
        self.roll = deque(maxlen=max_points)
        self.pitch = deque(maxlen=max_points)
        
        # GUI setup
        self.setup_gui()
        
        # Data collection thread
        self.data_thread = None
        self.start_time = time.time()
        
    def setup_gui(self):
        """Set up the GUI interface"""
        self.root = tk.Tk()
        self.root.title("MPU6050 Data Visualizer")
        self.root.geometry("1200x800")
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start/Stop buttons
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_collection)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_collection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready to start")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Current values frame
        values_frame = ttk.LabelFrame(main_frame, text="Current Values")
        values_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create value labels
        self.value_labels = {}
        labels = [
            ("Accel X", "ax"), ("Accel Y", "ay"), ("Accel Z", "az"),
            ("Gyro X", "gx"), ("Gyro Y", "gy"), ("Gyro Z", "gz"),
            ("Temperature", "temp"), ("Roll", "roll"), ("Pitch", "pitch")
        ]
        
        for i, (label, key) in enumerate(labels):
            row = i // 3
            col = i % 3
            
            ttk.Label(values_frame, text=f"{label}:").grid(row=row, column=col*2, sticky=tk.W, padx=5, pady=2)
            self.value_labels[key] = ttk.Label(values_frame, text="0.000")
            self.value_labels[key].grid(row=row, column=col*2+1, sticky=tk.W, padx=5, pady=2)
        
        # Create matplotlib figure
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Configure subplots
        self.axes[0, 0].set_title("Accelerometer Data")
        self.axes[0, 0].set_ylabel("Acceleration (g)")
        self.axes[0, 0].grid(True, alpha=0.3)
        
        self.axes[0, 1].set_title("Gyroscope Data")
        self.axes[0, 1].set_ylabel("Angular Velocity (°/s)")
        self.axes[0, 1].grid(True, alpha=0.3)
        
        self.axes[1, 0].set_title("Temperature")
        self.axes[1, 0].set_ylabel("Temperature (°C)")
        self.axes[1, 0].grid(True, alpha=0.3)
        
        self.axes[1, 1].set_title("Roll & Pitch Angles")
        self.axes[1, 1].set_ylabel("Angle (°)")
        self.axes[1, 1].grid(True, alpha=0.3)
        
        # Initialize plot lines
        self.accel_lines = {
            'x': self.axes[0, 0].plot([], [], 'r-', label='X', linewidth=2)[0],
            'y': self.axes[0, 0].plot([], [], 'g-', label='Y', linewidth=2)[0],
            'z': self.axes[0, 0].plot([], [], 'b-', label='Z', linewidth=2)[0]
        }
        self.axes[0, 0].legend()
        
        self.gyro_lines = {
            'x': self.axes[0, 1].plot([], [], 'r-', label='X', linewidth=2)[0],
            'y': self.axes[0, 1].plot([], [], 'g-', label='Y', linewidth=2)[0],
            'z': self.axes[0, 1].plot([], [], 'b-', label='Z', linewidth=2)[0]
        }
        self.axes[0, 1].legend()
        
        self.temp_line = self.axes[1, 0].plot([], [], 'orange', linewidth=2)[0]
        
        self.angle_lines = {
            'roll': self.axes[1, 1].plot([], [], 'purple', label='Roll', linewidth=2)[0],
            'pitch': self.axes[1, 1].plot([], [], 'brown', label='Pitch', linewidth=2)[0]
        }
        self.axes[1, 1].legend()
        
        # Embed matplotlib in tkinter
        canvas = FigureCanvasTkAgg(self.fig, main_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Set up animation
        self.animation = animation.FuncAnimation(self.fig, self.update_plots, interval=100, blit=False)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def start_collection(self):
        """Start data collection"""
        try:
            self.mpu = MPU6050()
            self.running = True
            self.start_time = time.time()
            
            # Start data collection thread
            self.data_thread = threading.Thread(target=self.collect_data)
            self.data_thread.daemon = True
            self.data_thread.start()
            
            # Update GUI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Collecting data...")
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to initialize MPU6050: {e}")
            
    def stop_collection(self):
        """Stop data collection"""
        self.running = False
        if self.mpu:
            self.mpu.close()
        
        # Update GUI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")
        
    def collect_data(self):
        """Data collection thread function"""
        while self.running:
            try:
                if self.mpu:
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
                    
                    # Store data
                    current_time = time.time() - self.start_time
                    self.timestamps.append(current_time)
                    
                    self.accel_x.append(ax)
                    self.accel_y.append(ay)
                    self.accel_z.append(az)
                    
                    self.gyro_x.append(gx)
                    self.gyro_y.append(gy)
                    self.gyro_z.append(gz)
                    
                    self.temperature.append(temp)
                    self.roll.append(roll)
                    self.pitch.append(pitch)
                    
                    # Update value labels
                    self.root.after(0, self.update_value_labels, ax, ay, az, gx, gy, gz, temp, roll, pitch)
                    
                time.sleep(0.05)  # 20Hz data collection
                
            except Exception as e:
                print(f"Data collection error: {e}")
                self.running = False
                break
                
    def update_value_labels(self, ax, ay, az, gx, gy, gz, temp, roll, pitch):
        """Update the current value labels"""
        self.value_labels['ax'].config(text=f"{ax:7.3f} g")
        self.value_labels['ay'].config(text=f"{ay:7.3f} g")
        self.value_labels['az'].config(text=f"{az:7.3f} g")
        
        self.value_labels['gx'].config(text=f"{gx:7.2f} °/s")
        self.value_labels['gy'].config(text=f"{gy:7.2f} °/s")
        self.value_labels['gz'].config(text=f"{gz:7.2f} °/s")
        
        self.value_labels['temp'].config(text=f"{temp:6.2f} °C")
        self.value_labels['roll'].config(text=f"{roll:7.2f} °")
        self.value_labels['pitch'].config(text=f"{pitch:7.2f} °")
        
    def update_plots(self, frame):
        """Update the plots"""
        if len(self.timestamps) < 2:
            return
            
        times = list(self.timestamps)
        
        # Update accelerometer plot
        self.accel_lines['x'].set_data(times, list(self.accel_x))
        self.accel_lines['y'].set_data(times, list(self.accel_y))
        self.accel_lines['z'].set_data(times, list(self.accel_z))
        
        # Update gyroscope plot
        self.gyro_lines['x'].set_data(times, list(self.gyro_x))
        self.gyro_lines['y'].set_data(times, list(self.gyro_y))
        self.gyro_lines['z'].set_data(times, list(self.gyro_z))
        
        # Update temperature plot
        self.temp_line.set_data(times, list(self.temperature))
        
        # Update angle plots
        self.angle_lines['roll'].set_data(times, list(self.roll))
        self.angle_lines['pitch'].set_data(times, list(self.pitch))
        
        # Auto-scale axes
        for ax in self.axes.flat:
            ax.relim()
            ax.autoscale_view()
            
        # Set x-axis label for bottom plots
        self.axes[1, 0].set_xlabel("Time (s)")
        self.axes[1, 1].set_xlabel("Time (s)")
        
    def on_closing(self):
        """Handle window closing"""
        self.stop_collection()
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Run the visualizer"""
        print("MPU6050 Data Visualizer")
        print("=======================")
        print("Click 'Start' to begin data collection")
        print("Close the window to exit")
        
        self.root.mainloop()

def main():
    """Main function"""
    import tkinter.messagebox
    
    try:
        visualizer = MPU6050Visualizer(max_points=200)
        visualizer.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()