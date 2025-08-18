#!/usr/bin/env python3
"""
Test the updated movement plugin with duration parameters.
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.agents.ollama_agent import OllamaBotAgent

# Minimal logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

async def test_duration_params():
    """Test movement commands with duration parameters."""
    print("🚀 Testing Duration Parameters")
    print("="*40)
    
    agent = OllamaBotAgent(model_name="llama3.2:1b")
    
    try:
        print("🔧 Initializing agent...")
        await agent.initialize()
        print("✅ Ready!\n")
        
        # Test commands with specific durations
        test_commands = [
            "Move forward for 2 seconds",
            "Turn left slowly for 0.5 seconds",
            "Move fast for 3 seconds",
            "Make a quick turn right"
        ]
        
        for i, command in enumerate(test_commands, 1):
            print(f"🧪 Test {i}: '{command}'")
            print("🔄 Processing...")
            
            response = await agent.process_command(command)
            print(f"🤖 Agent: {response[:150]}...")
            print()
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        print("✅ Duration parameter tests completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("\n🧹 Cleaning up...")
        agent.cleanup()
        print("✅ Done")

if __name__ == "__main__":
    asyncio.run(test_duration_params())
