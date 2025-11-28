# There is no Spoon Episode 2 - Solution Approach

> ⚠️ **Disclaimer**: This puzzle was solved with significant assistance from Claude Opus 4.5.

This document describes the approach I used to solve There is no Spoon Episode 2 (Hashiwokakero) on CodinGame. I'm not providing the implementation code here, just describing the methodology that worked.

## Problem Overview

Hashiwokakero (橋をかけろ, "build bridges") is a logic puzzle:
- Grid contains islands with numbers 1-8 indicating required connections
- Connect islands with horizontal/vertical bridges (1 or 2 per pair)
- Bridges cannot cross each other or pass through islands
- All islands must form a single connected component

Grid size: up to 30×30, time limit: 1 second for first output.

## Solution: Constraint Propagation + Backtracking

The algorithm has two phases that alternate:

### Phase 1: Constraint Propagation

Apply logical rules repeatedly until no new bridges can be deduced:

#### Rule 1: Forced Bridges
If the sum of maximum possible bridges equals the island's requirement, all bridges are mandatory.

**Example**: Island "4" with only two neighbors (max 2 each = 4 total) → must use all 4 bridges.

#### Rule 2: Single Neighbor
If an island has only one available neighbor, all its bridges go there.

#### Rule 3: The 2n-1 Rule
If an island needs ≥ 2n-1 bridges with n neighbors, each neighbor must have at least 1 bridge.

**Example**: Island "5" with 3 neighbors (max 6) → each gets at least 1 bridge.

#### Rule 4: Pair with High Requirement
If an island has exactly 2 neighbors and needs ≥3 bridges, each neighbor gets at least 1.

### Phase 2: Backtracking with Smart Heuristics

When propagation stalls, pick a node and try adding bridges:

#### MRV (Minimum Remaining Values) Heuristic

**Key insight**: Select the node with minimum "slack" - the difference between maximum possible bridges and required bridges.

- Slack 0 = fully determined (handled by propagation)
- Slack 1 = only one choice to make
- Higher slack = more uncertainty

**This was the critical optimization**. Originally I selected nodes with fewer neighbors, but this was wrong. A node "1" with 2 neighbors has slack 3 (can add 0-4, needs 1), while a node "6" with 3 neighbors has slack 0 (needs all 6). Processing low-slack nodes first dramatically reduces the search tree.

#### Bridge Ordering

When trying bridges to a selected node's neighbors:
1. Try 2 bridges first (more constrained choice)
2. Then try 1 bridge
3. Order neighbors by their constraint level (low slack first)

#### Undo Stack

Track all bridge additions on a stack. When backtracking, undo to the saved position in O(k) where k is bridges added since that point.

### Connectivity Check

Use Union-Find (Disjoint Set Union) with path compression:
- Merge components when adding bridges
- Final check: all islands in same component

**Caveat**: Union-Find doesn't support "undo", so I rebuild it from the bridge stack when needed.

### Bridge Crossing Detection

Precompute which potential bridges would cross:
- A horizontal bridge between (x1,y)-(x2,y) crosses a vertical bridge (x,y1)-(x,y2) if x is strictly between x1,x2 and y is strictly between y1,y2
- Store crossing pairs for O(1) lookup when checking if a bridge is blocked

## Performance Considerations

The main challenge was the "CG" test (test 11) - a complex shape that initially timed out.

### What Didn't Work

1. **Zobrist Hashing / Transposition Tables** - Added overhead exceeded benefits
2. **Island Detection Pruning** - Too expensive (requires rebuilding Union-Find)
3. **Wrong MRV ordering** - Prioritizing by neighbor count instead of slack

### What Worked

1. **Correct MRV with slack-based scoring** - Reduced search tree exponentially
2. **Trying 2 bridges before 1** - More constrained choices prune faster
3. **Simple undo stack** - O(1) add, O(k) undo, no complex data structures

## Complexity Analysis

- Constraint propagation: O(N² × E) per iteration, typically converges in O(N) iterations
- Backtracking: exponential worst case, but propagation handles most of the work
- Practical performance: 17-24ms for hardest tests

## Key Insights

1. **Propagation solves most of the puzzle** - Good rules eliminate 80%+ of decisions

2. **MRV heuristic is crucial** - Wrong ordering means exploring huge search trees

3. **"Slack" is the right metric** - Not neighbor count, not requirement value

4. **Simple beats clever** - Transposition tables and fancy pruning added more overhead than they saved

5. **Test locally** - Built an emulator to iterate quickly without CodinGame's web interface

## Testing Approach

Created 14 test cases including:
- Simple grids (test 1-3)
- Complex interconnected patterns (test 7-8)
- "CG" letter shapes (test 11, 14)
- Large expert grids (test 13)

Local emulator validates solutions by checking bridge counts, crossings, and connectivity.
