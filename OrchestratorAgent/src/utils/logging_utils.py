"""
Logging utilities for the Orchestrator Agent.
Provides centralized logging configuration and utilities.
"""

import logging
import logging.handlers
import os
from typing import Optional
from datetime import datetime


class LoggerManager:
    """
    Manages logging configuration for the orchestrator and its components.
    Provides file and console logging with proper formatting.
    """
    
    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        """
        Initialize the logger manager.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory to store log files
        """
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = log_dir
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure root logger
        self._configure_root_logger()
    
    def _configure_root_logger(self) -> None:
        """Configure the root logger with file and console handlers."""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = os.path.join(self.log_dir, 'orchestrator.log')
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Error log file
        error_log_file = os.path.join(self.log_dir, 'orchestrator_errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.
        
        Args:
            name: Logger name (usually __name__ of the module)
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)
    
    def log_agent_activity(self, agent_id: str, activity: str, level: str = "INFO") -> None:
        """
        Log agent-specific activity with structured format.
        
        Args:
            agent_id: ID of the agent
            activity: Description of the activity
            level: Log level
        """
        logger = self.get_logger(f"agent.{agent_id}")
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, f"[{agent_id}] {activity}")
    
    def log_task_execution(self, task_id: str, agent_id: str, status: str, details: str = "") -> None:
        """
        Log task execution events with structured format.
        
        Args:
            task_id: ID of the task
            agent_id: ID of the agent executing the task
            status: Task status (STARTED, COMPLETED, FAILED, etc.)
            details: Additional details about the task execution
        """
        logger = self.get_logger("task_execution")
        message = f"[TASK:{task_id}] [AGENT:{agent_id}] [STATUS:{status}]"
        if details:
            message += f" - {details}"
        logger.info(message)
    
    def log_websocket_event(self, event_type: str, client_id: Optional[str] = None, details: str = "") -> None:
        """
        Log WebSocket events with structured format.
        
        Args:
            event_type: Type of WebSocket event (CONNECT, DISCONNECT, MESSAGE, ERROR)
            client_id: ID of the WebSocket client
            details: Additional details about the event
        """
        logger = self.get_logger("websocket")
        message = f"[{event_type}]"
        if client_id:
            message += f" [CLIENT:{client_id}]"
        if details:
            message += f" - {details}"
        logger.info(message)
    
    def log_semantic_kernel_event(self, event_type: str, details: str = "") -> None:
        """
        Log Semantic Kernel events with structured format.
        
        Args:
            event_type: Type of SK event (PLAN_CREATED, FUNCTION_CALLED, etc.)
            details: Additional details about the event
        """
        logger = self.get_logger("semantic_kernel")
        message = f"[SK:{event_type}]"
        if details:
            message += f" - {details}"
        logger.info(message)


# Global logger manager instance
_logger_manager: Optional[LoggerManager] = None


def initialize_logging(log_level: str = "INFO", log_dir: str = "logs") -> LoggerManager:
    """
    Initialize the global logger manager.
    
    Args:
        log_level: Logging level
        log_dir: Directory to store log files
        
    Returns:
        Configured LoggerManager instance
    """
    global _logger_manager
    _logger_manager = LoggerManager(log_level, log_dir)
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance. Initializes logging if not already done.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager.get_logger(name)


def log_agent_activity(agent_id: str, activity: str, level: str = "INFO") -> None:
    """Convenience function for logging agent activity."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    _logger_manager.log_agent_activity(agent_id, activity, level)


def log_task_execution(task_id: str, agent_id: str, status: str, details: str = "") -> None:
    """Convenience function for logging task execution."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    _logger_manager.log_task_execution(task_id, agent_id, status, details)


def log_websocket_event(event_type: str, client_id: Optional[str] = None, details: str = "") -> None:
    """Convenience function for logging WebSocket events."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    _logger_manager.log_websocket_event(event_type, client_id, details)


def log_semantic_kernel_event(event_type: str, details: str = "") -> None:
    """Convenience function for logging Semantic Kernel events."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    _logger_manager.log_semantic_kernel_event(event_type, details)
