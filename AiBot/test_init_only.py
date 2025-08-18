#!/usr/bin/env python3
"""
Simple test to verify agent initialization handles GPIO errors gracefully.
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

async def test_init():
    """Test agent initialization with error handling."""
    print("🧪 Testing Agent Initialization")
    print("="*40)
    
    agent = OllamaBotAgent(model_name="llama3.2:1b")
    
    try:
        print("🔧 Initializing agent (GPIO errors are expected)...")
        success = await agent.initialize()
        
        if success:
            print("✅ Agent initialized successfully!")
            print("   - Even with GPIO errors, the agent can still work")
            print("   - Movement functions should work (PCA9685)")
            print("   - LED functions will gracefully fail")
            
            # Test that agent object is properly created
            if agent.agent is not None:
                print("✅ ChatCompletionAgent created successfully")
            else:
                print("❌ ChatCompletionAgent creation failed")
                
            if agent.movement_plugin is not None:
                print("✅ Movement plugin created successfully")
            else:
                print("❌ Movement plugin creation failed")
                
            if agent.led_plugin is not None:
                print("✅ LED plugin created successfully (will handle hardware errors)")
            else:
                print("❌ LED plugin creation failed")
        else:
            print("❌ Agent initialization failed completely")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("\n🧹 Cleaning up...")
        agent.cleanup()
        print("✅ Cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_init())
