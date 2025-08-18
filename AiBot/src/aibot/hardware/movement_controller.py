#!/usr/bin/env python3
"""
Movement Controller Module for AiBot
Handles robot movement using PCA9685 PWM driver for motor control with automatic stop delays
"""

import logging
import time
import asyncio
from typing import Optional
from .pca9685_controller import PCA9685Controller

logger = logging.getLogger(__name__)


class MovementController:
    """Controller for robot movement using PCA9685 motor driver with automatic stop functionality"""
    
    def __init__(self, pca_controller: Optional[PCA9685Controller] = None, motor_config: Optional[dict] = None):
        """
        Initialize movement controller
        
        Args:
            pca_controller: Instance of PCA9685Controller (will create if None)
            motor_config: Motor configuration dictionary
        """
        # Initialize PCA9685 controller if not provided
        if pca_controller is None:
            self.pca = PCA9685Controller()
        else:
            self.pca = pca_controller
        
        # Default motor configuration (4-wheel mecanum setup)
        self.motors = motor_config or {
            "front_right": {"channel": 15, "in1": 14, "in2": 13},
            "front_left": {"channel": 4, "in1": 5, "in2": 6},
            "rear_right": {"channel": 10, "in1": 12, "in2": 11},
            "rear_left": {"channel": 9, "in1": 7, "in2": 8},
        }
        
        # Track current movement task for stopping
        self._current_movement_task = None
        self._is_moving = False
        
        # Initialize all motors to stopped state
        self.stop_all_motors()
        
        logger.info(f"Movement controller initialized with {len(self.motors)} motors")
    
    def set_motor_speed(self, motor_name: str, speed: int, direction: str = "forward") -> bool:
        """
        Set motor speed and direction
        
        Args:
            motor_name: Name of the motor from config
            speed: Speed value (0-100)
            direction: Direction ("forward" or "backward")
            
        Returns:
            bool: Success status
        """
        if motor_name not in self.motors:
            logger.error(f"Motor {motor_name} not found in configuration")
            return False
        
        try:
            motor = self.motors[motor_name]
            
            # Convert speed percentage to PWM duty cycle (0-65535)
            speed = max(0, min(100, speed))  # Clamp between 0-100
            duty_cycle = int((speed / 100) * 65535)
            
            # Set PWM for motor enable/speed
            self.pca.set_pwm(motor["channel"], duty_cycle)
            
            # Set direction pins
            if direction == "forward":
                self.pca.set_pwm(motor["in1"], 65535)  # High
                self.pca.set_pwm(motor["in2"], 0)      # Low
            elif direction == "backward":
                self.pca.set_pwm(motor["in1"], 0)      # Low
                self.pca.set_pwm(motor["in2"], 65535)  # High
            else:
                logger.error(f"Invalid direction: {direction}")
                return False
            
            logger.info(f"Motor {motor_name}: Speed={speed}%, Direction={direction}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set motor speed for {motor_name}: {e}")
            return False
    
    def stop_motor(self, motor_name: str) -> bool:
        """
        Stop a specific motor
        
        Args:
            motor_name: Name of the motor from config
            
        Returns:
            bool: Success status
        """
        if motor_name not in self.motors:
            logger.error(f"Motor {motor_name} not found in configuration")
            return False
        
        try:
            motor = self.motors[motor_name]
            
            # Set all channels to 0
            self.pca.set_pwm(motor["channel"], 0)
            self.pca.set_pwm(motor["in1"], 0)
            self.pca.set_pwm(motor["in2"], 0)
            
            logger.info(f"Motor {motor_name} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop motor {motor_name}: {e}")
            return False
    
    def stop_all_motors(self) -> bool:
        """Stop all motors - does not cancel current movement task if called from within it"""
        try:
            # Only cancel movement task if we're not being called from within the task itself
            # (This prevents self-cancellation when movement completes normally)
            current_task = None
            try:
                current_task = asyncio.current_task()
            except RuntimeError:
                pass  # No event loop running
            
            if (self._current_movement_task and 
                not self._current_movement_task.done() and 
                current_task != self._current_movement_task):
                self._current_movement_task.cancel()
            
            success = True
            for motor_name in self.motors:
                if not self.stop_motor(motor_name):
                    success = False
            
            self._is_moving = False
            logger.info("All motors stopped")
            return success
        except Exception as e:
            logger.error(f"Failed to stop all motors: {e}")
            return False
    
    async def _movement_with_timeout(self, movement_func, speed: int, duration: float = 1.0) -> bool:
        """
        Execute a movement function with automatic timeout
        
        Args:
            movement_func: Function to execute the movement
            speed: Speed value (0-100)
            duration: Duration in seconds before auto-stop
            
        Returns:
            bool: Success status
        """
        try:
            # Execute the movement
            success = movement_func(speed)
            if not success:
                return False
            
            self._is_moving = True
            
            # Wait for the specified duration
            await asyncio.sleep(duration)
            
            # Auto-stop after duration
            self.stop_all_motors()
            
            return True
            
        except asyncio.CancelledError:
            # Movement was cancelled, stop motors
            self.stop_all_motors()
            logger.info("Movement cancelled")
            return False
        except Exception as e:
            logger.error(f"Error in movement with timeout: {e}")
            self.stop_all_motors()
            return False
    
    def _execute_forward(self, speed: int) -> bool:
        """Internal method to execute forward movement"""
        success = True
        for motor_name in self.motors:
            if not self.set_motor_speed(motor_name, speed, "forward"):
                success = False
        logger.info(f"Moving forward at {speed}% speed")
        return success
    
    def _execute_backward(self, speed: int) -> bool:
        """Internal method to execute backward movement"""
        success = True
        for motor_name in self.motors:
            if not self.set_motor_speed(motor_name, speed, "backward"):
                success = False
        logger.info(f"Moving backward at {speed}% speed")
        return success
    
    def _execute_turn_left(self, speed: int) -> bool:
        """Internal method to execute left turn"""
        success = True
        # Right motors forward
        if not self.set_motor_speed("rear_right", speed, "forward"):
            success = False
        if not self.set_motor_speed("front_right", speed, "forward"):
            success = False
        # Left motors backward
        if not self.set_motor_speed("rear_left", speed, "backward"):
            success = False
        if not self.set_motor_speed("front_left", speed, "backward"):
            success = False
        logger.info(f"Turning left at {speed}% speed")
        return success
    
    def _execute_turn_right(self, speed: int) -> bool:
        """Internal method to execute right turn"""
        success = True
        # Left motors forward
        if not self.set_motor_speed("rear_left", speed, "forward"):
            success = False
        if not self.set_motor_speed("front_left", speed, "forward"):
            success = False
        # Right motors backward
        if not self.set_motor_speed("rear_right", speed, "backward"):
            success = False
        if not self.set_motor_speed("front_right", speed, "backward"):
            success = False
        logger.info(f"Turning right at {speed}% speed")
        return success
    
    def _execute_strafe_left(self, speed: int) -> bool:
        """Internal method to execute left strafe"""
        success = True
        # Front left and rear right forward, front right and rear left backward
        if not self.set_motor_speed("front_left", speed, "forward"):
            success = False
        if not self.set_motor_speed("rear_right", speed, "forward"):
            success = False
        if not self.set_motor_speed("front_right", speed, "backward"):
            success = False
        if not self.set_motor_speed("rear_left", speed, "backward"):
            success = False
        logger.info(f"Strafing left at {speed}% speed")
        return success
    
    def _execute_strafe_right(self, speed: int) -> bool:
        """Internal method to execute right strafe"""
        success = True
        # Front right and rear left forward, front left and rear right backward
        if not self.set_motor_speed("front_right", speed, "forward"):
            success = False
        if not self.set_motor_speed("rear_left", speed, "forward"):
            success = False
        if not self.set_motor_speed("front_left", speed, "backward"):
            success = False
        if not self.set_motor_speed("rear_right", speed, "backward"):
            success = False
        logger.info(f"Strafing right at {speed}% speed")
        return success
    
    async def move_forward(self, speed: int = 50, duration: float = 1.0) -> bool:
        """
        Move all motors forward at specified speed with auto-stop
        
        Args:
            speed: Speed value (0-100)
            duration: Duration in seconds (default: 1.0 second)
            
        Returns:
            bool: Success status
        """
        try:
            # Cancel any previous movement only if it's still running
            if self._current_movement_task and not self._current_movement_task.done():
                self._current_movement_task.cancel()
                try:
                    await self._current_movement_task
                except asyncio.CancelledError:
                    pass  # Expected cancellation
                await asyncio.sleep(0.1)  # Brief pause for cleanup
            
            # Start new movement task
            self._current_movement_task = asyncio.create_task(
                self._movement_with_timeout(self._execute_forward, speed, duration)
            )
            
            # Await the result without additional cancellation handling
            result = await self._current_movement_task
            return result
            
        except asyncio.CancelledError:
            logger.info("Forward movement cancelled externally")
            self.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Failed to move forward: {e}")
            self.stop_all_motors()
            return False
    
    async def move_backward(self, speed: int = 50, duration: float = 1.0) -> bool:
        """
        Move all motors backward at specified speed with auto-stop
        
        Args:
            speed: Speed value (0-100)
            duration: Duration in seconds (default: 1.0 second)
            
        Returns:
            bool: Success status
        """
        try:
            # Cancel any previous movement
            if self._current_movement_task and not self._current_movement_task.done():
                self._current_movement_task.cancel()
                try:
                    await self._current_movement_task
                except asyncio.CancelledError:
                    pass  # Expected cancellation
                await asyncio.sleep(0.1)  # Brief pause for cleanup
            
            # Start new movement task
            self._current_movement_task = asyncio.create_task(
                self._movement_with_timeout(self._execute_backward, speed, duration)
            )
            
            result = await self._current_movement_task
            return result
            
        except asyncio.CancelledError:
            logger.info("Movement cancelled")
            self.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Failed to move backward: {e}")
            self.stop_all_motors()
            return False
    
    async def turn_left(self, speed: int = 50, duration: float = 1.0) -> bool:
        """
        Turn left with auto-stop
        
        Args:
            speed: Speed value (0-100)
            duration: Duration in seconds (default: 1.0 second)
            
        Returns:
            bool: Success status
        """
        try:
            # Cancel any previous movement
            if self._current_movement_task and not self._current_movement_task.done():
                self._current_movement_task.cancel()
                try:
                    await self._current_movement_task
                except asyncio.CancelledError:
                    pass  # Expected cancellation
                await asyncio.sleep(0.1)  # Brief pause for cleanup
            
            # Start new movement task
            self._current_movement_task = asyncio.create_task(
                self._movement_with_timeout(self._execute_turn_left, speed, duration)
            )
            
            result = await self._current_movement_task
            return result
            
        except asyncio.CancelledError:
            logger.info("Movement cancelled")
            self.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Failed to turn left: {e}")
            self.stop_all_motors()
            return False
    
    async def turn_right(self, speed: int = 50, duration: float = 1.0) -> bool:
        """
        Turn right with auto-stop
        
        Args:
            speed: Speed value (0-100)
            duration: Duration in seconds (default: 1.0 second)
            
        Returns:
            bool: Success status
        """
        try:
            # Cancel any previous movement
            if self._current_movement_task and not self._current_movement_task.done():
                self._current_movement_task.cancel()
                await asyncio.sleep(0.1)  # Brief pause for cleanup
            
            # Start new movement task
            self._current_movement_task = asyncio.create_task(
                self._movement_with_timeout(self._execute_turn_right, speed, duration)
            )
            
            return await self._current_movement_task
            
        except asyncio.CancelledError:
            logger.info("Movement cancelled")
            self.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Failed to turn right: {e}")
            self.stop_all_motors()
            return False
    
    async def strafe_left(self, speed: int = 50, duration: float = 1.0) -> bool:
        """
        Strafe left using mecanum wheel kinematics with auto-stop
        
        Args:
            speed: Speed value (0-100)
            duration: Duration in seconds (default: 1.0 second)
            
        Returns:
            bool: Success status
        """
        try:
            # Cancel any previous movement
            if self._current_movement_task and not self._current_movement_task.done():
                self._current_movement_task.cancel()
                await asyncio.sleep(0.1)  # Brief pause for cleanup
            
            # Start new movement task
            self._current_movement_task = asyncio.create_task(
                self._movement_with_timeout(self._execute_strafe_left, speed, duration)
            )
            
            return await self._current_movement_task
            
        except asyncio.CancelledError:
            logger.info("Movement cancelled")
            self.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Failed to strafe left: {e}")
            self.stop_all_motors()
            return False
    
    async def strafe_right(self, speed: int = 50, duration: float = 1.0) -> bool:
        """
        Strafe right using mecanum wheel kinematics with auto-stop
        
        Args:
            speed: Speed value (0-100)
            duration: Duration in seconds (default: 1.0 second)
            
        Returns:
            bool: Success status
        """
        try:
            # Cancel any previous movement
            if self._current_movement_task and not self._current_movement_task.done():
                self._current_movement_task.cancel()
                await asyncio.sleep(0.1)  # Brief pause for cleanup
            
            # Start new movement task
            self._current_movement_task = asyncio.create_task(
                self._movement_with_timeout(self._execute_strafe_right, speed, duration)
            )
            
            return await self._current_movement_task
            
        except asyncio.CancelledError:
            logger.info("Movement cancelled")
            self.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Failed to strafe right: {e}")
            self.stop_all_motors()
            return False
    
    def get_movement_status(self) -> str:
        """Get current movement status"""
        try:
            if self._is_moving:
                return "moving"
            else:
                return "stopped"
        except Exception as e:
            logger.error(f"Failed to get movement status: {e}")
            return "unknown"
    
    def cleanup(self):
        """Clean up movement controller resources"""
        try:
            # Cancel any ongoing movement
            if self._current_movement_task and not self._current_movement_task.done():
                self._current_movement_task.cancel()
            
            self.stop_all_motors()
            self.pca.cleanup()
            logger.info("Movement controller resources cleaned up")
        except Exception as e:
            logger.error(f"Error during movement controller cleanup: {e}")
