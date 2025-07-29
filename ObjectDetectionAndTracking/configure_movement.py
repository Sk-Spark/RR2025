#!/usr/bin/env python3
"""
Movement Configuration Utility for Ball Tracking Robot
Allows easy configuration of movement types and parameters
"""

import sys
import os

def print_header():
    """Print configuration utility header"""
    print("=" * 60)
    print("🏓 Ball Tracking Robot - Movement Configuration Utility")
    print("=" * 60)
    print()

def print_current_config():
    """Print current movement configuration"""
    try:
        import config
        print("📋 Current Movement Configuration:")
        print("-" * 40)
        print(f"Movement Type: {getattr(config, 'MOVEMENT_TYPE', 'mecanum')}")
        print(f"Motor Following: {'Enabled' if getattr(config, 'ENABLE_MOTOR_FOLLOWING', True) else 'Disabled'}")
        print(f"Strafing: {'Enabled' if getattr(config, 'ENABLE_STRAFING', True) else 'Disabled'}")
        print(f"Forward/Backward: {'Enabled' if getattr(config, 'ENABLE_FORWARD_BACKWARD', True) else 'Disabled'}")
        print(f"Rotation Tracking: {'Enabled' if getattr(config, 'ENABLE_ROTATION_TRACKING', True) else 'Disabled'}")
        print(f"Follow Speed: {getattr(config, 'MOTOR_FOLLOW_SPEED', 40)}")
        print(f"Max Speed: {getattr(config, 'MOTOR_MAX_SPEED', 60)}")
        print()
        print("Movement Gains:")
        print(f"  - Strafe Gain: {getattr(config, 'STRAFE_GAIN', 0.8)}")
        print(f"  - Forward Gain: {getattr(config, 'FORWARD_GAIN', 0.6)}")
        print(f"  - Rotation Gain: {getattr(config, 'ROTATION_GAIN', 0.8)}")
        print()
    except ImportError:
        print("❌ Error: Could not import config module")

def show_movement_types():
    """Show available movement types and their descriptions"""
    print("🚗 Available Movement Types:")
    print("-" * 40)
    movement_types = {
        "mecanum": "Full mecanum wheel movement (strafe + forward/back + rotation)",
        "tank": "Tank-style movement (forward/back + rotation only, no strafing)",
        "simple": "Simple directional movement (forward/back/left/right only)",
        "strafe_only": "Only left/right strafing movement (for fixed position tracking)",
        "turn_only": "Only rotation movement (for stationary ball tracking)"
    }
    
    for i, (movement_type, description) in enumerate(movement_types.items(), 1):
        print(f"{i}. {movement_type.upper()}: {description}")
    print()

def update_config_file(parameter, value):
    """Update a parameter in the config file"""
    config_file = "config.py"
    
    if not os.path.exists(config_file):
        print(f"❌ Error: {config_file} not found!")
        return False
    
    try:
        # Read the config file
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        # Find and update the parameter
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{parameter} ="):
                if isinstance(value, str):
                    lines[i] = f'{parameter} = "{value}"\n'
                else:
                    lines[i] = f'{parameter} = {value}\n'
                updated = True
                break
        
        if not updated:
            print(f"❌ Parameter {parameter} not found in config file")
            return False
        
        # Write back to file
        with open(config_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated {parameter} = {value}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        return False

def configure_movement_type():
    """Configure movement type"""
    show_movement_types()
    
    while True:
        try:
            choice = input("Select movement type (1-5) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return
            
            choice_num = int(choice)
            movement_types = ["mecanum", "tank", "simple", "strafe_only", "turn_only"]
            
            if 1 <= choice_num <= 5:
                selected_type = movement_types[choice_num - 1]
                if update_config_file("MOVEMENT_TYPE", selected_type):
                    print(f"🎯 Movement type set to: {selected_type.upper()}")
                return
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except ValueError:
            print("❌ Invalid input. Please enter a number 1-5 or 'q'.")

def configure_capabilities():
    """Configure movement capabilities"""
    print("🔧 Movement Capabilities Configuration:")
    print("-" * 40)
    
    capabilities = [
        ("ENABLE_STRAFING", "Enable left/right strafing movement"),
        ("ENABLE_FORWARD_BACKWARD", "Enable forward/backward movement"),
        ("ENABLE_ROTATION_TRACKING", "Enable rotation for ball centering")
    ]
    
    for param, description in capabilities:
        while True:
            response = input(f"{description} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                update_config_file(param, True)
                break
            elif response in ['n', 'no']:
                update_config_file(param, False)
                break
            else:
                print("❌ Please enter 'y' or 'n'")

def configure_gains():
    """Configure movement gains"""
    print("⚙️  Movement Gains Configuration:")
    print("-" * 40)
    print("(Gains control movement sensitivity: 0.1 = gentle, 2.0 = aggressive)")
    
    gains = [
        ("STRAFE_GAIN", "Strafing movement gain", 0.8),
        ("FORWARD_GAIN", "Forward/backward movement gain", 0.6), 
        ("ROTATION_GAIN", "Rotation movement gain", 0.8)
    ]
    
    for param, description, default in gains:
        while True:
            try:
                response = input(f"{description} [{default}]: ").strip()
                if not response:
                    value = default
                else:
                    value = float(response)
                    if not (0.1 <= value <= 2.0):
                        print("❌ Gain must be between 0.1 and 2.0")
                        continue
                
                update_config_file(param, value)
                break
                
            except ValueError:
                print("❌ Please enter a valid number")

def configure_speeds():
    """Configure movement speeds"""
    print("🏃 Speed Configuration:")
    print("-" * 40)
    
    speeds = [
        ("MOTOR_FOLLOW_SPEED", "Default following speed (0-100)", 40),
        ("MOTOR_MAX_SPEED", "Maximum motor speed (0-100)", 60)
    ]
    
    for param, description, default in speeds:
        while True:
            try:
                response = input(f"{description} [{default}]: ").strip()
                if not response:
                    value = default
                else:
                    value = int(response)
                    if not (0 <= value <= 100):
                        print("❌ Speed must be between 0 and 100")
                        continue
                
                update_config_file(param, value)
                break
                
            except ValueError:
                print("❌ Please enter a valid number")

def main_menu():
    """Display main configuration menu"""
    while True:
        print("\n🎮 Configuration Menu:")
        print("-" * 30)
        print("1. View current configuration")
        print("2. Change movement type")
        print("3. Configure movement capabilities")
        print("4. Configure movement gains")
        print("5. Configure movement speeds")
        print("6. Show movement type descriptions")
        print("q. Quit")
        print()
        
        choice = input("Select option: ").strip().lower()
        
        if choice == '1':
            print_current_config()
        elif choice == '2':
            configure_movement_type()
        elif choice == '3':
            configure_capabilities()
        elif choice == '4':
            configure_gains()
        elif choice == '5':
            configure_speeds()
        elif choice == '6':
            show_movement_types()
        elif choice == 'q':
            print("\n👋 Configuration complete!")
            print("🔄 Restart the ball tracking system to apply changes.")
            break
        else:
            print("❌ Invalid option. Please try again.")

def main():
    """Main function"""
    print_header()
    print_current_config()
    main_menu()

if __name__ == "__main__":
    main()
