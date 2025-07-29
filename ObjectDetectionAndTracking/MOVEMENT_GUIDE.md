# Ball Tracking Movement System Documentation

## Overview
The ball tracking robot now supports multiple movement types for following the ball, making it configurable for different robot designs and tracking scenarios.

## Movement Types

### 1. Mecanum Movement (`mecanum`)
**Default configuration**
- **Description**: Full mecanum wheel movement with strafing, forward/backward, and rotation
- **Best for**: Robots with mecanum wheels that need maximum flexibility
- **Capabilities**: 
  - Left/right strafing to center ball horizontally
  - Forward/backward movement based on ball distance
  - Rotation to keep ball centered
- **Use case**: Most versatile option for omni-directional robots

### 2. Tank Movement (`tank`)
- **Description**: Tank-style movement with forward/backward and rotation only
- **Best for**: Tracked vehicles, tank-style robots, or robots without strafing capability
- **Capabilities**:
  - Forward/backward movement
  - Left/right rotation to turn toward ball
  - No strafing movement
- **Use case**: Traditional wheeled robots that cannot strafe

### 3. Simple Movement (`simple`)
- **Description**: Basic directional movement (one direction at a time)
- **Best for**: Simple robots or testing scenarios
- **Capabilities**:
  - Forward, backward, left, or right movement
  - Prioritizes larger error (horizontal vs vertical)
  - One movement direction at a time
- **Use case**: Basic robots or step-by-step debugging

### 4. Strafe Only (`strafe_only`)
- **Description**: Only left/right strafing movement
- **Best for**: Fixed-position tracking where robot shouldn't move forward/backward
- **Capabilities**:
  - Left/right strafing only
  - No forward/backward movement
  - No rotation
- **Use case**: Robots on a fixed rail or table edge

### 5. Turn Only (`turn_only`)
- **Description**: Only rotation movement
- **Best for**: Stationary robots that only need to rotate to track
- **Capabilities**:
  - Rotation only to center ball horizontally
  - No translation movement
- **Use case**: Fixed-position turret-style tracking

## Configuration Options

### Movement Type Selection
Set in `config.py`:
```python
MOVEMENT_TYPE = "mecanum"  # Options: "mecanum", "tank", "simple", "strafe_only", "turn_only"
```

### Movement Capabilities
Enable/disable specific movement types:
```python
ENABLE_ROTATION_TRACKING = True   # Enable rotation to center ball horizontally
ENABLE_FORWARD_BACKWARD = True    # Enable forward/backward movement based on ball distance
ENABLE_STRAFING = True           # Enable left/right strafing movement
```

### Movement Gains
Fine-tune movement sensitivity:
```python
ROTATION_GAIN = 0.8      # Gain for rotational tracking (0.1-2.0)
FORWARD_GAIN = 0.6       # Gain for forward/backward movement (0.1-2.0)
STRAFE_GAIN = 0.8        # Gain for strafing movement (0.1-2.0)
```

## Quick Configuration

### Using the Configuration Utility
Run the interactive configuration tool:
```bash
cd /home/spark/RR2025/ObjectDetectionAndTracking
python3 configure_movement.py
```

### Manual Configuration
Edit `config.py` directly to change:
- `MOVEMENT_TYPE`: Select movement type
- `ENABLE_*`: Enable/disable movement capabilities
- `*_GAIN`: Adjust movement sensitivity
- `MOTOR_FOLLOW_SPEED`: Base movement speed
- `MOTOR_MAX_SPEED`: Maximum movement speed

## Movement Behavior

### Ball Position Logic
- **Horizontal Error**: Ball position relative to frame center (left/right)
- **Vertical Error**: Ball position relative to frame center (up/down)
- **Ball Size**: Used to determine distance (small = far, large = close)

### Movement Calculations
1. **Strafing**: Moves left/right to center ball horizontally
2. **Forward/Backward**: Based on ball size to maintain optimal distance
3. **Rotation**: Turns robot to keep ball centered

### Deadzone System
Prevents jittery movement when ball is near center:
- `MOTOR_DEADZONE_X`: Horizontal deadzone (15% of frame width)
- `MOTOR_DEADZONE_Y`: Vertical deadzone (15% of frame height)

## Display Information

The video overlay shows:
- **Movement Type**: Current movement configuration
- **Motor Status**: ACTIVE/READY
- **Movement Modes**: S (Strafing), F (Forward/Back), R (Rotation)

## Troubleshooting

### Robot Not Moving
1. Check `ENABLE_MOTOR_FOLLOWING = True` in config
2. Verify movement type is appropriate for your robot
3. Check motor controller initialization
4. Verify ball detection is working

### Erratic Movement
1. Increase deadzone values
2. Reduce movement gains
3. Lower movement speeds
4. Check for detection noise

### Wrong Movement Direction
1. Verify motor wiring and configuration
2. Check motor direction settings in motor config
3. Test individual motor functions

## Example Configurations

### Mecanum Wheel Robot (Default)
```python
MOVEMENT_TYPE = "mecanum"
ENABLE_ROTATION_TRACKING = True
ENABLE_FORWARD_BACKWARD = True
ENABLE_STRAFING = True
STRAFE_GAIN = 0.8
FORWARD_GAIN = 0.6
ROTATION_GAIN = 0.8
```

### Tank-Style Robot
```python
MOVEMENT_TYPE = "tank"
ENABLE_ROTATION_TRACKING = True
ENABLE_FORWARD_BACKWARD = True
ENABLE_STRAFING = False  # Tank can't strafe
ROTATION_GAIN = 1.0
FORWARD_GAIN = 0.8
```

### Fixed Position Tracker
```python
MOVEMENT_TYPE = "turn_only"
ENABLE_ROTATION_TRACKING = True
ENABLE_FORWARD_BACKWARD = False
ENABLE_STRAFING = False
ROTATION_GAIN = 1.2
```

### Simple Testing Setup
```python
MOVEMENT_TYPE = "simple"
ENABLE_ROTATION_TRACKING = False
ENABLE_FORWARD_BACKWARD = True
ENABLE_STRAFING = True
MOTOR_FOLLOW_SPEED = 30  # Slower for testing
```

## Integration Notes

- All movement types use the same motor controller interface
- Configuration changes require system restart
- Movement gains can be adjusted during runtime via config
- Display overlay updates automatically based on configuration
- Status reporting includes current movement configuration
