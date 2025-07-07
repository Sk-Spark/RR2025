#!/usr/bin/env python3
"""
Main Entry Point for LED Control Application
This file provides backward compatibility and serves as the main entry point.
"""

import asyncio
import sys
from app import LEDControlApp


async def main():
    """Main entry point for the LED control application."""
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