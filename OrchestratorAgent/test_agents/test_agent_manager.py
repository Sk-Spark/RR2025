"""
Test Agent Manager - Utility for managing and running test dummy agents
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, List, Optional
from aibot_agent import AIBotAgent

class TestAgentManager:
    """Manages multiple test agents for orchestrator testing"""
    
    def __init__(self):
        self.agents = {}
        self.running = False
        self.logger = logging.getLogger("TestAgentManager")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def create_agent(self, agent_type: str, agent_id: str = None) -> str:
        """Create a new test agent of specified type"""
        if not agent_id:
            agent_id = f"{agent_type}_{len([a for a in self.agents.values() if a.agent_type == agent_type]) + 1:03d}"
        
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID '{agent_id}' already exists")
        
        if agent_type == "aibot":
            agent = AIBotAgent(agent_id)
        else:
            raise ValueError(f"Agent type '{agent_type}' is no longer supported. Use 'aibot' for comprehensive capabilities.")
        
        self.agents[agent_id] = agent
        self.logger.info(f"Created {agent_type} agent: {agent_id}")
        return agent_id
    
    def remove_agent(self, agent_id: str):
        """Remove an agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            # Disconnect if connected
            if hasattr(agent, 'disconnect'):
                asyncio.create_task(agent.disconnect())
            del self.agents[agent_id]
            self.logger.info(f"Removed agent: {agent_id}")
        else:
            self.logger.warning(f"Agent not found: {agent_id}")
    
    async def start_agent(self, agent_id: str):
        """Start a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        agent = self.agents[agent_id]
        self.logger.info(f"Starting agent: {agent_id}")
        
        try:
            await agent.connect_to_orchestrator()
        except Exception as e:
            self.logger.error(f"Failed to start agent {agent_id}: {e}")
            raise
    
    async def stop_agent(self, agent_id: str):
        """Stop a specific agent"""
        if agent_id not in self.agents:
            self.logger.warning(f"Agent not found: {agent_id}")
            return
        
        agent = self.agents[agent_id]
        self.logger.info(f"Stopping agent: {agent_id}")
        
        try:
            await agent.disconnect()
        except Exception as e:
            self.logger.error(f"Error stopping agent {agent_id}: {e}")
    
    async def start_all_agents(self):
        """Start all agents concurrently"""
        if not self.agents:
            self.logger.warning("No agents to start")
            return
        
        self.logger.info(f"Starting {len(self.agents)} agents...")
        self.running = True
        
        # Start all agents concurrently
        tasks = []
        for agent_id, agent in self.agents.items():
            task = asyncio.create_task(self._run_agent_with_retry(agent_id, agent))
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Error in agent tasks: {e}")
        finally:
            self.running = False
    
    async def _run_agent_with_retry(self, agent_id: str, agent, max_retries: int = 3):
        """Run agent with automatic retry on connection failure"""
        retries = 0
        
        while self.running and retries < max_retries:
            try:
                self.logger.info(f"Connecting agent {agent_id} (attempt {retries + 1})")
                await agent.connect_to_orchestrator()
                break  # Success
            except Exception as e:
                retries += 1
                self.logger.error(f"Agent {agent_id} connection failed (attempt {retries}): {e}")
                
                if retries < max_retries:
                    # Wait before retry with exponential backoff
                    wait_time = 2 ** retries
                    self.logger.info(f"Retrying agent {agent_id} in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Agent {agent_id} failed to connect after {max_retries} attempts")
    
    async def stop_all_agents(self):
        """Stop all agents"""
        self.logger.info("Stopping all agents...")
        self.running = False
        
        # Stop all agents concurrently
        tasks = []
        for agent_id, agent in self.agents.items():
            task = asyncio.create_task(agent.disconnect())
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info("All agents stopped")
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all agents"""
        return [
            {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "agent_type": agent.agent_type,
                "capabilities": agent.capabilities,
                "is_connected": agent.is_connected
            }
            for agent in self.agents.values()
        ]
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, any]]:
        """Get status of specific agent"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.agent_name,
            "agent_type": agent.agent_type,
            "capabilities": agent.capabilities,
            "is_connected": agent.is_connected,
            "current_task": getattr(agent, 'current_task', None)
        }
    
    async def create_default_test_fleet(self):
        """Create a default fleet of test agents"""
        self.logger.info("Creating default test fleet...")
        
        # Create comprehensive AI bot agents (realistic scenario)
        # Each aibot includes all capabilities: movement, vision, sensors, navigation, AI
        self.create_agent("aibot", "aibot_001")
        self.create_agent("aibot", "aibot_002")
        self.create_agent("aibot", "aibot_003")
        
        self.logger.info(f"Created {len(self.agents)} comprehensive AI bot agents")
        self.logger.info("Each agent includes: movement, vision, sensors, navigation, and AI capabilities")


async def main():
    """Main function for running test agents"""
    manager = TestAgentManager()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down agents...")
        asyncio.create_task(manager.stop_all_agents())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create default test fleet
        await manager.create_default_test_fleet()
        
        # Print agent list
        print("\nCreated Test Agents:")
        print("-" * 60)
        for agent_info in manager.list_agents():
            print(f"ID: {agent_info['agent_id']}")
            print(f"Name: {agent_info['agent_name']}")
            print(f"Type: {agent_info['agent_type']}")
            print(f"Capabilities: {', '.join(agent_info['capabilities'][:3])}...")
            print("-" * 60)
        
        print(f"\nStarting {len(manager.agents)} test agents...")
        print("Press Ctrl+C to stop all agents")
        
        # Start all agents
        await manager.start_all_agents()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await manager.stop_all_agents()
        print("Test agent manager shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
