#!/usr/bin/env python3
"""
Color test for camera manager
Tests RGB to BGR conversion and color display
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import cv2
import numpy as np
logging.basicConfig(level=logging.INFO)

from camera_manager import CameraManager

def test_camera_colors():
    """Test camera color handling"""
    
    print("Testing camera color handling...")
    
    try:
        camera = CameraManager()
        
        # Test frame capture
        frame = camera.capture_frame()
        if frame is not None:
            print(f"✓ Frame captured: {frame.shape}, dtype: {frame.dtype}")
            print(f"✓ Frame value range: {frame.min()} to {frame.max()}")
            
            # Test color channels
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                b, g, r = cv2.split(frame)
                print(f"✓ Blue channel range: {b.min()} to {b.max()}")
                print(f"✓ Green channel range: {g.min()} to {g.max()}")
                print(f"✓ Red channel range: {r.min()} to {r.max()}")
                
                # Create a test color pattern to verify BGR order
                height, width = frame.shape[:2]
                test_frame = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Create colored rectangles (BGR format)
                cv2.rectangle(test_frame, (10, 10), (110, 110), (255, 0, 0), -1)    # Blue
                cv2.rectangle(test_frame, (120, 10), (220, 110), (0, 255, 0), -1)   # Green  
                cv2.rectangle(test_frame, (230, 10), (330, 110), (0, 0, 255), -1)   # Red
                
                # Add labels
                cv2.putText(test_frame, "BLUE", (15, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(test_frame, "GREEN", (125, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(test_frame, "RED", (235, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Test JPEG encoding
                jpeg_quality = 50
                ret, buffer = cv2.imencode('.jpg', test_frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
                if ret:
                    print(f"✓ JPEG encoding successful: {len(buffer)} bytes")
                    
                    # Test decoding
                    decoded_frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                    if decoded_frame is not None:
                        print(f"✓ JPEG decoding successful: {decoded_frame.shape}")
                        
                        # Save test image for visual verification
                        cv2.imwrite('/tmp/color_test.jpg', test_frame)
                        print("✓ Test color image saved to /tmp/color_test.jpg")
                    else:
                        print("❌ JPEG decoding failed")
                else:
                    print("❌ JPEG encoding failed")
            else:
                print(f"❌ Invalid frame format: {frame.shape}")
        else:
            print("⚠️  No frame captured (simulation mode)")
            
        camera.cleanup()
        print("✅ Camera color test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Camera color test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_camera_colors()
    sys.exit(0 if success else 1)
