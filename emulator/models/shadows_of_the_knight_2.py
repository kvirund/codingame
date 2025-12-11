"""Shadows of the Knight Episode 2 game model plugin."""
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from .base import GameModel, SimResult


TESTS_DIR = Path(__file__).parent.parent / "tests" / "shadows-of-the-knight-2"
TRACES_DIR = Path(__file__).parent.parent / "traces" / "shadows-of-the-knight-2"


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
    """Batman's current state."""
    x: int
    y: int
    prev_x: Optional[int] = None
    prev_y: Optional[int] = None
    turn: int = 0


@dataclass
class Environment:
    """Game environment."""
    width: int
    height: int
    max_jumps: int
    start_x: int
    start_y: int
    bomb_x: int
    bomb_y: int


@dataclass
class Control:
    """Player's output - next position to jump to."""
    x: int
    y: int

    @staticmethod
    def parse(line: str) -> 'Control':
        parts = line.strip().split()
        return Control(int(parts[0]), int(parts[1]))


def euclidean_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculate Euclidean distance between two points."""
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx * dx + dy * dy)


def get_direction(prev_x: int, prev_y: int, curr_x: int, curr_y: int,
                  bomb_x: int, bomb_y: int) -> str:
    """Determine WARMER/COLDER/SAME based on distances."""
    prev_dist = euclidean_distance(prev_x, prev_y, bomb_x, bomb_y)
    curr_dist = euclidean_distance(curr_x, curr_y, bomb_x, bomb_y)

    # Use small epsilon for floating point comparison
    eps = 1e-9
    if curr_dist < prev_dist - eps:
        return "WARMER"
    elif curr_dist > prev_dist + eps:
        return "COLDER"
    else:
        return "SAME"


class ShadowsOfTheKnight2Model(GameModel):
    """Shadows of the Knight Episode 2 game model."""

    name = "shadows_of_the_knight_2"
    description = "Shadows of the Knight Episode 2"

    def __init__(self):
        self._test_cases = load_test_cases_from_files()
        self._env: Optional[Environment] = None

    def get_test_cases(self) -> dict[str, str]:
        return {name: tc.get("name", name) for name, tc in self._test_cases.items()}

    def load_test_case(self, name: str) -> Tuple[Environment, State]:
        if name not in self._test_cases:
            raise ValueError(f"Unknown test case: {name}. Available: {list(self._test_cases.keys())}")

        tc = self._test_cases[name]

        bomb_x = tc.get("bomb_x")
        bomb_y = tc.get("bomb_y")

        if bomb_x is None or bomb_y is None:
            raise ValueError(f"Test case '{name}' has unknown bomb position (was TIMEOUT/FAILURE in CodinGame)")

        env = Environment(
            width=tc["width"],
            height=tc["height"],
            max_jumps=tc["max_jumps"],
            start_x=tc["start_x"],
            start_y=tc["start_y"],
            bomb_x=bomb_x,
            bomb_y=bomb_y
        )

        state = State(
            x=tc["start_x"],
            y=tc["start_y"],
            prev_x=None,
            prev_y=None,
            turn=0
        )

        self._env = env
        return env, state

    def format_init_input(self, env: Environment) -> List[str]:
        """Format initialization input: W H, N, X0 Y0."""
        return [
            f"{env.width} {env.height}",
            str(env.max_jumps),
            f"{env.start_x} {env.start_y}"
        ]

    def format_turn_input(self, state: State) -> str:
        """Format turn input based on state and stored environment."""
        if state.prev_x is None:
            return "UNKNOWN"
        if self._env is None:
            return "UNKNOWN"
        return get_direction(state.prev_x, state.prev_y, state.x, state.y,
                           self._env.bomb_x, self._env.bomb_y)

    def parse_output(self, line: str) -> Control:
        return Control.parse(line)

    def simulate(self, state: State, control: Control, env: Environment) -> Tuple[State, SimResult]:
        """Simulate one turn - Batman jumps to new position."""
        new_x = control.x
        new_y = control.y
        new_turn = state.turn + 1

        # Validate coordinates
        if new_x < 0 or new_x >= env.width:
            return state, SimResult('failure', f"x={new_x} out of bounds [0, {env.width})")
        if new_y < 0 or new_y >= env.height:
            return state, SimResult('failure', f"y={new_y} out of bounds [0, {env.height})")

        # Check if bomb found
        if new_x == env.bomb_x and new_y == env.bomb_y:
            new_state = State(
                x=new_x, y=new_y,
                prev_x=state.x, prev_y=state.y,
                turn=new_turn
            )
            return new_state, SimResult('success')

        # Check if out of jumps
        if new_turn >= env.max_jumps:
            new_state = State(
                x=new_x, y=new_y,
                prev_x=state.x, prev_y=state.y,
                turn=new_turn
            )
            return new_state, SimResult('failure', f"ran out of jumps ({new_turn}/{env.max_jumps})")

        # Continue game
        new_state = State(
            x=new_x, y=new_y,
            prev_x=state.x, prev_y=state.y,
            turn=new_turn
        )
        return new_state, SimResult('running')

    def format_result(self, state: State) -> str:
        return f"pos=({state.x}, {state.y}), turn={state.turn}"

    def get_traces_dir(self):
        return TRACES_DIR

    def compare_state(self, state: State, expected: dict) -> List[str]:
        """Compare state with expected trace entry."""
        mismatches = []

        exp_pos = expected.get("pos", [])
        if exp_pos:
            actual = [state.x, state.y]
            if actual != exp_pos:
                mismatches.append(f"pos: got {actual}, expected {exp_pos}")

        return mismatches
