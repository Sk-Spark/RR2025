"""
Test Agent Runner - Simple script to run individual test agents
"""

import asyncio
import argparse
import sys
import os

# Add current directory to path to import test agents
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aibot_agent import AIBotAgent
from test_agent_manager import TestAgentManager

async def run_single_agent(agent_type: str, agent_id: str = None):
    """Run a single test agent"""
    print(f"Starting {agent_type} agent...")
    
    if agent_type == "aibot":
        agent = AIBotAgent(agent_id or "aibot_test")
    else:
        print(f"Agent type '{agent_type}' is no longer supported.")
        print(f"The specialized agents have been consolidated into the comprehensive 'aibot' type.")
        print(f"Use --type aibot for full capabilities including movement, vision, sensors, and navigation.")
        return
    
    try:
        print(f"Agent {agent.agent_name} connecting to orchestrator...")
        print("Press Ctrl+C to disconnect")
        await agent.connect_to_orchestrator()
    except KeyboardInterrupt:
        print("\nDisconnecting agent...")
        await agent.disconnect()
        print("Agent disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await agent.disconnect()

async def run_test_fleet():
    """Run the full test fleet"""
    manager = TestAgentManager()
    
    try:
        print("Creating test fleet...")
        await manager.create_default_test_fleet()
        
        print("\nTest Fleet Created:")
        print("=" * 50)
        for agent_info in manager.list_agents():
            print(f"  {agent_info['agent_type'].title()} Agent: {agent_info['agent_id']}")
        print("=" * 50)
        
        print("\nStarting all agents...")
        print("Press Ctrl+C to stop all agents")
        
        await manager.start_all_agents()
        
    except KeyboardInterrupt:
        print("\nStopping all agents...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await manager.stop_all_agents()
        print("Test fleet shutdown complete")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run test dummy AI bot agents")
    parser.add_argument("--type", "-t", 
                       choices=["aibot", "fleet"],
                       default="aibot",
                       help="Type of agent to run (default: aibot)")
    parser.add_argument("--id", "-i",
                       help="Custom agent ID")
    parser.add_argument("--list", "-l", action="store_true",
                       help="List available agent types")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available agent types:")
        print("  aibot       - Comprehensive AI bot with all capabilities (RECOMMENDED)")
        print("                Includes: movement, vision, sensors, navigation, and AI")
        print("  fleet       - Run multiple aibot instances together")
        print("")
        print("Note: Specialized agents (movement, camera, sensor, navigation) have been")
        print("      consolidated into the comprehensive 'aibot' type for better simulation.")
        return
    
    print("=" * 60)
    print("Test Dummy AI Bot Agents for Orchestrator")
    print("=" * 60)
    print("🎯 These test agents simulate AI bot minions for the orchestrator")
    print("💡 Start the orchestrator in interactive mode to manage scenarios:")
    print("   cd .. && python main.py")
    print("=" * 60)
    
    if args.type == "fleet":
        print("Running test fleet with all agent types...")
        asyncio.run(run_test_fleet())
    else:
        print(f"Running single {args.type} agent...")
        asyncio.run(run_single_agent(args.type, args.id))

if __name__ == "__main__":
    main()
