"""
Agent manager for handling agent registration, lifecycle, and capabilities.
Manages the registry of all connected agents and their states.
"""

import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..core.models import (
    Agent, AgentStatus, AgentCapability, 
    AgentRegistration, Heartbeat, MessageType
)
from ..utils import get_logger, log_agent_activity, generate_unique_id


@dataclass
class AgentConnection:
    """Represents an agent's connection information."""
    agent: Agent
    websocket_id: str
    last_heartbeat: datetime
    connection_established: datetime


class AgentManager:
    """
    Manages agent registration, lifecycle, and capabilities.
    Handles agent discovery, heartbeat monitoring, and capability tracking.
    """
    
    def __init__(self, heartbeat_timeout: int = 30):
        """
        Initialize the agent manager.
        
        Args:
            heartbeat_timeout: Timeout in seconds before considering an agent offline
        """
        self.logger = get_logger(__name__)
        self.heartbeat_timeout = heartbeat_timeout
        
        # Agent storage
        self._agents: Dict[str, Agent] = {}
        self._agent_connections: Dict[str, AgentConnection] = {}
        self._websocket_to_agent: Dict[str, str] = {}
        
        # Capability index for fast lookup
        self._capability_index: Dict[str, Set[str]] = {}
        
        # Background tasks
        self._heartbeat_monitor_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        self.logger.info("AgentManager initialized")
    
    async def start(self) -> None:
        """Start the agent manager and its background tasks."""
        if self._is_running:
            self.logger.warning("AgentManager is already running")
            return
        
        self._is_running = True
        self._heartbeat_monitor_task = asyncio.create_task(self._heartbeat_monitor())
        self.logger.info("AgentManager started")
    
    async def stop(self) -> None:
        """Stop the agent manager and cleanup background tasks."""
        self._is_running = False
        
        if self._heartbeat_monitor_task:
            self._heartbeat_monitor_task.cancel()
            try:
                await self._heartbeat_monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("AgentManager stopped")
    
    async def register_agent(self, registration: AgentRegistration, websocket_id: str) -> bool:
        """
        Register a new agent or update an existing one.
        
        Args:
            registration: Agent registration information
            websocket_id: WebSocket connection ID
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            agent = registration.agent
            agent_id = agent.agent_id
            
            # Validate agent data
            if not self._validate_agent(agent):
                self.logger.error(f"Invalid agent data for agent {agent_id}")
                return False
            
            # Update agent status and metadata
            agent.status = AgentStatus.ONLINE
            agent.last_seen = datetime.utcnow()
            agent.websocket_id = websocket_id
            
            # Store agent
            self._agents[agent_id] = agent
            
            # Create connection info
            connection = AgentConnection(
                agent=agent,
                websocket_id=websocket_id,
                last_heartbeat=datetime.utcnow(),
                connection_established=datetime.utcnow()
            )
            self._agent_connections[agent_id] = connection
            self._websocket_to_agent[websocket_id] = agent_id
            
            # Update capability index
            self._update_capability_index(agent)
            
            log_agent_activity(agent_id, f"Registered with {len(agent.capabilities)} capabilities")
            self.logger.info(f"Agent {agent_id} ({agent.name}) registered successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent and cleanup its resources.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        try:
            if agent_id not in self._agents:
                self.logger.warning(f"Attempted to unregister unknown agent {agent_id}")
                return False
            
            agent = self._agents[agent_id]
            
            # Remove from capability index
            self._remove_from_capability_index(agent)
            
            # Cleanup connection tracking
            if agent_id in self._agent_connections:
                connection = self._agent_connections[agent_id]
                if connection.websocket_id in self._websocket_to_agent:
                    del self._websocket_to_agent[connection.websocket_id]
                del self._agent_connections[agent_id]
            
            # Remove agent
            del self._agents[agent_id]
            
            log_agent_activity(agent_id, "Unregistered")
            self.logger.info(f"Agent {agent_id} unregistered successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def handle_heartbeat(self, heartbeat: Heartbeat, websocket_id: str) -> bool:
        """
        Handle a heartbeat message from an agent.
        
        Args:
            heartbeat: Heartbeat information
            websocket_id: WebSocket connection ID
            
        Returns:
            True if heartbeat was processed successfully, False otherwise
        """
        try:
            agent_id = heartbeat.agent_id
            
            if agent_id not in self._agents:
                self.logger.warning(f"Received heartbeat from unknown agent {agent_id}")
                return False
            
            # Update agent status
            agent = self._agents[agent_id]
            agent.status = heartbeat.status
            agent.last_seen = datetime.utcnow()
            
            # Update connection info
            if agent_id in self._agent_connections:
                connection = self._agent_connections[agent_id]
                connection.last_heartbeat = datetime.utcnow()
                
                # Update metadata with system info
                if heartbeat.cpu_usage is not None:
                    agent.metadata['cpu_usage'] = heartbeat.cpu_usage
                if heartbeat.memory_usage is not None:
                    agent.metadata['memory_usage'] = heartbeat.memory_usage
                if heartbeat.active_tasks:
                    agent.metadata['active_tasks'] = heartbeat.active_tasks
                if heartbeat.last_error:
                    agent.metadata['last_error'] = heartbeat.last_error
            
            self.logger.debug(f"Processed heartbeat from agent {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process heartbeat: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent object or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_agent_by_websocket(self, websocket_id: str) -> Optional[Agent]:
        """
        Get an agent by WebSocket ID.
        
        Args:
            websocket_id: WebSocket connection ID
            
        Returns:
            Agent object or None if not found
        """
        agent_id = self._websocket_to_agent.get(websocket_id)
        return self._agents.get(agent_id) if agent_id else None
    
    def get_all_agents(self) -> List[Agent]:
        """
        Get all registered agents.
        
        Returns:
            List of all agents
        """
        return list(self._agents.values())
    
    def get_online_agents(self) -> List[Agent]:
        """
        Get all online agents.
        
        Returns:
            List of online agents
        """
        return [agent for agent in self._agents.values() if agent.status == AgentStatus.ONLINE]
    
    def get_agents_by_capability(self, capability_name: str) -> List[Agent]:
        """
        Get all agents that have a specific capability.
        
        Args:
            capability_name: Name of the capability to search for
            
        Returns:
            List of agents with the specified capability
        """
        agent_ids = self._capability_index.get(capability_name, set())
        return [self._agents[agent_id] for agent_id in agent_ids if agent_id in self._agents]
    
    def find_best_agent_for_capability(self, capability_name: str, exclude_busy: bool = True) -> Optional[Agent]:
        """
        Find the best agent for a specific capability.
        
        Args:
            capability_name: Name of the required capability
            exclude_busy: Whether to exclude busy agents
            
        Returns:
            Best available agent or None if no suitable agent found
        """
        candidates = self.get_agents_by_capability(capability_name)
        
        if exclude_busy:
            candidates = [agent for agent in candidates if agent.status not in [AgentStatus.BUSY, AgentStatus.ERROR]]
        
        if not candidates:
            return None
        
        # Simple selection strategy: prefer online agents, then by last seen
        online_agents = [agent for agent in candidates if agent.status == AgentStatus.ONLINE]
        if online_agents:
            # Sort by last seen (most recent first)
            return sorted(online_agents, key=lambda a: a.last_seen or datetime.min, reverse=True)[0]
        
        # If no online agents, return any available agent
        return candidates[0]
    
    def get_agent_capabilities(self, agent_id: str) -> List[AgentCapability]:
        """
        Get capabilities of a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of agent capabilities
        """
        agent = self.get_agent(agent_id)
        return agent.capabilities if agent else []
    
    def get_all_capabilities(self) -> Set[str]:
        """
        Get all unique capabilities across all agents.
        
        Returns:
            Set of all capability names
        """
        return set(self._capability_index.keys())
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """
        Update an agent's status.
        
        Args:
            agent_id: ID of the agent
            status: New status
            
        Returns:
            True if update was successful, False otherwise
        """
        if agent_id not in self._agents:
            return False
        
        old_status = self._agents[agent_id].status
        self._agents[agent_id].status = status
        self._agents[agent_id].last_seen = datetime.utcnow()
        
        log_agent_activity(agent_id, f"Status changed from {old_status.value} to {status.value}")
        return True
    
    def get_system_statistics(self) -> Dict[str, any]:
        """
        Get system statistics about registered agents.
        
        Returns:
            Dictionary containing system statistics
        """
        total_agents = len(self._agents)
        status_counts = {}
        
        for status in AgentStatus:
            status_counts[status.value] = sum(1 for agent in self._agents.values() if agent.status == status)
        
        capabilities_count = len(self._capability_index)
        
        return {
            'total_agents': total_agents,
            'status_distribution': status_counts,
            'total_capabilities': capabilities_count,
            'online_agents': status_counts.get(AgentStatus.ONLINE.value, 0),
            'capability_distribution': {
                cap: len(agents) for cap, agents in self._capability_index.items()
            }
        }
    
    def _validate_agent(self, agent: Agent) -> bool:
        """
        Validate agent data.
        
        Args:
            agent: Agent to validate
            
        Returns:
            True if agent is valid, False otherwise
        """
        if not agent.agent_id or not agent.name or not agent.agent_type:
            return False
        
        # Validate capabilities
        for capability in agent.capabilities:
            if not capability.name or not capability.description:
                return False
        
        return True
    
    def _update_capability_index(self, agent: Agent) -> None:
        """Update the capability index with agent's capabilities."""
        for capability in agent.capabilities:
            if capability.name not in self._capability_index:
                self._capability_index[capability.name] = set()
            self._capability_index[capability.name].add(agent.agent_id)
    
    def _remove_from_capability_index(self, agent: Agent) -> None:
        """Remove agent from capability index."""
        for capability in agent.capabilities:
            if capability.name in self._capability_index:
                self._capability_index[capability.name].discard(agent.agent_id)
                if not self._capability_index[capability.name]:
                    del self._capability_index[capability.name]
    
    async def _heartbeat_monitor(self) -> None:
        """Background task to monitor agent heartbeats and mark offline agents."""
        while self._is_running:
            try:
                current_time = datetime.utcnow()
                timeout_threshold = current_time - timedelta(seconds=self.heartbeat_timeout)
                
                offline_agents = []
                
                for agent_id, connection in self._agent_connections.items():
                    if connection.last_heartbeat < timeout_threshold and connection.agent.status != AgentStatus.OFFLINE:
                        offline_agents.append(agent_id)
                
                # Mark agents as offline
                for agent_id in offline_agents:
                    await self.update_agent_status(agent_id, AgentStatus.OFFLINE)
                    log_agent_activity(agent_id, "Marked offline due to heartbeat timeout", "WARNING")
                
                # Sleep before next check
                await asyncio.sleep(self.heartbeat_timeout // 2)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(5)  # Brief pause on error
