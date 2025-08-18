#!/usr/bin/env python3
"""
Test script for the OllamaBotAgent using the Semantic Kernel agent framework.
"""

import asyncio
import logging
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.aibot.agents.ollama_agent import OllamaBotAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_agent():
    """Test the OllamaBotAgent with various commands."""
    print("🤖 Testing OllamaBotAgent with Semantic Kernel...")
    
    # Create agent instance
    agent = OllamaBotAgent(model_name="llama3.2:1b")
    
    try:
        print("\n1️⃣ Initializing agent...")
        success = await agent.initialize()
        
        if not success:
            print("❌ Failed to initialize agent")
            return
        
        print("✅ Agent initialized successfully!")
        
        # Test commands
        test_commands = [
            "Hello, can you introduce yourself?",
            "What functions do you have available?",
            "Turn on the LED",
            "Get LED status", 
            "Turn off the LED",
            "Move forward",
            "Turn right",
            "Stop the robot",
            "Get movement status"
        ]
        
        print("\n2️⃣ Testing commands...")
        for i, command in enumerate(test_commands, 1):
            print(f"\n--- Test {i}: '{command}' ---")
            try:
                response = await agent.process_command(command)
                print(f"🔵 Agent Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Small delay between commands
            await asyncio.sleep(1)
        
        print("\n3️⃣ Testing complex command...")
        complex_command = "Make a square pattern"
        print(f"\n--- Complex Test: '{complex_command}' ---")
        try:
            response = await agent.process_command(complex_command)
            print(f"🔵 Agent Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("\n4️⃣ Cleaning up...")
        agent.cleanup()
        print("✅ Cleanup completed")

if __name__ == "__main__":
    print("🚀 Starting Agent Test...")
    asyncio.run(test_agent())
    print("🏁 Test completed!")
