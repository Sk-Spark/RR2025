#!/usr/bin/env python3
"""
Xbox 360 Controller Test with Integrated Universal Gamepad Controller
"""
import pygame
import time
import threading
from typing import Dict, Callable, Optional, Tuple

class XboxGamepadController:
    """Universal gamepad controller using pygame for cross-platform support"""
    
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        self.joystick = None
        self.running = False
        self.thread = None
        
        # Button state tracking
        self.button_states = {}
        self.analog_values = {
            'left_stick': (0.0, 0.0),
            'right_stick': (0.0, 0.0),
            'left_trigger': 0.0,
            'right_trigger': 0.0
        }
        
        # D-pad state tracking
        self.current_hat_state = (0, 0)  # Track current hat position
        
        # Callbacks
        self.callbacks = {
            'on_press': {},
            'on_release': {},
            'on_analog_change': {},
            'on_exit': None
        }
        
        # Controller type detection
        self.controller_type = "unknown"
        self.button_map = {}
        self.axis_map = {}
        
    def _detect_controller_type(self, joystick_name: str):
        """Detect controller type and set up button mappings"""
        name_lower = joystick_name.lower()
        
        if "xbox" in name_lower or "360" in name_lower:
            self.controller_type = "xbox360"
            self._setup_xbox360_mapping()
        elif "dualshock" in name_lower or "ps4" in name_lower or "playstation" in name_lower:
            self.controller_type = "ps4"
            self._setup_ps4_mapping()
        else:
            self.controller_type = "generic"
            self._setup_generic_mapping()
            
        print(f"Detected controller: {self.controller_type} - {joystick_name}")
    
    def _setup_xbox360_mapping(self):
        """Xbox 360 controller button/axis mapping"""
        self.button_map = {
            0: 'a',         # A button (bottom)
            1: 'b',         # B button (right)
            2: 'x',         # X button (left)
            3: 'y',         # Y button (top)
            4: 'lb',        # Left bumper
            5: 'rb',        # Right bumper
            6: 'back',      # Back button
            7: 'start',     # Start button
            8: 'ls',        # Left stick button
            9: 'rs',        # Right stick button
        }
        
        self.axis_map = {
            0: 'left_stick_x',
            1: 'left_stick_y',
            2: 'left_trigger',   # -1 to 1
            3: 'right_stick_x',
            4: 'right_stick_y', 
            5: 'right_trigger',  # -1 to 1
        }
        
        # Hat (D-pad) mapping
        self.hat_map = {
            (0, 1): 'dpad_up',
            (0, -1): 'dpad_down',
            (-1, 0): 'dpad_left',
            (1, 0): 'dpad_right',
        }
    
    def _setup_ps4_mapping(self):
        """PS4 controller button/axis mapping"""
        self.button_map = {
            0: 'x',         # X button (bottom)
            1: 'circle',    # Circle button (right)
            2: 'square',    # Square button (left)
            3: 'triangle',  # Triangle button (top)
            4: 'l1',        # L1 bumper
            5: 'r1',        # R1 bumper
            6: 'l2',        # L2 trigger button
            7: 'r2',        # R2 trigger button
            8: 'share',     # Share button
            9: 'options',   # Options button
            10: 'l3',       # Left stick button
            11: 'r3',       # Right stick button
            12: 'ps',       # PS button
            13: 'touchpad', # Touchpad button
        }
        
        self.axis_map = {
            0: 'left_stick_x',
            1: 'left_stick_y',
            2: 'right_stick_x',
            3: 'left_trigger',   # 0 to 1
            4: 'right_trigger',  # 0 to 1
            5: 'right_stick_y',
        }
    
    def _setup_generic_mapping(self):
        """Generic controller mapping (fallback)"""
        # Use simple numeric mapping
        self.button_map = {i: f'button_{i}' for i in range(20)}
        self.axis_map = {i: f'axis_{i}' for i in range(10)}
    
    def connect(self, joystick_index: int = 0) -> bool:
        """Connect to the specified joystick"""
        if pygame.joystick.get_count() == 0:
            print("No joysticks found!")
            return False
        
        if joystick_index >= pygame.joystick.get_count():
            print(f"Joystick index {joystick_index} not available")
            return False
        
        self.joystick = pygame.joystick.Joystick(joystick_index)
        self.joystick.init()
        
        joystick_name = self.joystick.get_name()
        self._detect_controller_type(joystick_name)
        
        print(f"Connected to: {joystick_name}")
        print(f"Buttons: {self.joystick.get_numbuttons()}")
        print(f"Axes: {self.joystick.get_numaxes()}")
        print(f"Hats: {self.joystick.get_numhats()}")
        
        return True
    
    def register_button_callback(self, button: str, callback: Callable, event_type: str = "press"):
        """Register a callback for button events"""
        if event_type not in ["press", "release"]:
            raise ValueError("event_type must be 'press' or 'release'")
        
        callback_key = f"on_{event_type}"
        if callback_key not in self.callbacks:
            self.callbacks[callback_key] = {}
        
        self.callbacks[callback_key][button] = callback
    
    def register_analog_callback(self, analog_input: str, callback: Callable):
        """Register a callback for analog input changes"""
        self.callbacks['on_analog_change'][analog_input] = callback
    
    def _call_callback(self, callback_type: str, button: str, *args):
        """Call registered callback if it exists"""
        if (callback_type in self.callbacks and 
            button in self.callbacks[callback_type]):
            try:
                self.callbacks[callback_type][button](*args)
            except Exception as e:
                print(f"Error in callback for {button}: {e}")
    
    def _normalize_trigger_value(self, value: float) -> float:
        """Normalize trigger value based on controller type"""
        if self.controller_type == "xbox360":
            # Xbox triggers go from -1 to 1, normalize to 0 to 1
            return (value + 1.0) / 2.0
        else:
            # PS4 triggers are already 0 to 1
            return max(0.0, value)
    
    def _process_events(self):
        """Process pygame events and call callbacks"""
        while self.running:
            pygame.event.pump()  # Update joystick state
            
            if not self.joystick:
                break
            
            # Process button events
            for button_index in range(self.joystick.get_numbuttons()):
                current_state = self.joystick.get_button(button_index)
                button_name = self.button_map.get(button_index, f"button_{button_index}")
                
                # Check for state changes
                if button_name not in self.button_states:
                    self.button_states[button_name] = False
                
                if current_state != self.button_states[button_name]:
                    self.button_states[button_name] = current_state
                    
                    if current_state:  # Button pressed
                        self._call_callback('on_press', button_name)
                    else:  # Button released
                        self._call_callback('on_release', button_name)
            
            # Process D-pad (hat) events
            for hat_index in range(self.joystick.get_numhats()):
                hat_value = self.joystick.get_hat(hat_index)
                
                # Check if hat state changed
                if hat_value != self.current_hat_state:
                    # Release the previous D-pad button if any
                    if self.current_hat_state != (0, 0) and hasattr(self, 'hat_map'):
                        if self.current_hat_state in self.hat_map:
                            old_button = self.hat_map[self.current_hat_state]
                            if old_button in self.button_states and self.button_states[old_button]:
                                self.button_states[old_button] = False
                                self._call_callback('on_release', old_button)
                    
                    # Press the new D-pad button if any
                    if hat_value != (0, 0) and hasattr(self, 'hat_map'):
                        if hat_value in self.hat_map:
                            new_button = self.hat_map[hat_value]
                            self.button_states[new_button] = True
                            self._call_callback('on_press', new_button)
                    
                    # Update current hat state
                    self.current_hat_state = hat_value
            
            # Process analog stick and trigger events
            for axis_index in range(self.joystick.get_numaxes()):
                axis_value = self.joystick.get_axis(axis_index)
                axis_name = self.axis_map.get(axis_index, f"axis_{axis_index}")
                
                # Apply deadzone
                if abs(axis_value) < 0.1:
                    axis_value = 0.0
                
                # Handle different axis types
                if 'trigger' in axis_name:
                    normalized_value = self._normalize_trigger_value(axis_value)
                    old_value = self.analog_values.get(axis_name, 0.0)
                    
                    if abs(normalized_value - old_value) > 0.01:  # Small threshold to avoid noise
                        self.analog_values[axis_name] = normalized_value
                        self._call_callback('on_analog_change', axis_name, normalized_value)
                
                elif 'stick' in axis_name:
                    # Group stick axes together
                    if 'left_stick' in axis_name:
                        if axis_name == 'left_stick_x':
                            old_x, old_y = self.analog_values['left_stick']
                            new_value = (axis_value, old_y)
                        else:  # left_stick_y
                            old_x, old_y = self.analog_values['left_stick']
                            new_value = (old_x, axis_value)
                        
                        if new_value != self.analog_values['left_stick']:
                            self.analog_values['left_stick'] = new_value
                            self._call_callback('on_analog_change', 'left_stick', new_value)
                    
                    elif 'right_stick' in axis_name:
                        if axis_name == 'right_stick_x':
                            old_x, old_y = self.analog_values['right_stick']
                            new_value = (axis_value, old_y)
                        else:  # right_stick_y
                            old_x, old_y = self.analog_values['right_stick']
                            new_value = (old_x, axis_value)
                        
                        if new_value != self.analog_values['right_stick']:
                            self.analog_values['right_stick'] = new_value
                            self._call_callback('on_analog_change', 'right_stick', new_value)
            
            time.sleep(0.02)  # ~50 FPS
    
    def listen(self, timeout: Optional[float] = None):
        """Start listening for controller input"""
        if not self.joystick:
            raise Exception("No controller connected. Call connect() first.")
        
        self.running = True
        self.thread = threading.Thread(target=self._process_events)
        self.thread.daemon = True
        self.thread.start()
        
        print(f"Listening for {self.controller_type} controller input...")
        print("Press Ctrl+C to exit")
        
        try:
            if timeout:
                self.thread.join(timeout)
            else:
                while self.running:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\\nExiting...")
            self.stop()
            if self.callbacks['on_exit']:
                self.callbacks['on_exit']()
    
    def stop(self):
        """Stop listening for input"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

def main():
    print("=== Xbox 360 Controller Test ===")
    
    controller = XboxGamepadController()
    
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
    
    # D-pad buttons
    for button in ['dpad_up', 'dpad_down', 'dpad_left', 'dpad_right']:
        controller.register_button_callback(button, lambda btn=button: on_button_event(btn, "PRESSED"), 'press')
        controller.register_button_callback(button, lambda btn=button: on_button_event(btn, "RELEASED"), 'release')
    
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
