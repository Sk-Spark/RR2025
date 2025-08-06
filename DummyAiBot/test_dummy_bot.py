#!/usr/bin/env python3
"""
Test script for DummyAiBot - Basic functionality testing
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from config.settings import BotConfig
from agents.dummy_bot import DummyAiBot
from controllers.movement_controller import MovementController
from controllers.camera_controller import CameraController
from agents.llm_service import LLMService


async def test_movement_controller():
    """Test movement controller"""
    print("\n=== Testing Movement Controller ===")
    controller = MovementController()
    
    print("Testing forward movement...")
    await controller.move_forward(0.5)
    
    print("Testing backward movement...")
    await controller.move_backward(0.5)
    
    print("Testing left turn...")
    await controller.turn_left(0.25)
    
    print("Testing right turn...")
    await controller.turn_right(0.25)
    
    print("Movement controller status:", controller.get_status())


async def test_camera_controller():
    """Test camera controller"""
    print("\n=== Testing Camera Controller ===")
    controller = CameraController()
    
    print("Testing center camera...")
    await controller.center_camera()
    
    print("Testing pan left...")
    await controller.pan_left(30)
    
    print("Testing pan right...")
    await controller.pan_right(60)
    
    print("Testing tilt up...")
    await controller.tilt_up(20)
    
    print("Testing area scan...")
    await controller.scan_area(90, 3)
    
    print("Camera controller status:", controller.get_status())


async def test_llm_service():
    """Test LLM service"""
    print("\n=== Testing LLM Service ===")
    config = BotConfig()
    llm_service = LLMService(config)
    
    # Initialize (may fail if Ollama not available)
    if await llm_service.initialize():
        print("LLM service connected successfully")
        
        # Test task analysis
        task_description = "Move forward and scan the area for objects"
        analysis = await llm_service.analyze_task(task_description, config.capabilities)
        print(f"Task analysis: {analysis}")
        
        # Test action plan generation
        action_plan = await llm_service.generate_action_plan(task_description)
        print(f"Action plan: {action_plan}")
        
    else:
        print("LLM service not available (Ollama not running or model not found)")
    
    await llm_service.cleanup()


async def test_bot_agent():
    """Test bot agent initialization"""
    print("\n=== Testing Bot Agent ===")
    config = BotConfig()
    bot = DummyAiBot(config)
    
    # Initialize
    if await bot.initialize():
        print("Bot initialized successfully")
        print(f"Bot status: {bot.get_status()}")
    else:
        print("Bot initialization failed")
    
    # Simulate a simple task
    print("\nSimulating movement task...")
    await bot._execute_movement_task("move forward", {"direction": "forward", "duration": 1.0})
    
    print("\nSimulating camera task...")
    await bot._execute_camera_task("center camera", {"action": "center"})
    
    await bot.shutdown()


async def main():
    """Run all tests"""
    print("DummyAiBot - Component Testing")
    print("=" * 40)
    
    try:
        await test_movement_controller()
        await test_camera_controller()
        await test_llm_service()
        await test_bot_agent()
        
        print("\n" + "=" * 40)
        print("All tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    asyncio.run(main())
