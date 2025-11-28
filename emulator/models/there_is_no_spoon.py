"""There is no Spoon Episode 2 game model plugin (Hashiwokakero)."""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional, Set

from .base import GameModel, SimResult


TESTS_DIR = Path(__file__).parent.parent / "tests" / "there-is-no-spoon-2"


def load_test_cases_from_files() -> dict:
    """Load all test cases from JSON files."""
    test_cases = {}
    if not TESTS_DIR.exists():
        return test_cases

    for json_file in sorted(TESTS_DIR.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            name = json_file.stem
            test_cases[name] = data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load {json_file}: {e}")

    return test_cases


@dataclass
class State:
    """Current puzzle state."""
    grid: List[List[int]]  # Remaining links needed: 0=empty, 1-8=node
    connections: List[Tuple[int, int, int, int, int]] = field(default_factory=list)  # (x1,y1,x2,y2,count)
    done: bool = False


@dataclass
class Environment:
    """Puzzle environment."""
    width: int
    height: int
    initial_grid: List[List[int]]  # Original node values
    nodes: List[Tuple[int, int, int]]  # (x, y, value) for all nodes


@dataclass
class Control:
    """Player's output - one link."""
    x1: int
    y1: int
    x2: int
    y2: int
    amount: int

    @staticmethod
    def parse(line: str) -> 'Control':
        parts = line.strip().split()
        return Control(
            int(parts[0]), int(parts[1]),
            int(parts[2]), int(parts[3]),
            int(parts[4])
        )


class ThereIsNoSpoonModel(GameModel):
    """There is no Spoon Episode 2 game model (Hashiwokakero)."""

    name = "there_is_no_spoon"
    description = "There is no Spoon Episode 2"

    def __init__(self):
        self._test_cases = load_test_cases_from_files()

    def get_test_cases(self) -> dict[str, str]:
        return {name: tc.get("name", name) for name, tc in self._test_cases.items()}

    def load_test_case(self, name: str) -> Tuple[Environment, State]:
        if name not in self._test_cases:
            raise ValueError(f"Unknown test case: {name}. Available: {list(self._test_cases.keys())}")

        tc = self._test_cases[name]
        width = tc["width"]
        height = tc["height"]
        lines = tc["grid"]

        # Parse grid
        initial_grid = []
        nodes = []
        for y, line in enumerate(lines):
            row = []
            for x, ch in enumerate(line):
                if ch == '.':
                    row.append(0)
                else:
                    val = int(ch)
                    row.append(val)
                    nodes.append((x, y, val))
            # Pad row if shorter than width
            while len(row) < width:
                row.append(0)
            initial_grid.append(row)

        env = Environment(
            width=width,
            height=height,
            initial_grid=initial_grid,
            nodes=nodes
        )

        # Deep copy for state
        state_grid = [row[:] for row in initial_grid]
        state = State(grid=state_grid)

        return env, state

    def format_init_input(self, env: Environment) -> List[str]:
        """Format initialization input: width, height, grid lines."""
        lines = [str(env.width), str(env.height)]
        for row in env.initial_grid:
            line = ''.join('.' if v == 0 else str(v) for v in row)
            lines.append(line)
        return lines

    def format_turn_input(self, state: State) -> str:
        """No turn input for this puzzle - single output game."""
        return ""

    def parse_output(self, line: str) -> Control:
        return Control.parse(line)

    def simulate(self, state: State, control: Control, env: Environment) -> Tuple[State, SimResult]:
        """Apply one link. Stub - minimal validation."""
        x1, y1, x2, y2, amount = control.x1, control.y1, control.x2, control.y2, control.amount

        # Basic validation
        if amount < 1 or amount > 2:
            return state, SimResult('failure', f"Invalid amount: {amount}")

        if x1 < 0 or x1 >= env.width or y1 < 0 or y1 >= env.height:
            return state, SimResult('failure', f"({x1},{y1}) out of bounds")

        if x2 < 0 or x2 >= env.width or y2 < 0 or y2 >= env.height:
            return state, SimResult('failure', f"({x2},{y2}) out of bounds")

        # Must be horizontal or vertical
        if x1 != x2 and y1 != y2:
            return state, SimResult('failure', f"Link must be horizontal or vertical")

        if x1 == x2 and y1 == y2:
            return state, SimResult('failure', f"Link endpoints must be different")

        # Create new state
        new_grid = [row[:] for row in state.grid]
        new_connections = state.connections + [(x1, y1, x2, y2, amount)]

        # Decrement node values
        new_grid[y1][x1] -= amount
        new_grid[y2][x2] -= amount

        # Check for over-connection
        if new_grid[y1][x1] < 0:
            return state, SimResult('failure', f"Node ({x1},{y1}) has too many links")
        if new_grid[y2][x2] < 0:
            return state, SimResult('failure', f"Node ({x2},{y2}) has too many links")

        new_state = State(grid=new_grid, connections=new_connections)

        # Check if all nodes satisfied
        all_done = all(
            new_grid[y][x] == 0
            for x, y, _ in env.nodes
        )

        if all_done:
            # TODO: Check connectivity
            new_state.done = True
            return new_state, SimResult('success')

        return new_state, SimResult('running')

    def format_result(self, state: State) -> str:
        return f"connections={len(state.connections)}, done={state.done}"
