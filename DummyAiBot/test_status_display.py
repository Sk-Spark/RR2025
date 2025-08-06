#!/usr/bin/env python3
"""Test status display to debug capabilities issue"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config

def test_capabilities_display():
    """Test how capabilities are displayed in status"""
    print("Testing capabilities display...")
    
    # Create config and test capabilities
    config = Config()
    print(f"Config capabilities type: {type(config.capabilities)}")
    print(f"Config capabilities length: {len(config.capabilities) if config.capabilities else 'None'}")
    print(f"Config capabilities: {config.capabilities}")
    
    # Simulate status display like in the bot
    status = {
        'bot_id': 'test-bot',
        'status': 'ready',
        'current_task': None,
        'active_tasks': 0,
        'completed_tasks': 0,
        'capabilities': config.capabilities,
        'movement_status': {
            'status': 'ready',
            'current_position': {'x': 0, 'y': 0, 'z': 0}
        },
        'camera_status': {
            'status': 'ready',
            'pan_angle': 0,
            'tilt_angle': 0
        }
    }
    
    print("\n" + "="*50)
    print("BOT STATUS:")
    print("-" * 40)
    print(f"Bot ID: {status['bot_id']}")
    print(f"Status: {status['status']}")
    print(f"Current Task: {status['current_task'] or 'None'}")
    print(f"Active Tasks: {status['active_tasks']}")
    print(f"Completed Tasks: {status['completed_tasks']}")
    print(f"Capabilities: {', '.join(status['capabilities']) if status['capabilities'] else 'None'}")
    print(f"\nMovement Status: {status['movement_status']['status']}")
    print(f"Position: {status['movement_status']['current_position']}")
    print(f"\nCamera Status: {status['camera_status']['status']}")
    print(f"Pan: {status['camera_status']['pan_angle']}°, Tilt: {status['camera_status']['tilt_angle']}°")
    print("-" * 40)
    print("="*50)

if __name__ == "__main__":
    test_capabilities_display()
