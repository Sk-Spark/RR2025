#!/usr/bin/env python3
"""
Configuration settings for DummyAiBot - Pure Simulation/Testing
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class BotConfig:
    """Configuration class for the Dummy AI Bot Agent - Simulation Only."""
    
    # Agent identification
    agent_id: str = "dummy_ai_bot_001"
    agent_name: str = "DummyAiBot"
    agent_description: str = "Dummy AI bot for testing - simulation only, no hardware"
    
    # Operation mode
    terminal_mode: bool = False  # If True, takes commands from terminal instead of orchestrator
    
    # Orchestrator connection
    orchestrator_url: str = "ws://localhost:8765"
    max_reconnect_attempts: int = -1  # -1 for infinite attempts
    reconnect_delay: int = 5
    
    # Ollama/LLM configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    # Bot capabilities (simulation only)
    capabilities: List[str] = None
    
    # Simulation parameters
    simulation_movement_speed: float = 1.0  # meters per second (simulated)
    simulation_turn_rate: float = 90.0     # degrees per second (simulated)
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
    
    def __post_init__(self):
        """Initialize default capabilities for dummy bot."""
        if self.capabilities is None:
            self.capabilities = [
                "movement_simulation",
                "camera_simulation", 
                "task_execution",
                "llm_reasoning",
                "status_reporting"
            ]
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Create configuration from environment variables."""
        return cls(
            agent_id=os.getenv('BOT_AGENT_ID', 'dummy_ai_bot_001'),
            orchestrator_url=os.getenv('ORCHESTRATOR_URL', 'ws://localhost:8765'),
            ollama_base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            ollama_model=os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_description': self.agent_description,
            'orchestrator_url': self.orchestrator_url,
            'ollama_base_url': self.ollama_base_url,
            'ollama_model': self.ollama_model,
            'capabilities': self.capabilities,
            'simulation_movement_speed': self.simulation_movement_speed,
            'simulation_turn_rate': self.simulation_turn_rate,
        }
