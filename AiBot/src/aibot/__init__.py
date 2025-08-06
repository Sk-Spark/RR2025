"""
AiBot - Intelligent Robot Control System
========================================

A modular AI-powered robot control system using Semantic Kernel and Ollama LLM
for natural language command processing with LED and movement control capabilities.

Features:
- Natural language command processing
- LED control with GPIO integration
- Motor control with PCA9685 PWM driver
- 1-second auto-stop safety for all movements
- Mecanum wheel movement patterns
- WebSocket communication support
- Modular plugin architecture

Version: 1.0.0
Author: Spark
"""

__version__ = "1.0.0"
__author__ = "Spark"

from .core.app import LEDControlApp
from .core.config import ConfigManager as Config

__all__ = ["LEDControlApp", "Config"]
