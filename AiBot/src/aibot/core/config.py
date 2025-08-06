#!/usr/bin/env python3
"""
Configuration Module
Contains configuration settings for the LED control application.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # GPIO Configuration
    led_pin: int = 18
    
    # Movement Configuration
    enable_movement: bool = True
    pca9685_address: int = 0x40
    pca9685_frequency: int = 50
    motor_config: dict = None  # Will be set in __post_init__
    
    # Ollama Configuration
    model_name: str = "llama3.2:1b"
    base_url: str = "http://localhost:11434"
    
    # Orchestrator Configuration
    orchestrator_url: Optional[str] = None  # Set to None by default for interactive mode
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
        """Create configuration from environment variables."""
        
        return cls(
            led_pin=cls.led_pin if cls.led_pin is not None else int(os.getenv("LED_PIN", "18")),
            enable_movement=cls.enable_movement if cls.enable_movement is not None else os.getenv("ENABLE_MOVEMENT", "true").lower() == "true",
            pca9685_address=cls.pca9685_address if cls.pca9685_address is not None else int(os.getenv("PCA9685_ADDRESS", "0x40"), 0),
            pca9685_frequency=cls.pca9685_frequency if cls.pca9685_frequency is not None else int(os.getenv("PCA9685_FREQUENCY", "50")),
            model_name=cls.model_name if cls.model_name is not None else os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
            base_url=cls.base_url if cls.base_url is not None else os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            orchestrator_url=cls.orchestrator_url if cls.orchestrator_url is not None else os.getenv("ORCHESTRATOR_URL"),
            agent_id=cls.agent_id if cls.agent_id is not None else os.getenv("AGENT_ID"),
            heartbeat_interval=cls.heartbeat_interval if cls.heartbeat_interval is not None else int(os.getenv("HEARTBEAT_INTERVAL", "30")),
            max_reconnect_attempts=cls.max_reconnect_attempts if cls.max_reconnect_attempts is not None else int(os.getenv("MAX_RECONNECT_ATTEMPTS", "-1")),
            reconnect_delay=cls.reconnect_delay if cls.reconnect_delay is not None else int(os.getenv("RECONNECT_DELAY", "5")),
            log_level=cls.log_level if cls.log_level is not None else os.getenv("LOG_LEVEL", "INFO"),
            log_format=cls.log_format if cls.log_format is not None else os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            max_retries=cls.max_retries if cls.max_retries is not None else int(os.getenv("MAX_RETRIES", "3")),
            timeout_seconds=cls.timeout_seconds if cls.timeout_seconds is not None else int(os.getenv("TIMEOUT_SECONDS", "30")),
        )


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
