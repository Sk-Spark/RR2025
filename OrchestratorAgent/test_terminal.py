#!/usr/bin/env /home/spark/.venv/bin/python
"""
Simple test script for terminal interface functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add paths
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
config_path = Path(__file__).parent / "config"
sys.path.insert(0, str(config_path))

print("🧪 Testing Terminal Interface Components...")

try:
    print("1. Testing imports...")
    from config import ConfigManager
    print("   ✅ ConfigManager imported")
    
    from src.orchestrator import Orchestrator
    print("   ✅ Orchestrator imported")
    
    from src.interfaces.terminal_interface import TerminalInterface
    print("   ✅ TerminalInterface imported")
    
    print("\\n2. Testing initialization...")
    config_manager = ConfigManager()
    print("   ✅ ConfigManager initialized")
    
    orchestrator = Orchestrator(config_manager)
    print("   ✅ Orchestrator initialized")
    
    terminal = TerminalInterface(orchestrator)
    print("   ✅ TerminalInterface initialized")
    
    print("\\n3. Testing command help...")
    print("   Available commands:", list(terminal.commands.keys()))
    
    print("\\n✅ All tests passed! Terminal interface is ready to use.")
    print("\\n🚀 To run interactively, use:")
    print("   python main.py --interactive")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\\n🏁 Test complete.")
