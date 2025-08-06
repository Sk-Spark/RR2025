"""Test configuration and utilities."""

import pytest
import asyncio
import sys
import os

# Add src to path for tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_hardware():
    """Mock hardware for testing without physical devices."""
    # This can be expanded to mock GPIO, PCA9685, etc.
    return True
