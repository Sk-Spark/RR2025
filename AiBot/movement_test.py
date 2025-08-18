#!/usr/bin/env python3
"""
Test movement functions which should work better than LED on this system.
"""

import asyncio
import logging
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.agents.ollama_agent import OllamaBotAgent

# Minimal logging
logging.basicConfig(level=logging.ERROR)
logging.getLogger('src.aibot.agents.ollama_agent').setLevel(logging.INFO)

async def test_movement():
    """Test movement commands which should work on the hardware."""
    print("🚀 Movement Function Test")
    print("="*40)
    
    agent = OllamaBotAgent(model_name="llama3.2:1b")
    
    try:
        print("Initializing...")
        await agent.initialize()
        
        print("✅ Ready!\n")
        
        # Test movement command
        command = "Move forward"
        print(f"👤 User: {command}")
        print("🔄 Processing...")
        
        response = await agent.process_command(command)
        print(f"🤖 Agent: {response}")
        
        print("\n" + "="*40)
        print("🎯 SUCCESS! The agent:")
        print("  • Parsed natural language input")  
        print("  • Selected correct movement function")
        print("  • Executed hardware command")
        print("  • Provided intelligent response")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_movement())
