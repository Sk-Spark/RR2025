#!/usr/bin/env python3
"""Test to check capabilities"""

import asyncio
from agents.dummy_bot import DummyAiBot
from config.settings import BotConfig

async def test_capabilities():
    print("Testing DummyAiBot capabilities...")
    
    config = BotConfig()
    config.terminal_mode = True
    config.agent_id = "test_capabilities_bot"
    
    print(f"Config capabilities: {config.capabilities}")
    print(f"Config capabilities type: {type(config.capabilities)}")
    
    bot = DummyAiBot(config)
    await bot.initialize()
    
    status = bot.get_status()
    
    print("\nBot Status:")
    print(f"  ID: {status['bot_id']}")
    print(f"  Status: {status['status']}")
    print(f"  Capabilities: {status['capabilities']}")
    print(f"  Capabilities type: {type(status['capabilities'])}")
    print(f"  Capabilities length: {len(status['capabilities']) if status['capabilities'] else 'None'}")
    
    if status['capabilities']:
        print("  Individual capabilities:")
        for i, cap in enumerate(status['capabilities']):
            print(f"    {i+1}. {cap}")
    
    await bot.shutdown()

if __name__ == "__main__":
    asyncio.run(test_capabilities())
