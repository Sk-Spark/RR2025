# MPU6050 Sensor Reader for Raspberry Pi 5

This project provides Python scripts to read accelerometer, gyroscope, and temperature data from an MPU6050 sensor connected to a Raspberry Pi 5 via I2C.

## Hardware Setup

### Wiring Connections
Connect the MPU6050 to your Raspberry Pi 5 as follows:

| MPU6050 Pin | RPi 5 Pin | Function |
|-------------|-----------|----------|
| VCC         | Pin 1 (3.3V) or Pin 2 (5V) | Power |
| GND         | Pin 6 (GND) | Ground |
| SCL         | Pin 5 (GPIO 3) | I2C Clock |
| SDA         | Pin 3 (GPIO 2) | I2C Data |

### Enable I2C Interface

1. Run the Raspberry Pi configuration tool:
   ```bash
   sudo raspi-config
   ```

2. Navigate to: `Interfacing Options` → `I2C` → `Yes`

3. Reboot your Raspberry Pi:
   ```bash
   sudo reboot
   ```

4. Verify I2C is enabled:
   ```bash
   lsmod | grep i2c_
   ```

## Software Setup

### Install Dependencies

1. Navigate to the project directory:
   ```bash
   cd /home/spark/RR2025/MPU6050_POC
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   Or use the provided activation script:
   ```bash
   source activate_venv.sh
   ```

3. Install system dependencies (for GUI plotting):
   ```bash
   sudo apt update
   sudo apt install python3-tk -y
   ```

4. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install smbus2 matplotlib numpy
   ```

**Note:** Always activate the virtual environment before running the scripts:
```bash
source venv/bin/activate
```

### Test Connection

Before running the main script, test if your MPU6050 is properly connected:

```bash
python3 test_connection.py
```

This will:
- Check if I2C is available
- Scan for I2C devices
- Test MPU6050 specific communication

## Usage

### Basic Usage

**Test the connection first:**
```bash
python3 test_connection.py
```

**Real-time sensor display:**
```bash
python3 mpu6050_reader.py
```
This displays real-time sensor data including accelerometer, gyroscope, temperature, and calculated roll/pitch angles. Press `Ctrl+C` to exit.

**Simple usage example:**
```bash
python3 simple_example.py
```
This shows basic usage of the MPU6050 class with 10 sensor readings.

**Data logging to CSV:**
```bash
python3 data_logger.py
```
This logs sensor data to a timestamped CSV file for 30 seconds at 10Hz.

**Real-time GUI plotting:**
```bash
python3 plotmpu.py
```
This opens a GUI window with real-time plots of all sensor data including accelerometer, gyroscope, temperature, and calculated angles. Features include:
- Start/Stop/Clear controls
- Adjustable update rate
- Multiple synchronized plots
- Real-time data visualization

**Advanced Data Visualizer:**
```bash
python3 MpuDataVisualiser.py
```
This opens an enhanced GUI with comprehensive real-time visualization featuring:
- Interactive start/stop controls
- Real-time value display
- Multiple synchronized plots (accelerometer, gyroscope, temperature, angles)
- Configurable data buffer size
- Professional matplotlib integration
- Thread-safe data collection

**Simple connection test:**
```bash
python3 test_mpu6050_simple.py
```
This performs a quick test to verify MPU6050 connectivity and basic functionality without GUI dependencies.

### Using the MPU6050 Class

You can import and use the MPU6050 class in your own scripts:

```python
from mpu6050 import MPU6050

# Initialize sensor
mpu = MPU6050()

# Read all data
data = mpu.get_all_data()
print(data)

# Read specific data
ax, ay, az = mpu.get_accelerometer_data()
gx, gy, gz = mpu.get_gyroscope_data()
temp = mpu.get_temperature()

# Calculate angles
roll, pitch = mpu.calculate_angles(ax, ay, az)

# Close connection
mpu.close()
```

## Files Description

- `mpu6050.py` - MPU6050 sensor class library (main module)
- `main.py` - Real-time sensor reading script with console display
- `MpuDataVisualiser.py` - Advanced GUI application for real-time data visualization
- `test_mpu6050_simple.py` - Simple connection test script without GUI dependencies
- `mpu6050_reader.py` - Real-time sensor reading script with display
- `plotmpu.py` - GUI application for real-time data plotting
- `test_connection.py` - I2C connection test script
- `data_logger.py` - Data logging to CSV example
- `simple_example.py` - Basic usage example of the MPU6050 class
- `requirements.txt` - Python dependencies
- `setup.sh` - Automated project setup script
- `activate_venv.sh` - Virtual environment activation script
- `README.md` - This documentation file

## Troubleshooting

### Common Issues

1. **"Permission denied" error:**
   ```bash
   sudo usermod -a -G i2c $USER
   # Then logout and login again
   ```

2. **"No such file or directory" for I2C:**
   - Ensure I2C is enabled in raspi-config
   - Check if i2c-dev module is loaded: `lsmod | grep i2c`

3. **MPU6050 not detected:**
   - Check wiring connections
   - Try different I2C address (0x69 instead of 0x68)
   - Verify power supply (3.3V or 5V)

4. **Erratic readings:**
   - Ensure stable power supply
   - Check for loose connections
   - Add pull-up resistors (4.7kΩ) on SDA and SCL lines if needed

### Manual I2C Detection

You can also use system tools to detect I2C devices:

```bash
# Install i2c-tools if not present
sudo apt update
sudo apt install i2c-tools

# Scan I2C bus
sudo i2cdetect -y 1
```

The MPU6050 should appear at address 0x68 or 0x69.

## Sensor Specifications

- **Accelerometer Range:** ±2g (configurable to ±4g, ±8g, ±16g)
- **Gyroscope Range:** ±250°/s (configurable to ±500°/s, ±1000°/s, ±2000°/s)
- **Temperature Range:** -40°C to +85°C
- **I2C Address:** 0x68 (or 0x69 if AD0 pin is high)
- **Supply Voltage:** 2.375V to 3.46V (or 5V with onboard regulator)

## License

This project is open source. Feel free to modify and distribute as needed.
