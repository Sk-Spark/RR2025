#!/usr/bin/env python3
"""
Movement Controller for DummyAiBot - Testing without Hardware
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MovementController:
    """Dummy movement controller for testing without hardware"""
    
    def __init__(self, config=None):
        self.config = config
        self.current_position = {"x": 0, "y": 0, "heading": 0}  # Simulated position
        self.is_moving = False
        
        # Use config values if available, otherwise defaults
        if config:
            self.movement_speed = config.simulation_movement_speed  # meters per second (simulated)
            self.turn_rate = config.simulation_turn_rate           # degrees per second (simulated)
        else:
            self.movement_speed = 1.0  # meters per second (simulated)
            self.turn_rate = 90.0      # degrees per second (simulated)
            
        logger.info("Movement controller initialized (simulation mode)")
    
    async def move_forward(self, duration: float = 1.0) -> bool:
        """Simulate moving forward"""
        try:
            logger.info(f"Simulating forward movement for {duration} seconds")
            self.is_moving = True
            
            # Simulate movement by updating position
            distance = self.movement_speed * duration
            self.current_position["y"] += distance
            
            await asyncio.sleep(duration)  # Simulate movement time
            
            self.is_moving = False
            logger.info(f"Forward movement completed. New position: {self.current_position}")
            return True
            
        except Exception as e:
            logger.error(f"Error in forward movement: {e}")
            self.is_moving = False
            return False
    
    async def move_backward(self, duration: float = 1.0) -> bool:
        """Simulate moving backward"""
        try:
            logger.info(f"Simulating backward movement for {duration} seconds")
            self.is_moving = True
            
            distance = self.movement_speed * duration
            self.current_position["y"] -= distance
            
            await asyncio.sleep(duration)
            
            self.is_moving = False
            logger.info(f"Backward movement completed. New position: {self.current_position}")
            return True
            
        except Exception as e:
            logger.error(f"Error in backward movement: {e}")
            self.is_moving = False
            return False
    
    async def turn_left(self, duration: float = 0.5) -> bool:
        """Simulate turning left"""
        try:
            logger.info(f"Simulating left turn for {duration} seconds")
            self.is_moving = True
            
            # Simulate rotation using configurable turn rate
            rotation = self.turn_rate * duration
            self.current_position["heading"] = (self.current_position["heading"] - rotation) % 360
            
            await asyncio.sleep(duration)
            
            self.is_moving = False
            logger.info(f"Left turn completed. New heading: {self.current_position['heading']}°")
            return True
            
        except Exception as e:
            logger.error(f"Error in left turn: {e}")
            self.is_moving = False
            return False
    
    async def turn_right(self, duration: float = 0.5) -> bool:
        """Simulate turning right"""
        try:
            logger.info(f"Simulating right turn for {duration} seconds")
            self.is_moving = True
            
            rotation = self.turn_rate * duration
            self.current_position["heading"] = (self.current_position["heading"] + rotation) % 360
            
            await asyncio.sleep(duration)
            
            self.is_moving = False
            logger.info(f"Right turn completed. New heading: {self.current_position['heading']}°")
            return True
            
        except Exception as e:
            logger.error(f"Error in right turn: {e}")
            self.is_moving = False
            return False
    
    async def stop(self) -> bool:
        """Stop all movement"""
        try:
            logger.info("Stopping all movement")
            self.is_moving = False
            return True
            
        except Exception as e:
            logger.error(f"Error stopping movement: {e}")
            return False
    
    def get_position(self) -> dict:
        """Get current position and status"""
        return {
            "position": self.current_position.copy(),
            "is_moving": self.is_moving,
            "movement_speed": self.movement_speed
        }
    
    def get_status(self) -> dict:
        """Get movement controller status"""
        return {
            "controller_type": "pure_simulation",
            "is_moving": self.is_moving,
            "current_position": self.current_position.copy(),
            "movement_speed": self.movement_speed,
            "turn_rate": self.turn_rate,
            "available_commands": ["forward", "backward", "left", "right", "stop"],
            "status": "ready" if not self.is_moving else "moving",
            "note": "Simulation only - no hardware"
        }
    
    def cleanup(self):
        """Cleanup movement controller"""
        logger.info("Movement controller cleaned up")
