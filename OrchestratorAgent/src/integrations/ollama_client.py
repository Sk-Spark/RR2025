"""
Ollama integration for local LLaMA model access.
Provides interface to communicate with locally running Ollama service.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, AsyncGenerator
import json

from ..utils import get_logger, retry_with_backoff, format_error_message


class OllamaClient:
    """
    Client for interacting with Ollama API to access local LLaMA models.
    Provides both streaming and non-streaming text generation capabilities.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: Base URL of the Ollama service
            model: Model name to use for generation
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.logger = get_logger(__name__)
        
        # Session for HTTP requests
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Model state
        self._model_loaded = False
        self._available_models: List[str] = []
        
        self.logger.info(f"OllamaClient initialized with model {model} at {base_url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self) -> None:
        """Start the Ollama client and initialize session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300, connect=10)
            )
        
        # Check if service is available
        if await self.check_health():
            await self.load_model()
            await self.update_available_models()
        else:
            self.logger.warning("Ollama service is not available")
    
    async def stop(self) -> None:
        """Stop the client and cleanup resources."""
        if self._session:
            await self._session.close()
            self._session = None
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def check_health(self) -> bool:
        """
        Check if Ollama service is healthy and reachable.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            if not self._session:
                return False
            
            async with self._session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    self.logger.debug("Ollama service is healthy")
                    return True
                else:
                    self.logger.warning(f"Ollama service returned status {response.status}")
                    return False
        
        except Exception as e:
            self.logger.error(f"Health check failed: {format_error_message(e)}")
            return False
    
    async def load_model(self) -> bool:
        """
        Load the specified model.
        
        Returns:
            True if model was loaded successfully, False otherwise
        """
        try:
            if not self._session:
                return False
            
            payload = {
                "name": self.model
            }
            
            async with self._session.post(
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                if response.status == 200:
                    self._model_loaded = True
                    self.logger.info(f"Model {self.model} loaded successfully")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(f"Failed to load model {self.model}: {error_text}")
                    return False
        
        except Exception as e:
            self.logger.error(f"Error loading model: {format_error_message(e)}")
            return False
    
    async def update_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of available model names
        """
        try:
            if not self._session:
                return []
            
            async with self._session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model.get('name', '') for model in data.get('models', [])]
                    self._available_models = models
                    self.logger.debug(f"Available models: {models}")
                    return models
                else:
                    self.logger.error(f"Failed to get models list: {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error getting available models: {format_error_message(e)}")
            return []
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Optional[str]:
        """
        Generate text using the loaded model.
        
        Args:
            prompt: Input prompt for generation
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            stream: Whether to use streaming response
            
        Returns:
            Generated text or None if generation failed
        """
        try:
            if not self._session:
                self.logger.error("Client session not initialized")
                return None
            
            if not await self.check_health():
                self.logger.error("Ollama service is not available")
                return None
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            if stream:
                return await self._generate_streaming(payload)
            else:
                return await self._generate_non_streaming(payload)
        
        except Exception as e:
            self.logger.error(f"Error generating text: {format_error_message(e)}")
            return None
    
    async def _generate_non_streaming(self, payload: Dict[str, Any]) -> Optional[str]:
        """Generate text without streaming."""
        try:
            async with self._session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    generated_text = data.get('response', '')
                    self.logger.debug(f"Generated {len(generated_text)} characters")
                    return generated_text
                else:
                    error_text = await response.text()
                    self.logger.error(f"Generation failed: {error_text}")
                    return None
        
        except Exception as e:
            self.logger.error(f"Error in non-streaming generation: {format_error_message(e)}")
            return None
    
    async def _generate_streaming(self, payload: Dict[str, Any]) -> Optional[str]:
        """Generate text with streaming."""
        try:
            async with self._session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    generated_text = ""
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line:
                            try:
                                chunk = json.loads(line)
                                if 'response' in chunk:
                                    generated_text += chunk['response']
                                if chunk.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    self.logger.debug(f"Generated {len(generated_text)} characters (streaming)")
                    return generated_text
                else:
                    error_text = await response.text()
                    self.logger.error(f"Streaming generation failed: {error_text}")
                    return None
        
        except Exception as e:
            self.logger.error(f"Error in streaming generation: {format_error_message(e)}")
            return None
    
    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Generate text with streaming chunks.
        
        Args:
            prompt: Input prompt for generation
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            
        Yields:
            Text chunks as they are generated
        """
        try:
            if not self._session:
                self.logger.error("Client session not initialized")
                return
            
            if not await self.check_health():
                self.logger.error("Ollama service is not available")
                return
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            async with self._session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line:
                            try:
                                chunk = json.loads(line)
                                if 'response' in chunk:
                                    yield chunk['response']
                                if chunk.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    error_text = await response.text()
                    self.logger.error(f"Streaming generation failed: {error_text}")
        
        except Exception as e:
            self.logger.error(f"Error in streaming generation: {format_error_message(e)}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Perform chat completion with conversation context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response or None if failed
        """
        try:
            if not self._session:
                self.logger.error("Client session not initialized")
                return None
            
            # Convert messages to Ollama format
            prompt = self._format_chat_messages(messages)
            
            return await self.generate_text(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        except Exception as e:
            self.logger.error(f"Error in chat completion: {format_error_message(e)}")
            return None
    
    def _format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format chat messages into a single prompt.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted prompt string
        """
        formatted_prompt = ""
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                formatted_prompt += f"System: {content}\n\n"
            elif role == 'user':
                formatted_prompt += f"Human: {content}\n\n"
            elif role == 'assistant':
                formatted_prompt += f"Assistant: {content}\n\n"
        
        # Add prompt for assistant response
        formatted_prompt += "Assistant: "
        
        return formatted_prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model,
            'base_url': self.base_url,
            'model_loaded': self._model_loaded,
            'available_models': self._available_models
        }
    
    def is_available(self) -> bool:
        """Check if the Ollama service is available."""
        return self._model_loaded
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return self._available_models.copy()
