#!/usr/bin/env python3
"""
Test agent without LED control - movement only.
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.agents.ollama_agent import OllamaBotAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

async def test_movement_only():
    """Test agent with only movement functions."""
    print("🤖 Testing Movement-Only Agent")
    print("="*40)
    
    agent = OllamaBotAgent(model_name="llama3.2:1b")
    
    try:
        print("🔧 Initializing agent (no LED)...")
        # Note: no led_pin parameter needed anymore
        success = await agent.initialize()
        
        if success:
            print("✅ Agent initialized successfully!")
            print("   - No GPIO conflicts (LED removed)")
            print("   - Movement functions available")
            print("   - Agent should work cleanly")
            
            # Verify components
            if agent.agent is not None:
                print("✅ ChatCompletionAgent created")
            if agent.movement_plugin is not None:
                print("✅ Movement plugin created")
                
            # Quick test
            print("\n🧪 Quick function test...")
            response = await agent.process_command("What can you do?")
            print(f"🤖 Agent Response: {response[:100]}...")
            
        else:
            print("❌ Agent initialization failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("\n🧹 Cleaning up...")
        agent.cleanup()
        print("✅ Done")

if __name__ == "__main__":
    asyncio.run(test_movement_only())
