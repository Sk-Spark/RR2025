"""
Utility functions and helpers for the Orchestrator Agent.
"""

import asyncio
import uuid
from typing import Any, Dict, Optional, Union
from datetime import datetime, timezone


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique identifier with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique identifier string
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format with UTC timezone.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now(timezone.utc).isoformat()


def safe_get_dict_value(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with fallback.
    
    Args:
        data: Dictionary to search
        key: Key to look for
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
    """
    return data.get(key, default)


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> bool:
    """
    Validate that all required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present, False otherwise
    """
    return all(field in data for field in required_fields)


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize a string by limiting length and removing potentially harmful characters.
    
    Args:
        text: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Remove or replace potentially harmful characters
    # This is a basic implementation - extend as needed
    text = text.replace('\x00', '')  # Remove null bytes
    text = text.strip()
    
    return text


async def timeout_wrapper(coro, timeout_seconds: float):
    """
    Wrap a coroutine with a timeout.
    
    Args:
        coro: Coroutine to execute
        timeout_seconds: Timeout in seconds
        
    Returns:
        Result of the coroutine or raises asyncio.TimeoutError
    """
    return await asyncio.wait_for(coro, timeout=timeout_seconds)


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format an error message with context information.
    
    Args:
        error: Exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    if context:
        return f"[{context}] {error_type}: {error_message}"
    else:
        return f"{error_type}: {error_message}"


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


class AsyncContextManager:
    """
    Generic async context manager for resource management.
    """
    
    def __init__(self, setup_func=None, cleanup_func=None):
        """
        Initialize the context manager.
        
        Args:
            setup_func: Optional async function to call on enter
            cleanup_func: Optional async function to call on exit
        """
        self.setup_func = setup_func
        self.cleanup_func = cleanup_func
        self.resource = None
    
    async def __aenter__(self):
        """Enter the async context."""
        if self.setup_func:
            self.resource = await self.setup_func()
        return self.resource
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context."""
        if self.cleanup_func:
            await self.cleanup_func(self.resource)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    await asyncio.sleep(delay)
            
            # If we get here, all retries failed
            raise last_exception
        
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Calculate delay with exponential backoff
                    import time
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    time.sleep(delay)
            
            # If we get here, all retries failed
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
