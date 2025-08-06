"""
Terminal interface for the Orchestrator Agent.
Provides an interactive command-line interface for users to interact with the orchestrator.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

from ..utils import get_logger, format_error_message


class TerminalInterface:
    """
    Interactive terminal interface for the Orchestrator Agent.
    Allows users to send commands, create tasks, and monitor system status.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize the terminal interface.
        
        Args:
            orchestrator: The main orchestrator instance
        """
        self.orchestrator = orchestrator
        self.logger = get_logger(__name__)
        self._is_running = False
        self._command_history: List[str] = []
        
        # Available commands
        self.commands = {
            'help': self._cmd_help,
            'status': self._cmd_status,
            'agents': self._cmd_agents,
            'tasks': self._cmd_tasks,
            'create': self._cmd_create_task,
            'execute': self._cmd_execute_task,
            'cancel': self._cmd_cancel_task,
            'orchestrate': self._cmd_orchestrate,
            'history': self._cmd_history,
            'metrics': self._cmd_metrics,
            'capabilities': self._cmd_capabilities,
            'clear': self._cmd_clear,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit,
        }
        
        self.logger.info("Terminal interface initialized")
    
    async def start(self) -> None:
        """Start the terminal interface."""
        self._is_running = True
        self.logger.info("Starting terminal interface")
        
        # Print welcome message
        self._print_welcome()
        
        # Start input loop
        await self._input_loop()
    
    async def stop(self) -> None:
        """Stop the terminal interface."""
        self._is_running = False
        self.logger.info("Terminal interface stopped")
    
    def _print_welcome(self) -> None:
        """Print welcome message and help."""
        print("\\n" + "="*80)
        print("🤖 ORCHESTRATOR AGENT - TERMINAL INTERFACE")
        print("="*80)
        print("Welcome to the interactive terminal interface!")
        print("Type 'help' to see available commands or 'exit' to quit.")
        print("="*80 + "\\n")
    
    async def _input_loop(self) -> None:
        """Main input loop for processing user commands."""
        while self._is_running:
            try:
                # Get user input
                prompt = "orchestrator> "
                user_input = await self._get_input(prompt)
                
                if not user_input.strip():
                    continue
                
                # Add to command history
                self._command_history.append(user_input)
                
                # Parse and execute command
                await self._process_command(user_input)
                
            except KeyboardInterrupt:
                print("\\n🛑 Use 'exit' command to quit gracefully.")
                continue
            except EOFError:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error processing command: {format_error_message(e)}")
                self.logger.error(f"Terminal interface error: {e}")
    
    async def _get_input(self, prompt: str) -> str:
        """Get user input asynchronously."""
        # Use asyncio to get input without blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)
    
    async def _process_command(self, user_input: str) -> None:
        """Process a user command."""
        parts = user_input.strip().split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                await self.commands[command](args)
            except Exception as e:
                print(f"❌ Error executing command '{command}': {format_error_message(e)}")
        else:
            print(f"❌ Unknown command: '{command}'. Type 'help' for available commands.")
    
    async def _cmd_help(self, args: List[str]) -> None:
        """Show help information."""
        print("\\n📚 AVAILABLE COMMANDS:")
        print("-" * 50)
        
        command_info = {
            'help': 'Show this help message',
            'status': 'Show system status',
            'agents': 'List all agents and their status',
            'tasks': 'List all tasks and their status',
            'create <description>': 'Create a new task from description',
            'execute <task_id>': 'Execute a specific task',
            'cancel <task_id>': 'Cancel a running task',
            'orchestrate <description>': 'Create and orchestrate multiple tasks',
            'history': 'Show command history',
            'metrics': 'Show system metrics',
            'capabilities': 'Show available agent capabilities',
            'clear': 'Clear the terminal screen',
            'exit/quit': 'Exit the terminal interface'
        }
        
        for cmd, desc in command_info.items():
            print(f"  {cmd:<25} - {desc}")
        
        print("\\n💡 Examples:")
        print("  create Move robot forward 1 meter")
        print("  orchestrate Scan room and create map")
        print("  status")
        print("  agents")
        print("-" * 50 + "\\n")
    
    async def _cmd_status(self, args: List[str]) -> None:
        """Show system status."""
        try:
            status = await self.orchestrator.get_system_status()
            
            print("\\n📊 SYSTEM STATUS:")
            print("-" * 40)
            print(f"🤖 Total Agents:     {status.total_agents}")
            print(f"🟢 Online Agents:    {status.online_agents}")
            print(f"⏳ Pending Tasks:    {status.pending_tasks}")
            print(f"🔄 Active Tasks:     {status.active_tasks}")
            print(f"✅ Completed Tasks:  {status.completed_tasks}")
            print(f"❌ Failed Tasks:     {status.failed_tasks}")
            print(f"⏰ System Uptime:    {status.system_uptime:.1f} seconds")
            print("-" * 40 + "\\n")
            
        except Exception as e:
            print(f"❌ Error getting system status: {format_error_message(e)}")
    
    async def _cmd_agents(self, args: List[str]) -> None:
        """List all agents and their status."""
        try:
            if not self.orchestrator.agent_manager:
                print("❌ Agent manager not available")
                return
            
            agents = self.orchestrator.agent_manager.get_all_agents()
            
            if not agents:
                print("📭 No agents registered")
                return
            
            print("\\n🤖 REGISTERED AGENTS:")
            print("-" * 80)
            print(f"{'Name':<20} {'ID':<15} {'Status':<10} {'Capabilities':<30}")
            print("-" * 80)
            
            for agent in agents:
                capabilities = ', '.join([cap.name for cap in agent.capabilities[:3]])
                if len(agent.capabilities) > 3:
                    capabilities += f" (+{len(agent.capabilities) - 3} more)"
                
                print(f"{agent.name:<20} {agent.agent_id:<15} {agent.status.value:<10} {capabilities:<30}")
            
            print("-" * 80 + "\\n")
            
        except Exception as e:
            print(f"❌ Error listing agents: {format_error_message(e)}")
    
    async def _cmd_tasks(self, args: List[str]) -> None:
        """List all tasks and their status."""
        try:
            if not self.orchestrator.task_manager:
                print("❌ Task manager not available")
                return
            
            # Get tasks by status using the available method
            from ..core.models import TaskStatus
            
            pending_tasks = self.orchestrator.task_manager.get_tasks_by_status(TaskStatus.PENDING)
            running_tasks = self.orchestrator.task_manager.get_tasks_by_status(TaskStatus.RUNNING)
            completed_tasks = self.orchestrator.task_manager.get_tasks_by_status(TaskStatus.COMPLETED)
            failed_tasks = self.orchestrator.task_manager.get_tasks_by_status(TaskStatus.FAILED)
            cancelled_tasks = self.orchestrator.task_manager.get_tasks_by_status(TaskStatus.CANCELLED)
            
            print("\\n📋 TASKS OVERVIEW:")
            print("-" * 80)
            
            def print_task_list(task_list, status_name, emoji):
                if task_list:
                    print(f"\\n{emoji} {status_name} Tasks ({len(task_list)}):")
                    for task in task_list[:5]:  # Show first 5
                        print(f"  • {task.task_id[:8]}... - {task.name[:50]}")
                    if len(task_list) > 5:
                        print(f"  ... and {len(task_list) - 5} more")
            
            print_task_list(pending_tasks, "PENDING", "⏳")
            print_task_list(running_tasks, "RUNNING", "🔄")
            print_task_list(completed_tasks, "COMPLETED", "✅")
            print_task_list(failed_tasks, "FAILED", "❌")
            print_task_list(cancelled_tasks, "CANCELLED", "🚫")
            
            if not any([pending_tasks, running_tasks, completed_tasks, failed_tasks, cancelled_tasks]):
                print("📭 No tasks found")
            
            print("-" * 80 + "\\n")
            
        except Exception as e:
            print(f"❌ Error listing tasks: {format_error_message(e)}")
    
    async def _cmd_create_task(self, args: List[str]) -> None:
        """Create a new task from description."""
        if not args:
            print("❌ Please provide a task description. Example: create Move robot forward")
            return
        
        try:
            description = ' '.join(args)
            print(f"🔄 Creating task: {description}")
            
            task_id = await self.orchestrator.create_task_from_user_input(description)
            
            if task_id:
                print(f"✅ Task created successfully!")
                print(f"📝 Task ID: {task_id}")
                print(f"📋 Description: {description}")
                print("🔄 Task will be automatically assigned to an appropriate agent.")
            else:
                print("❌ Failed to create task. Check logs for details.")
            
        except Exception as e:
            print(f"❌ Error creating task: {format_error_message(e)}")
    
    async def _cmd_execute_task(self, args: List[str]) -> None:
        """Execute a specific task."""
        if not args:
            print("❌ Please provide a task ID. Example: execute task_123")
            return
        
        try:
            task_id = args[0]
            
            if not self.orchestrator.task_manager:
                print("❌ Task manager not available")
                return
            
            task = self.orchestrator.task_manager.get_task(task_id)
            if not task:
                print(f"❌ Task {task_id} not found")
                return
            
            print(f"🔄 Executing task: {task_id}")
            print(f"📋 Description: {task.name}")
            
            # Force execution by finding best agent and assigning
            if self.orchestrator.agent_manager:
                best_agent = self.orchestrator.agent_manager.find_best_agent_for_capability(
                    task.capability_required
                )
                
                if best_agent:
                    success = await self.orchestrator._assign_task_to_agent(task_id, best_agent.agent_id)
                    if success:
                        print(f"✅ Task assigned to agent: {best_agent.name}")
                    else:
                        print("❌ Failed to assign task to agent")
                else:
                    print(f"❌ No suitable agent found for capability: {task.capability_required}")
            
        except Exception as e:
            print(f"❌ Error executing task: {format_error_message(e)}")
    
    async def _cmd_cancel_task(self, args: List[str]) -> None:
        """Cancel a running task."""
        if not args:
            print("❌ Please provide a task ID. Example: cancel task_123")
            return
        
        try:
            task_id = args[0]
            
            if not self.orchestrator.task_manager:
                print("❌ Task manager not available")
                return
            
            success = await self.orchestrator.task_manager.cancel_task(task_id)
            
            if success:
                print(f"✅ Task {task_id} cancelled successfully")
            else:
                print(f"❌ Failed to cancel task {task_id}")
            
        except Exception as e:
            print(f"❌ Error cancelling task: {format_error_message(e)}")
    
    async def _cmd_orchestrate(self, args: List[str]) -> None:
        """Create and orchestrate multiple tasks."""
        if not args:
            print("❌ Please provide a description. Example: orchestrate Scan room and create map")
            return
        
        try:
            description = ' '.join(args)
            print(f"🔄 Creating orchestration plan for: {description}")
            
            # For now, create a single complex task - could be enhanced to break down into subtasks
            task_id = await self.orchestrator.create_task_from_user_input(
                f"Orchestrated task: {description}",
                priority=8  # Higher priority for orchestrated tasks
            )
            
            if task_id:
                print(f"✅ Orchestration task created!")
                print(f"📝 Task ID: {task_id}")
                print(f"🎯 This will be handled by the Semantic Kernel planner for optimal execution.")
                
                # If planner supports concurrent orchestration, use it
                if (self.orchestrator.planner and 
                    hasattr(self.orchestrator.planner, 'create_concurrent_orchestration_plan')):
                    print("🧠 Advanced concurrent orchestration capabilities available.")
            else:
                print("❌ Failed to create orchestration task.")
            
        except Exception as e:
            print(f"❌ Error creating orchestration: {format_error_message(e)}")
    
    async def _cmd_history(self, args: List[str]) -> None:
        """Show command history."""
        if not self._command_history:
            print("📭 No command history available")
            return
        
        print("\\n📜 COMMAND HISTORY:")
        print("-" * 50)
        
        # Show last 10 commands
        recent_commands = self._command_history[-10:]
        for i, cmd in enumerate(recent_commands, 1):
            print(f"{i:2d}. {cmd}")
        
        if len(self._command_history) > 10:
            print(f"... and {len(self._command_history) - 10} more commands")
        
        print("-" * 50 + "\\n")
    
    async def _cmd_metrics(self, args: List[str]) -> None:
        """Show system metrics."""
        try:
            print("\\n📈 SYSTEM METRICS:")
            print("-" * 50)
            
            # WebSocket metrics
            if self.orchestrator.websocket_server:
                ws_stats = self.orchestrator.websocket_server.get_server_stats()
                print(f"🔌 WebSocket Connections: {ws_stats.get('active_connections', 0)}")
                print(f"📡 Messages Processed:    {ws_stats.get('messages_processed', 0)}")
            
            # Task metrics
            if self.orchestrator.task_manager:
                task_stats = self.orchestrator.task_manager.get_statistics()
                print(f"📋 Total Tasks Created:   {task_stats.get('total_tasks', 0)}")
                print(f"✅ Tasks Completed:       {task_stats.get('completed_tasks', 0)}")
                print(f"❌ Tasks Failed:          {task_stats.get('failed_tasks', 0)}")
            
            # Agent metrics
            if self.orchestrator.agent_manager:
                agent_stats = self.orchestrator.agent_manager.get_system_statistics()
                print(f"🤖 Registered Agents:     {agent_stats.get('total_agents', 0)}")
                print(f"🟢 Online Agents:         {agent_stats.get('online_agents', 0)}")
                print(f"🎯 Total Capabilities:    {agent_stats.get('total_capabilities', 0)}")
            
            # System uptime
            if self.orchestrator._start_time:
                uptime = datetime.utcnow() - self.orchestrator._start_time
                print(f"⏰ System Uptime:         {uptime}")
            
            print("-" * 50 + "\\n")
            
        except Exception as e:
            print(f"❌ Error getting metrics: {format_error_message(e)}")
    
    async def _cmd_capabilities(self, args: List[str]) -> None:
        """Show available agent capabilities."""
        try:
            if not self.orchestrator.agent_manager:
                print("❌ Agent manager not available")
                return
            
            capabilities = self.orchestrator.agent_manager.get_all_capabilities()
            
            if not capabilities:
                print("📭 No capabilities available")
                return
            
            print("\\n🎯 AVAILABLE CAPABILITIES:")
            print("-" * 60)
            
            for capability in capabilities:
                agents_with_cap = self.orchestrator.agent_manager.get_agents_by_capability(capability)
                agent_count = len(agents_with_cap)
                online_agents = len([a for a in agents_with_cap if a.status.value == 'online'])
                
                print(f"  • {capability:<30} ({online_agents}/{agent_count} agents online)")
            
            print("-" * 60 + "\\n")
            
        except Exception as e:
            print(f"❌ Error getting capabilities: {format_error_message(e)}")
    
    async def _cmd_clear(self, args: List[str]) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        self._print_welcome()
    
    async def _cmd_exit(self, args: List[str]) -> None:
        """Exit the terminal interface."""
        print("\\n👋 Exiting terminal interface...")
        self._is_running = False
