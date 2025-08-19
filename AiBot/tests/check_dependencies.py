#!/usr/bin/env python3
"""
Dependency Check Script for AiBot
Verifies all required libraries are properly installed and working
"""

import sys
import importlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_import(module_name, friendly_name=None):
    """Check if a module can be imported"""
    if friendly_name is None:
        friendly_name = module_name
    
    try:
        importlib.import_module(module_name)
        logger.info(f"✅ {friendly_name} - OK")
        return True
    except ImportError as e:
        logger.error(f"❌ {friendly_name} - FAILED: {e}")
        return False

def main():
    """Main dependency check function"""
    print("🔍 AiBot Dependency Check")
    print("=" * 40)
    
    all_good = True
    
    # Core Python libraries
    logger.info("Checking core libraries...")
    core_modules = [
        ("asyncio", "AsyncIO"),
        ("logging", "Logging"),
        ("time", "Time utilities"),
        ("typing", "Type hints"),
    ]
    
    for module, name in core_modules:
        if not check_import(module, name):
            all_good = False
    
    # AI and NLP libraries
    logger.info("\nChecking AI/NLP libraries...")
    ai_modules = [
        ("semantic_kernel", "Semantic Kernel"),
        ("ollama", "Ollama client"),
    ]
    
    for module, name in ai_modules:
        if not check_import(module, name):
            all_good = False
    
    # Web/Communication libraries
    logger.info("\nChecking communication libraries...")
    comm_modules = [
        ("aiohttp", "AsyncIO HTTP"),
        ("websockets", "WebSockets"),
    ]
    
    for module, name in comm_modules:
        if not check_import(module, name):
            all_good = False
    
    # Hardware libraries
    logger.info("\nChecking hardware libraries...")
    hardware_modules = [
        ("gpiozero", "GPIO Zero"),
        ("lgpio", "Linux GPIO (RPi 5 support)"),
        ("board", "CircuitPython Board"),
        ("busio", "CircuitPython Bus IO"),
        ("adafruit_pca9685", "Adafruit PCA9685"),
        ("adafruit_blinka", "Adafruit Blinka"),
    ]
    
    for module, name in hardware_modules:
        if not check_import(module, name):
            all_good = False
    
    # Testing libraries (optional)
    logger.info("\nChecking testing libraries...")
    test_modules = [
        ("pytest", "PyTest"),
        ("pytest_asyncio", "PyTest AsyncIO"),
    ]
    
    for module, name in test_modules:
        check_import(module, name)  # Don't fail on these
    
    print("\n" + "=" * 40)
    if all_good:
        logger.info("🎉 All required dependencies are working!")
        print("\n✅ Hardware compatibility test...")
        try:
            # Test hardware initialization
            import board
            import busio
            from adafruit_pca9685 import PCA9685
            
            logger.info("  - Board module: OK")
            logger.info("  - Bus IO: OK") 
            logger.info("  - PCA9685 driver: OK")
            
            # Try actual hardware detection
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                pca = PCA9685(i2c, address=0x40)
                logger.info("  - PCA9685 hardware detected: OK")
            except Exception as e:
                logger.warning(f"  - PCA9685 hardware detection: {e}")
                logger.info("  - (This is normal if hardware is not connected)")
                
        except Exception as e:
            logger.error(f"❌ Hardware test failed: {e}")
            all_good = False
    else:
        logger.error("❌ Some dependencies are missing or failed to load")
        logger.error("Run: pip install -r requirements.txt")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
