# Mars Lander - Episode 3

## The Goal

The goal for your program is to safely land the "Mars Lander" shuttle, the landing ship which contains the Opportunity rover. Mars Lander is guided by a program, and right now the failure rate for landing on the NASA simulator is unacceptable.

This puzzle is the last level of the "Mars Lander" trilogy. The controls are the same as the previous levels but the surface is more complex...

## Rules

Built as a game, the simulator puts Mars Lander on a limited zone of Mars sky.

- The zone is **7000m wide** and **3000m high**.
- There is a unique area of **flat ground** on the surface of Mars, which is at least **1000 meters wide**.

Every second, depending on the current flight parameters (location, speed, fuel ...), the program must provide the new desired tilt angle and thrust power of Mars Lander:

- **Angle** goes from -90° to 90°
- **Thrust power** goes from 0 to 4

The game simulates a **free fall without atmosphere**. Gravity on Mars is **3.711 m/s²**. For a thrust power of X, a push force equivalent to X m/s² is generated and X liters of fuel are consumed. As such, a thrust power of 4 in an almost vertical position is needed to compensate for the gravity on Mars.

### Landing Conditions

For a landing to be successful, the ship must:
- Land on **flat ground**
- Land in a **vertical position** (tilt angle = 0°)
- **Vertical speed** must be limited (≤ 40m/s in absolute value)
- **Horizontal speed** must be limited (≤ 20m/s in absolute value)

## Game Input

### Initialization Input

- **Line 1:** the number `surfaceN` of points used to draw the surface of Mars.
- **Next surfaceN lines:** a couple of integers `landX landY` providing the coordinates of a ground point. By linking all the points together in a sequential fashion, you form the surface of Mars which is composed of several segments. For the first point, landX = 0 and for the last point, landX = 6999

### Input for One Game Turn

A single line with 7 integers: `X Y hSpeed vSpeed fuel rotate power`

| Variable | Description |
|----------|-------------|
| X, Y | Coordinates of Mars Lander (in meters) |
| hSpeed | Horizontal speed (in m/s), can be negative |
| vSpeed | Vertical speed (in m/s), can be negative |
| fuel | Remaining quantity of fuel in liters |
| rotate | Rotation angle in degrees (-90 to 90) |
| power | Thrust power (0 to 4) |

### Output for One Game Turn

A single line with 2 integers: `rotate power`

- **rotate** is the desired rotation angle for Mars Lander. Please note that for each turn the actual value of the angle is limited to the value of the previous turn **+/- 15°**.
- **power** is the desired thrust power. 0 = off. 4 = maximum power. Please note that for each turn the value of the actual power is limited to the value of the previous turn **+/- 1**.

## Constraints

| Constraint | Range |
|------------|-------|
| surfaceN | 2 ≤ surfaceN < 30 |
| X | 0 ≤ X < 7000 |
| Y | 0 ≤ Y < 3000 |
| hSpeed, vSpeed | -500 < hSpeed, vSpeed < 500 |
| fuel | 0 ≤ fuel ≤ 2000 |
| rotate | -90 ≤ rotate ≤ 90 |
| power | 0 ≤ power ≤ 4 |
| Response time | ≤ 100ms per turn |

## Example

### Initialization Input
```
6                   (surfaceN) Surface made of 6 points
0 1500              (landX landY)
1000 2000           (landX landY)
2000 500            (landX landY) Start of flat ground
3500 500            (landX landY) End of flat ground
5000 1500           (landX landY)
6999 1000           (landX landY)
```

### Turn 1
**Input:** `5000 2500 -50 0 1000 90 0` (X Y hSpeed vSpeed fuel rotate power)

**Output:** `-45 4` (rotate power) - Requested rotation to the right, maximum thrust power

### Turn 2
**Input:** `4950 2498 -51 -3 999 75 1` (X Y hSpeed vSpeed fuel rotate power)

Note: Tilt angle changed only by 15° and thrust power only by 1

**Output:** `-45 4` (rotate power) - Same request as previous turn

### Turn 3
**Input:** `4898 2493 -53 -6 997 60 2` (X Y hSpeed vSpeed fuel rotate power)

**Output:** `-45 4` (rotate power) - Same request as previous turn

## Test Cases

1. **Cave, correct side** - Starting on the correct side of the cave
2. **Cave, wrong side** - Starting on the wrong side of the cave (need to navigate around)
