# Smooth Servo Movement Guide

## Overview
The Camera Pan-Tilt Controller now includes advanced smooth movement capabilities that eliminate jerky servo movements and provide professional, fluid camera control.

## Key Features

### 1. Smooth Movement Functions
- **smooth_move_servo()**: Core function for smooth servo movement with easing
- **smooth_set_camera_position()**: Simultaneously move both pan and tilt servos
- **Enhanced convenience methods**: All camera control methods now support smooth movement

### 2. Easing Functions
Four different easing types available:

#### Linear (`"linear"`)
- Constant speed throughout movement
- Simple and predictable motion

#### Ease-In (`"ease_in"`)
- Starts slow, accelerates at the end
- Good for dramatic camera movements
- Formula: `t²`

#### Ease-Out (`"ease_out"`)
- Starts fast, decelerates at the end
- Natural-feeling movements
- Formula: `1 - (1-t)²`

#### Ease-In-Out (`"ease_in_out"`)
- Starts slow, speeds up in middle, slows down at end
- Most professional and smooth appearance
- Formula: `2t²` (first half), `1 - 2(1-t)²` (second half)

## Usage Examples

### Basic Smooth Movement
```python
# Move tilt servo smoothly to 45° over 1.5 seconds with ease-in-out
robot.servo_controller.smooth_move_servo("camera_tilt", 45, 1.5, "ease_in_out")

# Move both servos simultaneously
robot.servo_controller.smooth_set_camera_position(tilt=60, pan=120, duration=2.0, easing="ease_in_out")
```

### Convenience Methods with Smooth Movement
```python
# All convenience methods now support smooth movement (enabled by default)
robot.camera_look_up(30, smooth=True, duration=0.8)
robot.camera_look_down(45, smooth=True, duration=1.0)
robot.camera_look_left(60, smooth=True, duration=0.5)
robot.camera_look_right(30, smooth=True, duration=1.2)
robot.camera_center(smooth=True)

# For instant movement (old behavior)
robot.camera_look_up(30, smooth=False)
```

### Interactive Controls
In interactive mode:
- **i/k/j/l/c**: Smooth camera movements (default)
- **I/K/J/L/C**: Instant camera movements (hold Shift)

## Technical Details

### Movement Parameters
- **Duration**: Time in seconds (0.1 to 10.0 recommended)
- **Steps**: Automatically calculated based on movement range
- **Step Delay**: Automatically calculated for smooth timing
- **Angle Validation**: All angles clamped to servo limits

### Performance Optimization
- Minimum movement threshold (1°) to avoid unnecessary micro-movements
- Dynamic step calculation (more steps for larger movements)
- Simultaneous dual-servo movements using threading
- Efficient PWM updates with minimal overhead

### Easing Implementation
```python
def _ease_in_out(self, t):
    """Ease-in-out function (quadratic)"""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - 2 * (1 - t) * (1 - t)
```

## Testing Modes

### Camera Test Mode
```bash
./run_robot.sh --mode camera
```
Comprehensive test of all smooth movement features including:
- Different easing functions demonstration
- Side-by-side comparison of jerky vs smooth movement
- Various duration and angle combinations

### Interactive Mode
```bash
./run_robot.sh --mode interactive
```
Real-time testing with immediate feedback:
- Smooth movements: `i/k/j/l/c`
- Instant movements: `I/K/J/L/C`

## Benefits

### 1. Professional Appearance
- Eliminates jerky, robotic movements
- Creates smooth, cinematic camera motion
- Reduces mechanical stress on servos

### 2. Better Video Quality
- No sudden camera jumps in recordings
- Smooth tracking and positioning
- Professional video production quality

### 3. Hardware Protection
- Gradual movements reduce servo wear
- Less mechanical shock and vibration
- Extended servo lifespan

### 4. User Experience
- More intuitive and natural control
- Responsive yet smooth interaction
- Configurable movement characteristics

## Configuration Options

### Default Settings
- **Duration**: 0.8 seconds for basic movements
- **Easing**: "ease_in_out" for natural feel
- **Smooth Mode**: Enabled by default in all new commands

### Customization
```python
# Custom smooth movement
robot.servo_controller.smooth_move_servo(
    servo_name="camera_tilt",
    target_angle=60,
    duration=2.0,        # Slower movement
    easing="ease_out"    # Different easing style
)

# Quick movements when needed
robot.servo_controller.smooth_move_servo(
    servo_name="camera_pan", 
    target_angle=90,
    duration=0.3,        # Fast movement
    easing="linear"      # No easing for speed
)
```

## Troubleshooting

### Common Issues
1. **Movement too slow**: Reduce duration parameter
2. **Movement too fast**: Increase duration parameter
3. **Jerky movement**: Check easing function selection
4. **No movement**: Verify servo connections and angles

### Performance Tips
1. Use "ease_in_out" for most movements
2. Keep durations between 0.5-2.0 seconds for best results
3. Use smooth=False for emergency stops
4. Test different easing functions for your specific application

## Backwards Compatibility
All existing code continues to work unchanged. Smooth movement is opt-in through new parameters, ensuring existing scripts remain functional while providing enhanced capabilities for new implementations.
