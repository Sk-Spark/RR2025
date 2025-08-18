#!/usr/bin/env python3
"""
AiBot Configuration File
Edit this file to customize your AiBot settings.
"""

# Orchestrator Configuration
# Set to None for interactive mode only, or provide WebSocket URL for orchestrator mode
ORCHESTRATOR_URL = "ws://localhost:8080"  # Change this to your orchestrator URL
AGENT_ID = "rpi5_agent"                    # Change this to your desired agent ID

# Hardware Configuration  
LED_PIN = 18                               # GPIO pin for LED control

# AI Configuration
OLLAMA_MODEL = "llama3.2:3b"               # Ollama model to use
OLLAMA_BASE_URL = "http://192.168.137.1:11434" # Ollama server URL

# Logging
LOG_LEVEL = "INFO"                         # DEBUG, INFO, WARNING, ERROR
