#!/bin/bash
# Setup script for MPU6050 project

echo "MPU6050 Project Setup"
echo "====================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the MPU6050_POC directory"
    exit 1
fi

echo "1. Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

echo "2. Activating virtual environment..."
source venv/bin/activate

echo "3. Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

echo "4. Installing system dependencies for GUI..."
sudo apt update > /dev/null 2>&1
sudo apt install python3-tk -y > /dev/null 2>&1

echo "5. Installing Python dependencies..."
pip install -r requirements.txt

echo "6. Testing installation..."
python -c "import smbus2; print('   ✓ smbus2 imported successfully')" 2>/dev/null || echo "   ✗ Error importing smbus2"

echo ""
echo "Setup complete!"
echo ""
echo "To use the project:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the scripts:"
echo "   python test_connection.py      # Test I2C connection"
echo "   python mpu6050_reader.py       # Real-time sensor reading"
echo "   python plotmpu.py              # GUI plotting application"
echo "   python data_logger.py          # Data logging to CSV"
echo "   python simple_example.py       # Basic usage example"
echo ""
echo "3. When finished, deactivate:"
echo "   deactivate"
