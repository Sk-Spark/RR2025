# Mecanum Wheel Movement Guide

## 🎯 Mecanum Wheel Capabilities

Your robot now supports **FULL OMNIDIRECTIONAL MOVEMENT** with mecanum wheels!

## 📋 Movement Matrix

### Basic Movements
| Command | Movement | Description |
|---------|----------|-------------|
| `w` | ⬆️ Forward | All wheels forward |
| `s` | ⬇️ Backward | All wheels backward |
| `a` | ↩️ Turn Left | Right wheels forward, left wheels backward |
| `d` | ↪️ Turn Right | Left wheels forward, right wheels backward |

### Mecanum-Specific Movements
| Command | Movement | Description |
|---------|----------|-------------|
| `z` | ⬅️ Strafe Left | FL+RR forward, FR+RL backward |
| `x` | ➡️ Strafe Right | FR+RL forward, FL+RR backward |
| `u` | ↖️ Diagonal Forward-Left | FL+RR forward only |
| `o` | ↗️ Diagonal Forward-Right | FR+RL forward only |
| `m` | ↙️ Diagonal Backward-Left | FR+RL backward only |
| `.` | ↘️ Diagonal Backward-Right | FL+RR backward only |
| `r` | 🔄 Rotate CCW | FL+RL backward, FR+RR forward |
| `t` | 🔃 Rotate CW | FL+RL forward, FR+RR backward |

### Camera Controls
| Command | Movement | Description |
|---------|----------|-------------|
| `i` | 📷⬆️ Look Up | Tilt camera up |
| `k` | 📷⬇️ Look Down | Tilt camera down |
| `j` | 📷⬅️ Look Left | Pan camera left |
| `l` | 📷➡️ Look Right | Pan camera right |
| `c` | 📷🎯 Center | Center camera |

## 🎮 Advanced Control

### Mecanum Combined Movement
```bash
mecanum <x_speed> <y_speed> <rotation_speed>
```

Examples:
- `mecanum 50 0 0` - Move right at 50% speed
- `mecanum 0 50 0` - Move forward at 50% speed
- `mecanum 50 50 0` - Move diagonally forward-right
- `mecanum 0 0 50` - Rotate clockwise
- `mecanum 30 40 -20` - Move forward-right while rotating left

## 🔧 Motor Layout
```
    Front
FL -------- FR
|    ^      |
|    |      |  
|  Robot    |
|    |      |
|    v      |
RL -------- RR
    Rear
```

**Legend:**
- FL = Front Left
- FR = Front Right  
- RL = Rear Left
- RR = Rear Right

## 🚀 Kinematics Formula

The mecanum wheel equations used:
```
FL = y + x + rotation
FR = y - x - rotation  
RL = y - x + rotation
RR = y + x - rotation
```

Where:
- `x` = lateral movement (positive = right)
- `y` = forward movement (positive = forward)
- `rotation` = rotational movement (positive = clockwise)

## 🎯 Usage Examples

1. **Pure Translation:** Move without rotating
2. **Pure Rotation:** Rotate without translating  
3. **Combined Movement:** Move and rotate simultaneously
4. **Diagonal Movement:** Move at any angle
5. **Holonomic Motion:** Independent control of X, Y, and rotation

Your robot can now move like a pro with complete omnidirectional control! 🤖✨
