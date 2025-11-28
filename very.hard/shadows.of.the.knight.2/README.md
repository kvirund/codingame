# Shadows of the Knight Episode 2 - Solution Approach

This document describes the approach I used to solve the Shadows of the Knight Episode 2 puzzle on CodinGame. I'm not providing the specific implementation code here, just describing the methodology that worked.

## Problem Overview

Batman must find a bomb hidden in a building represented as a W×H grid (up to 10000×10000). After each jump, you only get feedback: **WARMER**, **COLDER**, or **SAME** - indicating whether you moved closer or farther from the bomb (Euclidean distance). You have limited jumps to find the exact cell.

## Solution: Hybrid Constraint/Cell Algorithm

The key challenge is handling grids up to 100 million cells efficiently while converging in ~30 jumps.

### Core Insight: Half-Plane Constraints

Each WARMER/COLDER feedback defines a **half-plane constraint**:
- The perpendicular bisector between previous and current position divides the grid
- WARMER → bomb is on your side of the bisector
- COLDER → bomb is on the opposite side

Mathematically: `dx*x + dy*y > c` or `dx*x + dy*y < c`

### Two-Phase Approach

#### Phase 1: Constraint-Based (Large Grids)

For grids too large to enumerate (>25k cells):

1. Store each feedback as a half-plane constraint
2. Compute the **bounding box** of the valid region by finding:
   - Intersections of constraint lines with grid boundaries
   - Pairwise intersections of constraint lines
   - Grid corners that satisfy all constraints
3. Jump toward the center of the bounding box using **reflection strategy**

#### Phase 2: Cell-Based (Small Regions)

When the bounding box shrinks below threshold:

1. Enumerate all cells in the bounding box
2. Filter to cells satisfying all constraints
3. Use exact centroid for more precise jumps
4. SAME feedback can now be handled exactly (equidistant cells only)

### Jump Strategy: Adaptive Reflection

Instead of always jumping to the centroid, use **reflection through the centroid**:

```
target = k * centroid - (k-1) * current_position
```

The multiplier `k` is adaptive:
- **k = 2.0** for large regions (standard reflection, bisects the region)
- **k = 1.5** for medium regions (softer reflection, cuts off 1/3)
- **k = 1.8** for small regions near grid edges (more aggressive convergence)

This prevents oscillation and handles corner cases better than fixed reflection.

### Handling Edge Cases

#### Corner Bombs
When the bomb is near a corner (e.g., position (0,1) in an 8000×8000 grid):
- Standard 2x reflection can overshoot beyond the grid
- Near-edge detection triggers softer reflection coefficients
- Forces cell-based mode earlier when one dimension becomes narrow

#### Oscillation Detection
If the algorithm would return to a recent position:
- Sort candidates by distance to centroid
- Pick the closest unvisited candidate
- Fallback to small step toward centroid if still stuck

## Performance Considerations

The main constraint is **150ms per turn**. Critical optimizations:

1. **CELL_THRESHOLD = 25000** - Maximum cells to enumerate
   - 25k cells × 15 constraints ≈ 375k operations ≈ 50ms

2. **Single bbox computation per turn** - Cache results instead of recomputing

3. **Early mode switching** - Switch to cell-based when bbox becomes narrow in any dimension

## Complexity Analysis

| Operation | Complexity |
|-----------|------------|
| Add constraint | O(1) |
| Compute bbox | O(n²) where n = constraints |
| Generate cells | O(area × constraints) |
| Filter cells | O(candidates) |

With ~30 jumps maximum: n² ≈ 900 intersection checks - fast enough.

## Theoretical vs Actual Performance

For 8000×8000 grid (64M cells):
- Theoretical minimum: ceil(log₂(64M)) + 1 = **27 jumps**
- Algorithm achieves: **28-30 jumps** (depending on bomb position)
- Allowed maximum: **31 jumps**

## Key Insights

1. **Don't enumerate cells too early** - 100k cells with 12 constraints = 1.2M operations = timeout

2. **Reflection beats simple centroid jumping** - Centroid alone doesn't converge fast enough

3. **Adaptive coefficients matter** - 2x reflection overshoots near corners, 1.5x-1.8x works better

4. **Bounding box from constraint intersections** - More accurate than sampling-based approaches

5. **SAME feedback is rare but tricky** - In constraint mode, hard to represent exactly; in cell mode, filter to equidistant cells

## Testing Approach

Built a local emulator matching CodinGame's mechanics to test solutions rapidly. Key test cases:
- Small grids (50×50) for algorithm correctness
- Large grids (1000×1000, 8000×8000) for performance
- Corner positions (0,1), (1,1) for edge case handling
