"""
Configuration management for the Orchestrator Agent.
Contains all configuration values directly in the file.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class WebSocketConfig:
    """WebSocket server configuration."""
    host: str
    port: int
    max_connections: int


@dataclass
class OllamaConfig:
    """Ollama API configuration."""
    host: str
    port: int
    model: str
    base_url: str


@dataclass
class SemanticKernelConfig:
    """Semantic Kernel configuration."""
    service_id: str
    model_deployment_name: str


@dataclass
class OrchestratorConfig:
    """Main orchestrator configuration."""
    debug: bool
    log_level: str
    websocket: WebSocketConfig
    ollama: OllamaConfig
    semantic_kernel: SemanticKernelConfig
    agent_registration_timeout: int
    agent_heartbeat_interval: int
    task_execution_timeout: int


class ConfigManager:
    """
    Manages application configuration with hardcoded values.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._config = self._load_config()
    
    def _load_config(self) -> OrchestratorConfig:
        """Load hardcoded configuration values."""
        # WebSocket configuration
        websocket_config = WebSocketConfig(
            host='0.0.0.0',
            port=8080,
            max_connections=10
        )
        
        # Ollama configuration
        ollama_host = 'localhost'
        ollama_port = 11434
        ollama_config = OllamaConfig(
            host=ollama_host,
            port=ollama_port,
            model='llama3.2:1b',
            base_url=f"http://{ollama_host}:{ollama_port}"
        )
        
        # Semantic Kernel configuration
        sk_config = SemanticKernelConfig(
            service_id='orchestrator_sk',
            model_deployment_name='gpt-3.5-turbo'
        )
        
        return OrchestratorConfig(
            debug=True,
            log_level='INFO',
            websocket=websocket_config,
            ollama=ollama_config,
            semantic_kernel=sk_config,
            agent_registration_timeout=30,
            agent_heartbeat_interval=10,
            task_execution_timeout=60
        )
    
    @property
    def config(self) -> OrchestratorConfig:
        """Get the current configuration."""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration values at runtime.
        
        Args:
            **kwargs: Configuration values to update
        """
        # This is a simplified version - in production, you might want
        # more sophisticated config updating logic
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
