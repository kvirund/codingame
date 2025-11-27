# Mars Lander Emulator

Physics emulator for testing Mars Lander control algorithms. Achieves 100% accuracy against CodinGame's game engine.

## Physics Model

### Constants
- **Gravity**: 3.711 m/s²
- **Zone**: 7000m × 3000m
- **Angle range**: -90° to +90°
- **Power range**: 0 to 4

### Control Constraints (per turn)
- Angle change: ±15° maximum
- Power change: ±1 maximum

### Kinematic Equations
```
velocity_new = velocity + acceleration
position_new = position + velocity + 0.5 * acceleration
```

### Key Implementation Details

**Internal Float State**: The game maintains internal floating-point state between turns. Each physics step uses float values from the previous step, not the integers shown to the player.

**Rounding Method**: Integer output uses "round half away from zero":
- 2.5 → 3
- -2.5 → -3
- 2.4 → 2
- -2.4 → -2

## API Reference

### Classes

#### `State`
Integer state as returned to player:
```python
@dataclass
class State:
    x: int        # Horizontal position (m)
    y: int        # Vertical position (m)
    hSpeed: int   # Horizontal speed (m/s)
    vSpeed: int   # Vertical speed (m/s)
    fuel: int     # Remaining fuel (L)
    rotate: int   # Current angle (degrees)
    power: int    # Current thrust (0-4)
```

#### `FloatState`
Internal floating-point state:
```python
@dataclass
class FloatState:
    x: float
    y: float
    hSpeed: float
    vSpeed: float
    fuel: int
    rotate: int
    power: int
```

#### `Control`
Player command:
```python
@dataclass
class Control:
    rotate: int  # Desired angle (-90 to 90)
    power: int   # Desired thrust (0 to 4)
```

#### `Surface`
Terrain definition:
```python
@dataclass
class Surface:
    points: List[Point]      # Terrain vertices
    landing_zone: LandingZone  # Flat landing area
```

#### `Emulator`
Main emulator class:
```python
emulator = Emulator(surface, initial_state)
result = emulator.step(control)  # Returns SimResult
```

### Functions

#### `simulate_turn_float(fstate, control, surface)`
Simulates one physics turn with internal float state.

#### `load_test_case(filepath)`
Loads test case from JSON file.

## Usage

### Validate Against Test Cases
```bash
python emulator.py --float
```

### Run with Custom Controller
```python
from emulator import Emulator, Control, load_test_case

surface, state = load_test_case('test_case_01.json')
emulator = Emulator(surface, state)

while True:
    # Your control logic here
    control = Control(rotate=0, power=4)
    result = emulator.step(control)

    if result.status != 'flying':
        print(f"Result: {result.status}")
        break
```

## Landing Conditions

For successful landing:
- Land on **flat ground** (landing zone)
- **Angle = 0°** (vertical)
- **|vSpeed| ≤ 40 m/s**
- **|hSpeed| ≤ 20 m/s**

## Test Cases

| File | Name | Landing Zone | Start Position |
|------|------|--------------|----------------|
| test_case_01.json | Cave, correct side | x=2200-3200, y=150 | (6500, 2600) |
| test_case_02.json | Cave, wrong side | x=3700-4700, y=220 | (6500, 2000) |
