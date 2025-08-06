"""
WebSocket server for handling agent communications.
Manages WebSocket connections, message routing, and protocol handling.
"""

import asyncio
import json
import websockets
from typing import Dict, Set, Optional, Callable, Any
from datetime import datetime
import uuid

from ..core.models import (
    Message, MessageType, AgentRegistration, Heartbeat,
    TaskAssignment, TaskUpdate, TaskResult
)
from ..utils import get_logger, log_websocket_event, generate_unique_id, format_error_message


class WebSocketConnection:
    """Represents a WebSocket connection with metadata."""
    
    def __init__(self, websocket, connection_id: str, remote_address: str):
        self.websocket = websocket
        self.connection_id = connection_id
        self.remote_address = remote_address
        self.connected_at = datetime.utcnow()
        self.agent_id: Optional[str] = None
        self.last_ping = datetime.utcnow()
        self.last_pong = datetime.utcnow()


class WebSocketServer:
    """
    WebSocket server for handling agent communications.
    Manages connections, message routing, and protocol handling.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, max_connections: int = 100):
        """
        Initialize the WebSocket server.
        
        Args:
            host: Server host address
            port: Server port
            max_connections: Maximum number of concurrent connections
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.logger = get_logger(__name__)
        
        # Connection management
        self._connections: Dict[str, WebSocketConnection] = {}
        self._agent_connections: Dict[str, str] = {}  # agent_id -> connection_id
        
        # Message handlers
        self._message_handlers: Dict[MessageType, Callable] = {}
        
        # Server state
        self._server = None
        self._is_running = False
        self._background_tasks: Set[asyncio.Task] = set()
        
        # Metrics
        self._messages_processed = 0
        self._connections_established = 0
        
        self.logger.info(f"WebSocketServer initialized on {host}:{port}")
    
    async def start(self) -> None:
        """Start the WebSocket server."""
        if self._is_running:
            self.logger.warning("WebSocket server is already running")
            return
        
        try:
            self._server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port,
                max_size=1024 * 1024,  # 1MB max message size
                ping_interval=20,
                ping_timeout=10
            )
            
            self._is_running = True
            
            # Start background tasks
            self._start_background_tasks()
            
            log_websocket_event("SERVER_STARTED", details=f"{self.host}:{self.port}")
            self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the WebSocket server."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # Stop background tasks
        await self._stop_background_tasks()
        
        # Close all connections
        await self._close_all_connections()
        
        # Stop server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        log_websocket_event("SERVER_STOPPED")
        self.logger.info("WebSocket server stopped")
    
    def register_message_handler(self, message_type: MessageType, handler: Callable) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async handler function
        """
        self._message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for {message_type.value}")
    
    async def send_message_to_agent(self, agent_id: str, message: Message) -> bool:
        """
        Send a message to a specific agent.
        
        Args:
            agent_id: Target agent ID
            message: Message to send
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        connection_id = self._agent_connections.get(agent_id)
        if not connection_id:
            self.logger.warning(f"No connection found for agent {agent_id}")
            return False
        
        return await self._send_message_to_connection(connection_id, message)
    
    async def broadcast_message(self, message: Message, exclude_agent: Optional[str] = None) -> int:
        """
        Broadcast a message to all connected agents.
        
        Args:
            message: Message to broadcast
            exclude_agent: Optional agent ID to exclude from broadcast
            
        Returns:
            Number of agents the message was sent to
        """
        sent_count = 0
        
        for agent_id, connection_id in self._agent_connections.items():
            if exclude_agent and agent_id == exclude_agent:
                continue
            
            if await self._send_message_to_connection(connection_id, message):
                sent_count += 1
        
        self.logger.debug(f"Broadcast message to {sent_count} agents")
        return sent_count
    
    def get_connected_agents(self) -> Set[str]:
        """Get set of connected agent IDs."""
        return set(self._agent_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get current number of connections."""
        return len(self._connections)
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            'is_running': self._is_running,
            'active_connections': len(self._connections),
            'connected_agents': len(self._agent_connections),
            'messages_processed': self._messages_processed,
            'connections_established': self._connections_established,
            'host': self.host,
            'port': self.port
        }
    
    async def _handle_connection(self, websocket, path) -> None:
        """Handle a new WebSocket connection."""
        connection_id = generate_unique_id("conn")
        remote_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        
        # Check connection limit
        if len(self._connections) >= self.max_connections:
            await websocket.close(code=1013, reason="Server at capacity")
            log_websocket_event("CONNECTION_REJECTED", connection_id, "Server at capacity")
            return
        
        connection = WebSocketConnection(websocket, connection_id, remote_address)
        self._connections[connection_id] = connection
        self._connections_established += 1
        
        log_websocket_event("CONNECTION_ESTABLISHED", connection_id, remote_address)
        self.logger.info(f"New connection established: {connection_id} from {remote_address}")
        
        try:
            await self._handle_connection_messages(connection)
        except websockets.exceptions.ConnectionClosed:
            log_websocket_event("CONNECTION_CLOSED", connection_id, "Connection closed by client")
        except Exception as e:
            log_websocket_event("CONNECTION_ERROR", connection_id, format_error_message(e))
            self.logger.error(f"Error handling connection {connection_id}: {e}")
        finally:
            await self._cleanup_connection(connection_id)
    
    async def _handle_connection_messages(self, connection: WebSocketConnection) -> None:
        """Handle messages from a WebSocket connection."""
        async for raw_message in connection.websocket:
            try:
                # Parse message
                message_data = json.loads(raw_message)
                message = self._parse_message(message_data, connection.connection_id)
                
                if message:
                    self._messages_processed += 1
                    await self._process_message(message, connection)
                
            except json.JSONDecodeError as e:
                log_websocket_event("MESSAGE_ERROR", connection.connection_id, f"Invalid JSON: {e}")
                await self._send_error_response(connection, "Invalid JSON format")
            except Exception as e:
                log_websocket_event("MESSAGE_ERROR", connection.connection_id, format_error_message(e))
                self.logger.error(f"Error processing message from {connection.connection_id}: {e}")
                await self._send_error_response(connection, "Message processing error")
    
    def _parse_message(self, data: Dict[str, Any], connection_id: str) -> Optional[Message]:
        """Parse raw message data into a Message object."""
        try:
            # Validate required fields
            required_fields = ['message_type', 'sender_id', 'payload']
            for field in required_fields:
                if field not in data:
                    log_websocket_event("MESSAGE_ERROR", connection_id, f"Missing field: {field}")
                    return None
            
            # Parse message type
            try:
                message_type = MessageType(data['message_type'])
            except ValueError:
                log_websocket_event("MESSAGE_ERROR", connection_id, f"Invalid message type: {data['message_type']}")
                return None
            
            message = Message(
                message_id=data.get('message_id', generate_unique_id("msg")),
                message_type=message_type,
                sender_id=data['sender_id'],
                recipient_id=data.get('recipient_id'),
                payload=data['payload'],
                correlation_id=data.get('correlation_id')
            )
            
            return message
            
        except Exception as e:
            log_websocket_event("MESSAGE_ERROR", connection_id, f"Parse error: {e}")
            return None
    
    async def _process_message(self, message: Message, connection: WebSocketConnection) -> None:
        """Process a received message."""
        log_websocket_event(
            "MESSAGE_RECEIVED", 
            connection.connection_id, 
            f"Type: {message.message_type.value}, From: {message.sender_id}"
        )
        
        # Update connection info based on message
        if message.message_type == MessageType.REGISTER_AGENT:
            # Associate connection with agent
            connection.agent_id = message.sender_id
            self._agent_connections[message.sender_id] = connection.connection_id
        
        # Handle ping/pong
        if message.message_type == MessageType.PING:
            await self._handle_ping(connection, message)
            return
        elif message.message_type == MessageType.PONG:
            connection.last_pong = datetime.utcnow()
            return
        
        # Route message to handler
        handler = self._message_handlers.get(message.message_type)
        if handler:
            try:
                await handler(message, connection.connection_id)
            except Exception as e:
                self.logger.error(f"Error in message handler for {message.message_type.value}: {e}")
                await self._send_error_response(connection, f"Handler error: {e}")
        else:
            log_websocket_event("MESSAGE_ERROR", connection.connection_id, f"No handler for {message.message_type.value}")
            await self._send_error_response(connection, f"No handler for message type: {message.message_type.value}")
    
    async def _handle_ping(self, connection: WebSocketConnection, ping_message: Message) -> None:
        """Handle ping message by sending pong response."""
        pong_message = Message(
            message_id=generate_unique_id("msg"),
            message_type=MessageType.PONG,
            sender_id="orchestrator",
            recipient_id=ping_message.sender_id,
            correlation_id=ping_message.message_id
        )
        
        await self._send_message_to_connection(connection.connection_id, pong_message)
        connection.last_ping = datetime.utcnow()
    
    async def _send_message_to_connection(self, connection_id: str, message: Message) -> bool:
        """Send a message to a specific connection."""
        connection = self._connections.get(connection_id)
        if not connection:
            return False
        
        try:
            message_data = {
                'message_id': message.message_id,
                'message_type': message.message_type.value,
                'sender_id': message.sender_id,
                'recipient_id': message.recipient_id,
                'timestamp': message.timestamp.isoformat(),
                'payload': message.payload,
                'correlation_id': message.correlation_id
            }
            
            await connection.websocket.send(json.dumps(message_data))
            
            log_websocket_event(
                "MESSAGE_SENT", 
                connection_id, 
                f"Type: {message.message_type.value}, To: {message.recipient_id}"
            )
            
            return True
            
        except Exception as e:
            log_websocket_event("MESSAGE_ERROR", connection_id, f"Send error: {e}")
            return False
    
    async def _send_error_response(self, connection: WebSocketConnection, error_message: str) -> None:
        """Send an error response to a connection."""
        error_msg = Message(
            message_id=generate_unique_id("msg"),
            message_type=MessageType.ERROR,
            sender_id="orchestrator",
            recipient_id=connection.agent_id or "unknown",
            payload={'error': error_message}
        )
        
        await self._send_message_to_connection(connection.connection_id, error_msg)
    
    async def _cleanup_connection(self, connection_id: str) -> None:
        """Clean up a connection and associated resources."""
        connection = self._connections.get(connection_id)
        if not connection:
            return
        
        # Remove from agent connections
        if connection.agent_id and connection.agent_id in self._agent_connections:
            del self._agent_connections[connection.agent_id]
        
        # Remove from connections
        del self._connections[connection_id]
        
        log_websocket_event("CONNECTION_CLEANUP", connection_id, f"Agent: {connection.agent_id}")
        self.logger.info(f"Connection {connection_id} cleaned up")
    
    async def _close_all_connections(self) -> None:
        """Close all active connections."""
        if not self._connections:
            return
        
        close_tasks = []
        for connection in self._connections.values():
            close_tasks.append(connection.websocket.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self._connections.clear()
        self._agent_connections.clear()
        
        self.logger.info("All connections closed")
    
    def _start_background_tasks(self) -> None:
        """Start background tasks."""
        # Add connection health monitoring task
        task = asyncio.create_task(self._monitor_connections())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
    
    async def _stop_background_tasks(self) -> None:
        """Stop all background tasks."""
        for task in self._background_tasks:
            task.cancel()
        
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        self._background_tasks.clear()
    
    async def _monitor_connections(self) -> None:
        """Monitor connection health and cleanup stale connections."""
        while self._is_running:
            try:
                current_time = datetime.utcnow()
                stale_connections = []
                
                for connection_id, connection in self._connections.items():
                    # Check for stale connections (no pong received for 60 seconds)
                    if (current_time - connection.last_pong).total_seconds() > 60:
                        stale_connections.append(connection_id)
                
                # Cleanup stale connections
                for connection_id in stale_connections:
                    log_websocket_event("CONNECTION_TIMEOUT", connection_id, "No pong received")
                    connection = self._connections.get(connection_id)
                    if connection:
                        try:
                            await connection.websocket.close()
                        except Exception:
                            pass  # Connection might already be closed
                        await self._cleanup_connection(connection_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in connection monitor: {e}")
                await asyncio.sleep(5)
