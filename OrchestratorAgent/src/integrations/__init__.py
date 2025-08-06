"""
Integrations package for the Orchestrator Agent.
Contains integrations with external services like Ollama.
"""

from .ollama_integration import OllamaClient, OllamaIntegration, OllamaModelInfo

__all__ = [
    'OllamaClient',
    'OllamaIntegration', 
    'OllamaModelInfo'
]
