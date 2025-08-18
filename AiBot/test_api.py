#!/usr/bin/env python3
"""
Quick test to check the ChatCompletionAgent API
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.agents import ChatCompletionAgent

async def test_agent_api():
    # Create kernel and service
    kernel = sk.Kernel()
    chat_completion = OllamaChatCompletion(
        ai_model_id="llama3.2:1b",
        service_id="ollama_chat"
    )
    kernel.add_service(chat_completion)
    
    print("Available parameters for ChatCompletionAgent:")
    print(ChatCompletionAgent.__init__.__annotations__)
    
    # Try minimal initialization
    try:
        agent = ChatCompletionAgent(
            kernel=kernel,
            name="TestAgent",
            instructions="You are a test assistant."
        )
        print("✅ Minimal agent created successfully!")
        return agent
    except Exception as e:
        print(f"❌ Error with minimal params: {e}")
        
    # Try even more minimal
    try:
        agent = ChatCompletionAgent(
            kernel=kernel,
            instructions="You are a test assistant."
        )
        print("✅ Super minimal agent created successfully!")
        return agent
    except Exception as e:
        print(f"❌ Error with super minimal params: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_api())
