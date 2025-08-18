#!/usr/bin/env python3
"""
Test to find correct invoke API
"""

import asyncio
import sys
import os
import inspect

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory

async def test_invoke_api():
    # Create kernel and service
    kernel = sk.Kernel()
    chat_completion = OllamaChatCompletion(
        ai_model_id="llama3.2:1b",
        service_id="ollama_chat"
    )
    kernel.add_service(chat_completion)
    
    # Create agent
    agent = ChatCompletionAgent(
        kernel=kernel,
        name="TestAgent",
        instructions="You are a test assistant."
    )
    
    print("ChatCompletionAgent.invoke signature:")
    print(inspect.signature(agent.invoke))
    
    # Test different invoke methods
    chat_history = ChatHistory()
    chat_history.add_user_message("Hello")
    
    try:
        print("\nTrying invoke(chat_history)...")
        response = agent.invoke(chat_history)
        print(f"Type of response: {type(response)}")
        if hasattr(response, '__aiter__'):
            print("Response is async iterable")
            async for message in response:
                print(f"Message: {message}")
                break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_invoke_api())
