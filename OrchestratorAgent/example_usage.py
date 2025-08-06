#!/usr/bin/env /home/spark/.venv/bin/python
"""
Usage example script for the Orchestrator Agent Terminal Interface.
This script demonstrates various terminal interface features.
"""

import asyncio
import sys
from pathlib import Path

# Add paths
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
config_path = Path(__file__).parent / "config"
sys.path.insert(0, str(config_path))

from src.orchestrator import Orchestrator
from config import ConfigManager


async def main():
    print("\\n" + "="*80)
    print("🤖 ORCHESTRATOR AGENT - TERMINAL INTERFACE USAGE EXAMPLE")
    print("="*80)
    print("This example shows how to use the terminal interface programmatically.")
    print("For interactive use, run: python main.py --interactive")
    print("="*80)
    
    try:
        # Initialize orchestrator
        config_manager = ConfigManager()
        orchestrator = Orchestrator(config_manager)
        
        print("\\n📋 AVAILABLE COMMANDS:")
        print("-" * 50)
        
        # Get terminal interface
        terminal = orchestrator.terminal_interface
        
        command_descriptions = {
            'help': 'Show all available commands and usage examples',
            'status': 'Display system status (agents, tasks, uptime)',
            'agents': 'List all registered agents and capabilities',
            'tasks': 'Show all tasks by status (pending, running, completed)',
            'create <description>': 'Create task from natural language',
            'execute <task_id>': 'Force execution of specific task',
            'cancel <task_id>': 'Cancel a running task',
            'orchestrate <description>': 'Create complex multi-agent plan',
            'metrics': 'Show detailed system metrics',
            'capabilities': 'List all available agent capabilities',
            'history': 'Show command history',
            'clear': 'Clear terminal screen',
            'exit/quit': 'Exit terminal interface'
        }
        
        for cmd, desc in command_descriptions.items():
            print(f"  {cmd:<30} - {desc}")
        
        print("\\n" + "-" * 50)
        print("\\n💡 EXAMPLE USAGE SCENARIOS:")
        print("-" * 50)
        
        scenarios = [
            ("System Monitoring", [
                "status                    # Check system health",
                "agents                    # List connected agents", 
                "tasks                     # View all tasks",
                "metrics                   # Detailed statistics"
            ]),
            ("Task Management", [
                "create Move robot forward 2 meters",
                "create Take photo of room",
                "create Read all sensors",
                "tasks                     # Check task status"
            ]),
            ("Advanced Orchestration", [
                "orchestrate Scan entire house and create map",
                "orchestrate Patrol perimeter and report",
                "orchestrate Gather sensor data from all rooms"
            ]),
            ("Development & Debug", [
                "capabilities              # See what agents can do",
                "history                   # Review commands", 
                "help                      # Get detailed help"
            ])
        ]
        
        for scenario_name, commands in scenarios:
            print(f"\\n🎯 {scenario_name}:")
            for cmd in commands:
                print(f"    orchestrator> {cmd}")
        
        print("\\n" + "-" * 50)
        print("\\n🚀 TO START INTERACTIVE MODE:")
        print("-" * 50)
        print("1. Open terminal")
        print("2. Navigate to project directory:")
        print("   cd /home/spark/RR2025/OrchestratorAgent")
        print("3. Activate virtual environment:")
        print("   source /home/spark/.venv/bin/activate")
        print("4. Start interactive mode:")
        print("   python main.py --interactive")
        print("5. Use commands like: help, status, create <task>")
        
        print("\\n🔧 TECHNICAL FEATURES:")
        print("-" * 50)
        print("• AI-powered task analysis via Semantic Kernel")
        print("• Real-time agent and task monitoring")
        print("• Concurrent orchestration with dependency management")  
        print("• Natural language task creation")
        print("• Intelligent agent selection and routing")
        print("• Complete system integration (WebSocket, Ollama, etc.)")
        
        print("\\n📖 For detailed documentation, see:")
        print("   TERMINAL_INTERFACE.md")
        
        print("\\n✅ Ready to use! Start with: python main.py --interactive")
        print("="*80 + "\\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
