#!/usr/bin/env python3
"""
Configuration Module
Contains configuration settings for the LED control application.
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # GPIO Configuration
    led_pin: int = 18
    
    # Movement Configuration
    pca9685_address: int = 0x40
    pca9685_frequency: int = 50
    motor_config: dict = None  # Will be set in __post_init__
    
    # Ollama Configuration
    model_name: str = "llama3.2:1b"
    base_url: str = "http://localhost:11434"
    
    # Orchestrator Configuration
    orchestrator_url: Optional[str] = None  # Set in config or by command-line mode
    agent_id: Optional[str] = "rpi5_agent"
    heartbeat_interval: int = 30
    max_reconnect_attempts: int = -1  # -1 for unlimited
    reconnect_delay: int = 5
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Application Settings
    max_retries: int = 3
    timeout_seconds: int = 30
    
    def __post_init__(self):
        """Set default motor configuration if not provided"""
        if self.motor_config is None:
            self.motor_config = {
                "front_right": {"channel": 15, "in1": 14, "in2": 13},
                "front_left": {"channel": 4, "in1": 5, "in2": 6},
                "rear_right": {"channel": 10, "in1": 12, "in2": 11},
                "rear_left": {"channel": 9, "in1": 7, "in2": 8},
            }
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables and config file."""
        
        # Try to load from config file first
        config_values = cls._load_config_file()
        
        return cls(
            led_pin=int(os.getenv("LED_PIN", config_values.get("LED_PIN", "18"))),
            pca9685_address=int(os.getenv("PCA9685_ADDRESS", "0x40"), 0),
            pca9685_frequency=int(os.getenv("PCA9685_FREQUENCY", "50")),
            model_name=os.getenv("OLLAMA_MODEL", config_values.get("OLLAMA_MODEL", "llama3.2:1b")),
            base_url=os.getenv("OLLAMA_BASE_URL", config_values.get("OLLAMA_BASE_URL", "http://localhost:11434")),
            orchestrator_url=os.getenv("ORCHESTRATOR_URL", config_values.get("ORCHESTRATOR_URL")),
            agent_id=os.getenv("AGENT_ID", config_values.get("AGENT_ID", "rpi5_agent")),
            heartbeat_interval=int(os.getenv("HEARTBEAT_INTERVAL", "30")),
            max_reconnect_attempts=int(os.getenv("MAX_RECONNECT_ATTEMPTS", "-1")),
            reconnect_delay=int(os.getenv("RECONNECT_DELAY", "5")),
            log_level=os.getenv("LOG_LEVEL", config_values.get("LOG_LEVEL", "INFO")),
        )
    
    @staticmethod
    def _load_config_file() -> dict:
        """Load configuration from config file."""
        config_values = {}
        
        # Try to find config file
        config_paths = [
            "config/aibot_config.py",
            "../config/aibot_config.py", 
            "../../config/aibot_config.py"
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    # Add config directory to path
                    config_dir = os.path.dirname(os.path.abspath(config_path))
                    if config_dir not in sys.path:
                        sys.path.insert(0, config_dir)
                    
                    # Import config module
                    import aibot_config
                    
                    # Extract configuration values
                    for attr in dir(aibot_config):
                        if not attr.startswith('_'):
                            config_values[attr] = getattr(aibot_config, attr)
                    
                    break
                except Exception:
                    continue
        
        return config_values


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize configuration manager."""
        self.config = config or AppConfig.from_env()
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")
    
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        try:
            # Validate GPIO pin
            if not (1 <= self.config.led_pin <= 40):
                raise ValueError(f"Invalid GPIO pin: {self.config.led_pin}")
            
            # Validate timeout
            if self.config.timeout_seconds <= 0:
                raise ValueError(f"Invalid timeout: {self.config.timeout_seconds}")
            
            # Validate retries
            if self.config.max_retries < 0:
                raise ValueError(f"Invalid max retries: {self.config.max_retries}")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
