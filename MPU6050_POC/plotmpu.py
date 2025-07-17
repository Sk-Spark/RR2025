#!/usr/bin/env python3
"""
MPU6050 Real-time Data Plotter for Raspberry Pi 5
Author: GitHub Copilot
Date: July 17, 2025

This script creates a GUI window that displays real-time plots of MPU6050 sensor data:
- Accelerometer data (X, Y, Z axes)
- Gyroscope data (X, Y, Z axes)
- Temperature data
- Calculated roll and pitch angles

Requirements:
- matplotlib
- tkinter (usually comes with Python)
- MPU6050 sensor connected via I2C
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import time
from collections import deque
from mpu6050 import MPU6050

class MPU6050Plotter:
    """Real-time MPU6050 data plotter with GUI"""
    
    def __init__(self, window_size=100, update_interval=50):
        """
        Initialize the plotter
        
        Args:
            window_size (int): Number of data points to display
            update_interval (int): Update interval in milliseconds
        """
        self.window_size = window_size
        self.update_interval = update_interval
        
        # Initialize data buffers
        self.time_data = deque(maxlen=window_size)
        self.accel_x = deque(maxlen=window_size)
        self.accel_y = deque(maxlen=window_size)
        self.accel_z = deque(maxlen=window_size)
        self.gyro_x = deque(maxlen=window_size)
        self.gyro_y = deque(maxlen=window_size)
        self.gyro_z = deque(maxlen=window_size)
        self.temperature = deque(maxlen=window_size)
        self.roll = deque(maxlen=window_size)
        self.pitch = deque(maxlen=window_size)
        
        # Control variables
        self.running = False
        self.mpu = None
        self.data_thread = None
        self.start_time = None
        
        # Initialize GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI window and controls"""
        self.root = tk.Tk()
        self.root.title("MPU6050 Real-time Data Plotter")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Buttons
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_plotting)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_plotting, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(control_frame, text="Clear", command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Disconnected", foreground="red")
        self.status_label.pack(side=tk.RIGHT)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(control_frame, text="Settings")
        settings_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        ttk.Label(settings_frame, text="Update Rate (Hz):").pack(side=tk.LEFT)
        self.rate_var = tk.StringVar(value="20")
        rate_spinbox = ttk.Spinbox(settings_frame, from_=1, to=100, width=5, textvariable=self.rate_var)
        rate_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Create matplotlib figure
        self.setup_plots(main_frame)
        
    def setup_plots(self, parent):
        """Setup matplotlib plots"""
        # Create figure with subplots
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('MPU6050 Real-time Data', fontsize=16)
        
        # Accelerometer plot
        self.ax_accel = self.axes[0, 0]
        self.ax_accel.set_title('Accelerometer (g)')
        self.ax_accel.set_ylabel('Acceleration (g)')
        self.ax_accel.grid(True, alpha=0.3)
        self.ax_accel.legend(['X', 'Y', 'Z'], loc='upper right')
        
        # Gyroscope plot
        self.ax_gyro = self.axes[0, 1]
        self.ax_gyro.set_title('Gyroscope (°/s)')
        self.ax_gyro.set_ylabel('Angular velocity (°/s)')
        self.ax_gyro.grid(True, alpha=0.3)
        self.ax_gyro.legend(['X', 'Y', 'Z'], loc='upper right')
        
        # Temperature plot
        self.ax_temp = self.axes[1, 0]
        self.ax_temp.set_title('Temperature (°C)')
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.grid(True, alpha=0.3)
        
        # Angles plot
        self.ax_angles = self.axes[1, 1]
        self.ax_angles.set_title('Calculated Angles (°)')
        self.ax_angles.set_ylabel('Angle (°)')
        self.ax_angles.set_xlabel('Time (s)')
        self.ax_angles.grid(True, alpha=0.3)
        self.ax_angles.legend(['Roll', 'Pitch'], loc='upper right')
        
        plt.tight_layout()
        
        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def connect_sensor(self):
        """Connect to MPU6050 sensor"""
        try:
            print("Attempting to connect to MPU6050...")
            self.mpu = MPU6050()
            self.status_label.config(text="Status: Connected", foreground="green")
            print("✓ MPU6050 sensor connected successfully")
            
            # Test read to verify connection
            test_data = self.mpu.get_all_data()
            print(f"Test reading: Accel={test_data['accelerometer']}, Temp={test_data['temperature']:.1f}°C")
            return True
        except Exception as e:
            error_msg = f"Failed to connect to MPU6050:\n{e}\n\nMake sure:\n• I2C is enabled\n• MPU6050 is properly wired\n• Sensor is powered on"
            messagebox.showerror("Connection Error", error_msg)
            self.status_label.config(text="Status: Connection Failed", foreground="red")
            print(f"✗ Connection failed: {e}")
            return False
    
    def disconnect_sensor(self):
        """Disconnect from MPU6050 sensor"""
        if self.mpu and hasattr(self.mpu, 'close'):
            self.mpu.close()
            self.mpu = None
        self.status_label.config(text="Status: Disconnected", foreground="red")
    
    def data_collection_thread(self):
        """Thread function for collecting sensor data"""
        print("Data collection thread started")
        update_rate = float(self.rate_var.get())
        sleep_time = 1.0 / update_rate
        sample_count = 0
        
        while self.running and self.mpu:
            try:
                # Get current time
                current_time = time.time() - self.start_time
                
                # Read sensor data from real MPU6050
                if hasattr(self.mpu, 'get_all_data'):
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
                    
                    # Add to buffers
                    self.time_data.append(current_time)
                    self.accel_x.append(ax)
                    self.accel_y.append(ay)
                    self.accel_z.append(az)
                    self.gyro_x.append(gx)
                    self.gyro_y.append(gy)
                    self.gyro_z.append(gz)
                    self.temperature.append(temp)
                    self.roll.append(roll)
                    self.pitch.append(pitch)
                    
                    sample_count += 1
                    
                    # Debug output every 50 samples
                    if sample_count % 50 == 0:
                        print(f"Collected {sample_count} samples, buffer size: {len(self.time_data)}")
                        print(f"Latest data - Accel: ({ax:.3f}, {ay:.3f}, {az:.3f}), Gyro: ({gx:.2f}, {gy:.2f}, {gz:.2f}), Temp: {temp:.1f}°C")
                else:
                    print("Error: MPU6050 object doesn't have get_all_data method")
                    break
                
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"Data collection error: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
                break
        
        print(f"Data collection thread stopped. Total samples: {sample_count}")
    
    def update_plots(self, frame):
        """Update the plots with new data"""
        if not self.running:
            return
            
        if len(self.time_data) == 0:
            return
        
        # Print debug info every 50 frames
        if frame % 50 == 0:
            print(f"Updating plots - Frame: {frame}, Data points: {len(self.time_data)}")
            if len(self.time_data) > 0:
                print(f"Time range: {self.time_data[0]:.2f} to {self.time_data[-1]:.2f}s")
                print(f"Sample data - Accel X: {self.accel_x[-1]:.3f}, Temp: {self.temperature[-1]:.1f}°C")
        
        # Convert deques to numpy arrays for plotting
        time_array = np.array(self.time_data)
        
        # Clear all axes
        self.ax_accel.clear()
        self.ax_gyro.clear()
        self.ax_temp.clear()
        self.ax_angles.clear()
        
        # Plot accelerometer data
        self.ax_accel.plot(time_array, self.accel_x, 'r-', label='X', linewidth=1.5)
        self.ax_accel.plot(time_array, self.accel_y, 'g-', label='Y', linewidth=1.5)
        self.ax_accel.plot(time_array, self.accel_z, 'b-', label='Z', linewidth=1.5)
        self.ax_accel.set_title('Accelerometer (g)')
        self.ax_accel.set_ylabel('Acceleration (g)')
        self.ax_accel.grid(True, alpha=0.3)
        self.ax_accel.legend(loc='upper right')
        self.ax_accel.set_ylim(-3, 3)
        
        # Plot gyroscope data
        self.ax_gyro.plot(time_array, self.gyro_x, 'r-', label='X', linewidth=1.5)
        self.ax_gyro.plot(time_array, self.gyro_y, 'g-', label='Y', linewidth=1.5)
        self.ax_gyro.plot(time_array, self.gyro_z, 'b-', label='Z', linewidth=1.5)
        self.ax_gyro.set_title('Gyroscope (°/s)')
        self.ax_gyro.set_ylabel('Angular velocity (°/s)')
        self.ax_gyro.grid(True, alpha=0.3)
        self.ax_gyro.legend(loc='upper right')
        
        # Plot temperature data
        self.ax_temp.plot(time_array, self.temperature, 'orange', linewidth=2)
        self.ax_temp.set_title('Temperature (°C)')
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.grid(True, alpha=0.3)
        
        # Plot angles
        self.ax_angles.plot(time_array, self.roll, 'purple', label='Roll', linewidth=1.5)
        self.ax_angles.plot(time_array, self.pitch, 'cyan', label='Pitch', linewidth=1.5)
        self.ax_angles.set_title('Calculated Angles (°)')
        self.ax_angles.set_ylabel('Angle (°)')
        self.ax_angles.set_xlabel('Time (s)')
        self.ax_angles.grid(True, alpha=0.3)
        self.ax_angles.legend(loc='upper right')
        self.ax_angles.set_ylim(-180, 180)
        
        # Set common x-axis limits
        if len(time_array) > 0:
            x_min, x_max = time_array[0], time_array[-1]
            for ax in [self.ax_accel, self.ax_gyro, self.ax_temp, self.ax_angles]:
                ax.set_xlim(x_min, x_max)
        
        plt.tight_layout()
        
        # Force canvas update
        self.canvas.draw()
        self.canvas.flush_events()
        
        # Debug: Confirm plot update
        if frame % 50 == 0:
            print(f"Plot update complete for frame {frame}")
    
    def start_plotting(self):
        """Start data collection and plotting"""
        if not self.connect_sensor():
            return
        
        self.running = True
        self.start_time = time.time()
        
        # Start data collection thread
        self.data_thread = threading.Thread(target=self.data_collection_thread, daemon=True)
        self.data_thread.start()
        
        # Start tkinter-based plot updates instead of matplotlib animation
        self.update_plots_timer()
        
        # Update button states
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.status_label.config(text="Status: Running", foreground="blue")
    
    def update_plots_timer(self):
        """Timer-based plot update method"""
        if not self.running:
            return
            
        if len(self.time_data) > 0:
            self.update_plots_data()
        
        # Schedule next update
        self.root.after(self.update_interval, self.update_plots_timer)
    
    def update_plots_data(self):
        """Update the plots with current data"""
        if len(self.time_data) == 0:
            return
        
        # Convert deques to numpy arrays for plotting
        time_array = np.array(self.time_data)
        
        # Clear all axes
        self.ax_accel.clear()
        self.ax_gyro.clear()
        self.ax_temp.clear()
        self.ax_angles.clear()
        
        # Plot accelerometer data
        self.ax_accel.plot(time_array, self.accel_x, 'r-', label='X', linewidth=1.5)
        self.ax_accel.plot(time_array, self.accel_y, 'g-', label='Y', linewidth=1.5)
        self.ax_accel.plot(time_array, self.accel_z, 'b-', label='Z', linewidth=1.5)
        self.ax_accel.set_title('Accelerometer (g)')
        self.ax_accel.set_ylabel('Acceleration (g)')
        self.ax_accel.grid(True, alpha=0.3)
        self.ax_accel.legend(loc='upper right')
        self.ax_accel.set_ylim(-3, 3)
        
        # Plot gyroscope data
        self.ax_gyro.plot(time_array, self.gyro_x, 'r-', label='X', linewidth=1.5)
        self.ax_gyro.plot(time_array, self.gyro_y, 'g-', label='Y', linewidth=1.5)
        self.ax_gyro.plot(time_array, self.gyro_z, 'b-', label='Z', linewidth=1.5)
        self.ax_gyro.set_title('Gyroscope (°/s)')
        self.ax_gyro.set_ylabel('Angular velocity (°/s)')
        self.ax_gyro.grid(True, alpha=0.3)
        self.ax_gyro.legend(loc='upper right')
        
        # Plot temperature data
        self.ax_temp.plot(time_array, self.temperature, 'orange', linewidth=2)
        self.ax_temp.set_title('Temperature (°C)')
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.grid(True, alpha=0.3)
        
        # Plot angles
        self.ax_angles.plot(time_array, self.roll, 'purple', label='Roll', linewidth=1.5)
        self.ax_angles.plot(time_array, self.pitch, 'cyan', label='Pitch', linewidth=1.5)
        self.ax_angles.set_title('Calculated Angles (°)')
        self.ax_angles.set_ylabel('Angle (°)')
        self.ax_angles.set_xlabel('Time (s)')
        self.ax_angles.grid(True, alpha=0.3)
        self.ax_angles.legend(loc='upper right')
        self.ax_angles.set_ylim(-180, 180)
        
        # Set common x-axis limits
        if len(time_array) > 0:
            x_min, x_max = time_array[0], time_array[-1]
            for ax in [self.ax_accel, self.ax_gyro, self.ax_temp, self.ax_angles]:
                ax.set_xlim(x_min, x_max)
        
        plt.tight_layout()
        
        # Force canvas update
        self.canvas.draw()
        self.canvas.flush_events()
        
        # Debug output
        print(f"Plot updated - Data points: {len(time_array)}, Latest temp: {self.temperature[-1]:.1f}°C")
    
    def stop_plotting(self):
        """Stop data collection and plotting"""
        self.running = False
        
        if self.data_thread and self.data_thread.is_alive():
            self.data_thread.join(timeout=1.0)
        
        self.disconnect_sensor()
        
        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.status_label.config(text="Status: Stopped", foreground="orange")
    
    def clear_data(self):
        """Clear all data buffers and plots"""
        self.time_data.clear()
        self.accel_x.clear()
        self.accel_y.clear()
        self.accel_z.clear()
        self.gyro_x.clear()
        self.gyro_y.clear()
        self.gyro_z.clear()
        self.temperature.clear()
        self.roll.clear()
        self.pitch.clear()
        
        # Clear plots
        for ax in [self.ax_accel, self.ax_gyro, self.ax_temp, self.ax_angles]:
            ax.clear()
        
        self.setup_plots(self.root.children['!frame'])
        self.canvas.draw()
    
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            self.stop_plotting()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        print("MPU6050 Real-time Plotter")
        print("=========================")
        print("Click 'Start' to begin data collection and plotting")
        print("Use 'Stop' to pause, 'Clear' to reset data")
        print("Close the window to exit")
        
        self.root.mainloop()

def main():
    """Main function"""
    try:
        plotter = MPU6050Plotter(window_size=200, update_interval=50)
        plotter.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Application error:\n{e}")

if __name__ == "__main__":
    main()
