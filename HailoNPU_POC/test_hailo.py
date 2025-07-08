#!/usr/bin/env python3
"""
Simple test script to verify Hailo NPU functionality
"""

import os
import sys
import numpy as np
from picamera2.devices import Hailo
import config

def test_hailo():
    """Test Hailo NPU initialization and basic functionality"""
    print("Testing Hailo NPU...")
    
    # Get model path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, config.MODEL_PATH)
    
    print(f"Model path: {model_path}")
    print(f"Model exists: {os.path.exists(model_path)}")
    
    if not os.path.exists(model_path):
        print("ERROR: Model file not found!")
        return False
    
    try:
        # Initialize Hailo
        print("Initializing Hailo...")
        hailo = Hailo(model_path)
        
        # Get input shape
        h, w, c = hailo.get_input_shape()
        print(f"Model input shape: {w}x{h}x{c}")
        
        # Create dummy input
        dummy_input = np.random.randint(0, 255, (h, w, c), dtype=np.uint8)
        print(f"Created dummy input: {dummy_input.shape}")
        
        # Run inference
        print("Running inference...")
        results = hailo.run(dummy_input)
        print(f"Inference successful! Results type: {type(results)}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_hailo()
    print(f"Test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
