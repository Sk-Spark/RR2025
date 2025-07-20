#!/usr/bin/env python3
"""
Simple Xbox 360 Controller Test
"""
from universal_gamepad_controller import UniversalGamepadController
import time

def main():
    print("=== Xbox 360 Controller Test ===")
    
    controller = UniversalGamepadController()
    
    if not controller.connect():
        print("Failed to connect to controller!")
        return
    
    # Register button callbacks
    def on_button_event(button_name, event_type):
        print(f"🎮 {button_name.upper()} {event_type}!")
    
    # Face buttons (Xbox: A, B, X, Y)
    for button in ['a', 'b', 'x', 'y']:
        controller.register_button_callback(button, lambda btn=button: on_button_event(btn, "PRESSED"), 'press')
        controller.register_button_callback(button, lambda btn=button: on_button_event(btn, "RELEASED"), 'release')
    
    # Shoulder buttons (Xbox: LB, RB)
    for button in ['lb', 'rb']:
        controller.register_button_callback(button, lambda btn=button: on_button_event(btn, "PRESSED"), 'press')
        controller.register_button_callback(button, lambda btn=button: on_button_event(btn, "RELEASED"), 'release')
    
    # D-pad
    def register_dpad_callbacks():
        def on_dpad_up_press():
            on_button_event("dpad_up", "PRESSED")
        def on_dpad_up_release():
            on_button_event("dpad_up", "RELEASED")
        def on_dpad_down_press():
            on_button_event("dpad_down", "PRESSED")
        def on_dpad_down_release():
            on_button_event("dpad_down", "RELEASED")
        def on_dpad_left_press():
            on_button_event("dpad_left", "PRESSED")
        def on_dpad_left_release():
            on_button_event("dpad_left", "RELEASED")
        def on_dpad_right_press():
            on_button_event("dpad_right", "PRESSED")
        def on_dpad_right_release():
            on_button_event("dpad_right", "RELEASED")
        
        controller.register_button_callback('dpad_up', on_dpad_up_press, 'press')
        controller.register_button_callback('dpad_up', on_dpad_up_release, 'release')
        controller.register_button_callback('dpad_down', on_dpad_down_press, 'press')
        controller.register_button_callback('dpad_down', on_dpad_down_release, 'release')
        controller.register_button_callback('dpad_left', on_dpad_left_press, 'press')
        controller.register_button_callback('dpad_left', on_dpad_left_release, 'release')
        controller.register_button_callback('dpad_right', on_dpad_right_press, 'press')
        controller.register_button_callback('dpad_right', on_dpad_right_release, 'release')
    
    register_dpad_callbacks()
    
    # Analog callbacks
    def on_stick_change(stick_name, value):
        x, y = value
        if abs(x) > 0.1 or abs(y) > 0.1:  # Only show significant movement
            print(f"🕹️  {stick_name}: ({x:.2f}, {y:.2f})")
    
    def on_trigger_change(trigger_name, value):
        if value > 0.1:  # Only show when pressed
            print(f"🔫 {trigger_name}: {value:.2f}")
    
    controller.register_analog_callback('left_stick', lambda val: on_stick_change('Left Stick', val))
    controller.register_analog_callback('right_stick', lambda val: on_stick_change('Right Stick', val))
    controller.register_analog_callback('left_trigger', lambda val: on_trigger_change('Left Trigger', val))
    controller.register_analog_callback('right_trigger', lambda val: on_trigger_change('Right Trigger', val))
    
    print(f"\\n🎮 Controller connected: {controller.controller_type}")
    print("\\n=== Button Mapping ===")
    print("Face buttons: A, B, X, Y")
    print("Shoulder buttons: LB, RB") 
    print("D-pad: UP, DOWN, LEFT, RIGHT")
    print("Analog: Left/Right sticks, Left/Right triggers")
    print("\\nPress buttons to test detection...")
    print("Press Ctrl+C to exit\\n")
    
    try:
        controller.listen()
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
        controller.stop()

if __name__ == "__main__":
    main()
