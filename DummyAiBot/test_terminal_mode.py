#!/usr/bin/env python3
"""Quick test of terminal mode"""

import asyncio
from agents.dummy_bot import DummyAiBot
from config.settings import BotConfig

async def test_terminal():
    config = BotConfig()
    config.terminal_mode = True
    config.agent_id = "test_terminal_bot"
    
    bot = DummyAiBot(config)
    await bot.initialize()
    
    print("Terminal mode test - the bot should start in terminal mode now")
    # We won't actually start it here to avoid blocking

if __name__ == "__main__":
    asyncio.run(test_terminal())
