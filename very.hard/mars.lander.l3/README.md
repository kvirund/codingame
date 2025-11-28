# Mars Lander Episode 3 - Solution Approach

> ⚠️ **Disclaimer**: This puzzle was solved with significant assistance from Claude Opus 4.5.

This document describes the approach I used to solve the Mars Lander Episode 3 puzzle on CodinGame. I'm not providing the specific implementation code here, just describing the methodology that worked.

## Problem Overview

Mars Lander Episode 3 features complex terrain including **caves** - the landing zone may be inside a cavern with a roof overhead. The challenge is navigating through the cave entrance to reach the landing zone safely.

## Solution: Waypoint-Based Path Planning

Instead of trying to directly control the lander toward the landing zone, I implemented a **two-phase approach**:

1. **Path Planning Phase** - Analyze terrain and generate waypoints
2. **Flight Control Phase** - Follow waypoints with velocity control

### Phase 1: Path Planning

#### Cave Detection

The key insight is detecting whether the landing zone is inside a cave:

- Scan terrain points above the landing zone
- If there are high terrain points (significantly above LZ altitude) within the horizontal bounds of the LZ, it's a cave
- Track the **roof bounds** - the leftmost and rightmost extent of the cave ceiling

#### Finding Cave Entrances

This was the critical part. The algorithm must find where to **descend into the cave**:

- Search for clear vertical descent paths **outside** the roof bounds
- For each potential descent point, verify that a vertical line from high altitude to entry altitude doesn't intersect any terrain
- Check both left and right sides of the cave

#### Validating Entry Paths

After finding descent points, verify the **horizontal path** from descent point to LZ center is clear:

- At the chosen entry altitude, check that flying horizontally won't hit any terrain
- Handle complex terrain where surface segments may go "backwards" in X (forming cave walls)

#### Waypoint Generation

The final path consists of:

1. **Cruise waypoint** - Fly horizontally above all terrain to the descent point
2. **Descent waypoint** - Drop down through the cave entrance
3. **Entry waypoint** - Fly horizontally into the cave toward LZ
4. **Landing waypoint** - Final approach over the landing zone

### Phase 2: Flight Control

#### Navigation Mode (following waypoints)

- Calculate direction to current waypoint
- Use tilt angle to control horizontal velocity (lean to accelerate/brake)
- Maintain safe vertical speed - don't fall too fast
- Limit maximum horizontal speed to stay controllable
- Switch to next waypoint when close enough

#### Landing Mode (over landing zone)

When above the landing zone at low altitude:

- Prioritize zeroing horizontal speed
- Gradually reduce tilt angle toward 0
- Control descent rate to stay under 40 m/s vertical
- Final approach: angle must be 0, gentle touchdown

## Key Insights

1. **Don't descend over the LZ** - If there's a cave roof, descending directly above the landing zone will crash into the ceiling

2. **Find the roof bounds first** - Before planning descent, identify where the cave roof starts and ends horizontally

3. **Search outside the roof** - Look for clear descent paths beyond the roof edges, not from the LZ edges

4. **Validate both vertical AND horizontal paths** - A clear descent point is useless if you can't fly from there to the LZ

5. **Terrain can go "backwards"** - Cave structures often have surface segments where X decreases (forming the roof going back over the cave). This creates the cave ceiling geometry.

## Testing Approach

I built a physics emulator matching CodinGame's engine to test solutions locally before submitting. This allowed rapid iteration without waiting for the web interface.

Key physics details discovered through reverse engineering:

- Gravity: 3.711 m/s²
- Angle/power change limits: ±15° and ±1 per turn
- Position update formula: `new_pos = pos + velocity + 0.5 * acceleration`
- Internal state uses floating point, output values are rounded

## What Didn't Work

- **Genetic algorithms** - Too slow to converge for complex cave scenarios
- **Direct path to LZ center** - Crashes into cave roofs
- **Searching from LZ edges** - Roof may extend beyond LZ boundaries
