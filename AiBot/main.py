#!/usr/bin/env python3
"""
Main Entry Point for AiBot
This file provides the main entry point for the AiBot application.
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aibot import LEDControlApp


async def main():
    """Main entry point for the AiBot application."""
    app = LEDControlApp()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program terminated by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)