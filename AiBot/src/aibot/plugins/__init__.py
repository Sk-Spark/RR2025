"""Plugins module initialization."""

from .movement_plugin import MovementControlPlugin
from .camera_plugin import CameraControlPlugin

__all__ = ["MovementControlPlugin", "CameraControlPlugin"]
