#!/bin/bash
# Activation script for MPU6050 Python virtual environment

echo "Activating MPU6050 Python virtual environment..."
source venv/bin/activate

echo "Virtual environment activated!"
echo "Python path: $(which python)"
echo "Installed packages:"
pip list

echo ""
echo "You can now run:"
echo "  python test_connection.py     - Test MPU6050 connection"
echo "  python mpu6050_reader.py      - Read sensor data in real-time"
echo "  python plotmpu.py             - GUI plotting application"
echo "  python data_logger.py         - Log data to CSV file"
echo "  python simple_example.py      - Basic usage example"
echo ""
echo "To deactivate, type: deactivate"
