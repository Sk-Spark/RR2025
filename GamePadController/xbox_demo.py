#!/usr/bin/env python3
"""
Xbox 360 Controller Reader for Raspberry Pi 5
This script demonstrates the basic controller reading functionality
For robot control, use robot_control.py instead
"""

import time
import threading
from universal_gamepad_controller import UniversalGamepadController


def setup_demo_callbacks(controller):
    """Setup demonstration callbacks for the controller"""
    
    # Button callbacks
    def on_button_press(button_name):
        def callback():
            print(f"🎮 {button_name.upper()} pressed")
        return callback
    
    def on_button_release(button_name):
        def callback():
            print(f"🎮 {button_name.upper()} released")
        return callback
    
    # Register button callbacks for Xbox 360 controller
    # Xbox 360 mapping: A, B, X, Y, LB, RB, Back, Start, LS, RS + D-pad
    buttons = ['a', 'b', 'x', 'y', 'lb', 'rb', 'back', 'start', 'ls', 'rs',
               'dpad_up', 'dpad_down', 'dpad_left', 'dpad_right']
    
    for button in buttons:
        controller.register_button_callback(button, on_button_press(button), 'press')
        controller.register_button_callback(button, on_button_release(button), 'release')
    
    # Analog callbacks
    def on_left_stick(values):
        x, y = values
        if abs(x) > 0.1 or abs(y) > 0.1:
            print(f"🕹️  Left stick: X={x:.2f}, Y={y:.2f}")
    
    def on_right_stick(values):
        x, y = values
        if abs(x) > 0.1 or abs(y) > 0.1:
            print(f"🕹️  Right stick: X={x:.2f}, Y={y:.2f}")
    
    def on_left_trigger(value):
        if value > 0.1:
            print(f"🎯 Left trigger: {value:.2f}")
    
    def on_right_trigger(value):
        if value > 0.1:
            print(f"🎯 Right trigger: {value:.2f}")
    
    controller.register_analog_callback('left_stick', on_left_stick)
    controller.register_analog_callback('right_stick', on_right_stick)
    controller.register_analog_callback('left_trigger', on_left_trigger)
    controller.register_analog_callback('right_trigger', on_right_trigger)


def print_controller_status(controller):
    """Print current controller status"""
    left_stick = controller.get_analog_value('left_stick')
    right_stick = controller.get_analog_value('right_stick')
    left_trigger = controller.get_analog_value('left_trigger')
    right_trigger = controller.get_analog_value('right_trigger')
    
    print("\\n" + "="*50)
    print("CONTROLLER STATUS:")
    print("="*50)
    print(f"Left Stick  - X: {left_stick[0]:6.2f}, Y: {left_stick[1]:6.2f}")
    print(f"Right Stick - X: {right_stick[0]:6.2f}, Y: {right_stick[1]:6.2f}")
    print(f"Left Trigger: {left_trigger:6.2f} | Right Trigger: {right_trigger:6.2f}")
    
    # Show pressed buttons
    pressed_buttons = []
    buttons_to_check = ['a', 'b', 'x', 'y', 'lb', 'rb', 'back', 'start', 'ls', 'rs',
                       'dpad_up', 'dpad_down', 'dpad_left', 'dpad_right']
    
    for button in buttons_to_check:
        if controller.get_button_state(button):
            pressed_buttons.append(button)
    
    if pressed_buttons:
        print(f"Pressed: {', '.join(pressed_buttons)}")
    
    print("="*50 + "\\n")


def main():
    """Main function to demonstrate basic controller reading"""
    try:
        print("🎮 Xbox 360 Controller Reader (Demo Mode)")
        print("="*50)
        print("Connecting to controller...")
        
        # Initialize controller
        controller = UniversalGamepadController()
        
        if not controller.connect():
            print("❌ Failed to connect to controller!")
            return
        
        print("✅ Controller connected successfully!")
        print(f"\\nDetected: {controller.controller_type} controller")
        print("\\nThis is demo mode - showing raw controller inputs")
        print("For robot control, run: python3 robot_control.py")
        print("Press Ctrl+C to exit\\n")
        
        # Setup callbacks for demonstration
        setup_demo_callbacks(controller)
        
        # Status tracking
        should_exit = False
        
        # Start a background thread to print status periodically
        def status_printer():
            while not should_exit:
                time.sleep(5)  # Print status every 5 seconds
                if not should_exit:
                    print_controller_status(controller)
        
        status_thread = threading.Thread(target=status_printer, daemon=True)
        status_thread.start()
        
        # Exit callback
        def on_exit():
            nonlocal should_exit
            should_exit = True
            print("\\n🛑 Exit requested")
        
        controller.register_exit_callback(on_exit)
        
        # Start listening for controller input
        controller.listen()
        
    except FileNotFoundError:
        print("❌ Error: Controller not found at /dev/input/js0")
        print("Please check:")
        print("1. Controller is connected via USB")
        print("2. Controller is detected by the system") 
        print("3. Run 'ls -la /dev/input/js*' to see available controllers")
        
    except PermissionError:
        print("❌ Error: Permission denied accessing controller")
        print("Try running with sudo or add your user to the 'input' group:")
        print("sudo usermod -a -G input $USER")
        print("Then log out and log back in")
        
    except KeyboardInterrupt:
        print("\\n🛑 Interrupted by user")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Make sure pygame is installed correctly")
        
    finally:
        print("👋 Controller reader stopped")


if __name__ == "__main__":
    main()
