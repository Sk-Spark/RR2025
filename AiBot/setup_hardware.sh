#!/bin/bash
"""
AiBot Setup Script for Raspberry Pi 5
Ensures proper environment setup for hardware control
"""

echo "🤖 Setting up AiBot for Raspberry Pi 5..."

# Activate the Python virtual environment
echo "📦 Activating Python virtual environment..."
source /home/spark/.venv/bin/activate

# Check if we're running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Some hardware features may not work"
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r /home/spark/RR2025/AiBot/requirements.txt

# Enable I2C and GPIO if not already enabled
echo "🔧 Checking hardware interfaces..."
if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
    echo "   Enabling I2C interface..."
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
fi

if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "   Enabling SPI interface..."
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
fi

# Check if user is in gpio group
if ! groups $USER | grep -q gpio; then
    echo "   Adding user to gpio group..."
    sudo usermod -a -G gpio $USER
    echo "   ⚠️  Please log out and back in for group changes to take effect"
fi

# Check if user is in i2c group
if ! groups $USER | grep -q i2c; then
    echo "   Adding user to i2c group..."
    sudo usermod -a -G i2c $USER
    echo "   ⚠️  Please log out and back in for group changes to take effect"
fi

# Test hardware availability
echo "🧪 Testing hardware availability..."
python3 -c "
try:
    from gpiozero import LED
    print('✅ GPIO/gpiozero: Available')
except ImportError as e:
    print(f'❌ GPIO/gpiozero: Not available - {e}')

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    print('✅ PCA9685: Libraries available')
except ImportError as e:
    print(f'❌ PCA9685: Libraries not available - {e}')

try:
    import semantic_kernel
    print('✅ Semantic Kernel: Available')
except ImportError as e:
    print(f'❌ Semantic Kernel: Not available - {e}')
"

echo ""
echo "🎉 AiBot setup complete!"
echo "   Run: cd /home/spark/RR2025/AiBot && python main.py"
echo ""
