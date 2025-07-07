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
    
    # Ollama Configuration
    model_name: str = "llama3.2:1b"
    base_url: str = "http://localhost:11434"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Application Settings
    max_retries: int = 3
    timeout_seconds: int = 30
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            led_pin=int(os.getenv("LED_PIN", "18")),
            model_name=os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "30"))
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
