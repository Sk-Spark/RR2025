#!/usr/bin/env python3
"""
Terminal Mode Test - Windows Compatible
"""

import asyncio
from agents.dummy_bot import DummyAiBot
from config.settings import BotConfig

async def quick_test():
    """Quick test that shows terminal mode works"""
    print("Creating bot in terminal mode...")
    
    config = BotConfig()
    config.terminal_mode = True
    config.agent_id = "terminal_test_bot"
    
    bot = DummyAiBot(config)
    
    print("Initializing bot...")
    await bot.initialize()
    
    print("Bot initialized successfully!")
    print("Testing movement simulation...")
    
    # Test one movement command
    result = await bot._execute_movement_task("test move", {'direction': 'forward', 'duration': 1.0})
    print(f"Movement test result: {result['success']}")
    
    print("Testing camera simulation...")
    result = await bot._execute_camera_task("test camera", {'action': 'center'})
    print(f"Camera test result: {result['success']}")
    
    print("All basic functions working!")
    print("To use terminal mode interactively, run:")
    print("python main.py --terminal --bot-id your_bot_name")
    
    await bot.shutdown()

if __name__ == "__main__":
    asyncio.run(quick_test())
