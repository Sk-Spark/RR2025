"""
Hailo NPU Object Detector
Based on implementation from HailoNPU_POC with adaptations for ball tracking
"""

import os
import sys
import numpy as np
import logging
import config

logger = logging.getLogger(__name__)

try:
    from picamera2.devices import Hailo
    HAILO_AVAILABLE = True
    logger.info("Hailo NPU available through picamera2")
except ImportError as e:
    logger.warning(f"Hailo NPU not available: {e}")
    HAILO_AVAILABLE = False


def extract_detections(hailo_output, w, h, class_names, threshold=0.5):
    """Extract detections from the HailoRT-postprocess output."""
    results = []
    for class_id, detections in enumerate(hailo_output):
        for detection in detections:
            score = detection[4]
            if score >= threshold:
                y0, x0, y1, x1 = detection[:4]
                bbox = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
                results.append({
                    'class_name': class_names[class_id] if class_id < len(class_names) else 'unknown',
                    'bbox': bbox,
                    'confidence': float(score),
                    'class_id': class_id
                })
    return results


class HailoObjectDetector:
    """Hailo-based object detector using picamera2"""
    
    def __init__(self, model_path=None, confidence_threshold=None):
        # Set default values from config
        self.model_path = model_path or self._get_default_model_path()
        self.confidence_threshold = confidence_threshold or config.CONFIDENCE_THRESHOLD
        self.class_names = self._load_class_names()
        self.hailo = None
        self.model_w = None
        self.model_h = None
        
        # Initialize colors for drawing
        self.colors = self._generate_colors()
        
        logger.info(f"Initializing Hailo detector with model: {self.model_path}")
        
    def _get_default_model_path(self):
        """Get the default model path"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try config first
        if hasattr(config, 'MODEL_PATH') and config.MODEL_PATH:
            model_path = os.path.join(script_dir, config.MODEL_PATH)
            if os.path.exists(model_path):
                return model_path
        
        # Try local resources directory first (priority order)
        models_dir = os.path.join(script_dir, "resources", "models", "hailo8")
        preferred_models = [
            "yolov8m.hef",      # YOLOv8 medium - good balance of speed/accuracy
            "yolov6n.hef",      # YOLOv6 nano - fastest
            "yolov5m_seg.hef",  # YOLOv5 medium with segmentation
        ]
        
        for model_name in preferred_models:
            model_path = os.path.join(models_dir, model_name)
            if os.path.exists(model_path):
                logger.info(f"Using Hailo model: {model_name}")
                return model_path
        
        # Try any .hef file in the models directory
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith('.hef'):
                    model_path = os.path.join(models_dir, file)
                    logger.info(f"Using available Hailo model: {file}")
                    return model_path
        
        logger.error("No Hailo model found!")
        raise FileNotFoundError("Hailo model file not found")
        
    def _load_class_names(self):
        """Load class names from labels file or use COCO classes"""
        # Try to load from coco.txt file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        labels_path = os.path.join(script_dir, "coco.txt")
        
        if os.path.exists(labels_path):
            try:
                with open(labels_path, 'r', encoding="utf-8") as f:
                    return f.read().splitlines()
            except Exception as e:
                logger.warning(f"Could not load labels from {labels_path}: {e}")
        
        # Fallback to hardcoded COCO classes
        return [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
    
    def _generate_colors(self):
        """Generate colors for different classes"""
        if hasattr(config, 'DETECTION_COLORS') and config.DETECTION_COLORS:
            return config.DETECTION_COLORS
        else:
            # Generate random colors for each class
            np.random.seed(42)  # For consistent colors
            return np.random.randint(0, 255, size=(len(self.class_names), 3)).tolist()
    
    def initialize(self):
        """Initialize the Hailo model"""
        if not HAILO_AVAILABLE:
            logger.error("Hailo NPU not available")
            return False
            
        try:
            self.hailo = Hailo(self.model_path)
            self.model_h, self.model_w, _ = self.hailo.get_input_shape()
            logger.info(f"Hailo model initialized. Input shape: {self.model_w}x{self.model_h}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Hailo model: {e}")
            return False
    
    def detect(self, frame):
        """Run inference on a frame"""
        if self.hailo is None:
            logger.error("Hailo model not initialized")
            return []
            
        try:
            # Run inference
            results = self.hailo.run(frame)
            
            # Extract detections - we need to get the original frame dimensions
            # for proper scaling
            h, w = frame.shape[:2] if len(frame.shape) > 2 else frame.shape
            
            detections = extract_detections(
                results, w, h, self.class_names, self.confidence_threshold
            )
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources"""
        if self.hailo:
            # Hailo context manager should handle cleanup
            pass
