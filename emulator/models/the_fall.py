"""The Fall Episode 3 game model plugin."""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional, Dict

from .base import GameModel, SimResult


TESTS_DIR = Path(__file__).parent.parent / "tests" / "the-fall-3"
TRACES_DIR = Path(__file__).parent.parent / "traces" / "the-fall-3"


# Room definitions: maps (entry_direction) -> exit_direction
# Entry: TOP, LEFT, RIGHT
# Exit: BOTTOM, LEFT, RIGHT, None (blocked)
ROOM_TYPES: Dict[int, Dict[str, Optional[Tuple[int, int, str]]]] = {
    # Type 0: blocked
    0: {"TOP": None, "LEFT": None, "RIGHT": None},
    # Type 1: cross - all pass through to bottom
    1: {"TOP": (0, 1, "TOP"), "LEFT": (0, 1, "TOP"), "RIGHT": (0, 1, "TOP")},
    # Type 2: horizontal only
    2: {"TOP": None, "LEFT": (1, 0, "LEFT"), "RIGHT": (-1, 0, "RIGHT")},
    # Type 3: vertical only
    3: {"TOP": (0, 1, "TOP"), "LEFT": None, "RIGHT": None},
    # Type 4: top goes left, left blocked, right goes down
    4: {"TOP": (-1, 0, "RIGHT"), "LEFT": None, "RIGHT": (0, 1, "TOP")},
    # Type 5: top goes right, left goes down, right blocked
    5: {"TOP": (1, 0, "LEFT"), "LEFT": (0, 1, "TOP"), "RIGHT": None},
    # Type 6: horizontal only (was labeled as type 2 in docs)
    6: {"TOP": None, "LEFT": (1, 0, "LEFT"), "RIGHT": (-1, 0, "RIGHT")},
    # Type 7: top goes down, right goes down
    7: {"TOP": (0, 1, "TOP"), "LEFT": None, "RIGHT": (0, 1, "TOP")},
    # Type 8: T with stem down - all entries go down
    8: {"TOP": (0, 1, "TOP"), "LEFT": (0, 1, "TOP"), "RIGHT": (0, 1, "TOP")},
    # Type 9: top goes down, left goes down
    9: {"TOP": (0, 1, "TOP"), "LEFT": (0, 1, "TOP"), "RIGHT": None},
    # Type 10: top goes left
    10: {"TOP": (-1, 0, "RIGHT"), "LEFT": None, "RIGHT": None},
    # Type 11: top goes right
    11: {"TOP": (1, 0, "LEFT"), "LEFT": None, "RIGHT": None},
    # Type 12: right goes down
    12: {"TOP": None, "LEFT": None, "RIGHT": (0, 1, "TOP")},
    # Type 13: left goes down
    13: {"TOP": None, "LEFT": (0, 1, "TOP"), "RIGHT": None},
}

# Rotation mappings: type -> rotated_type (clockwise)
ROTATE_RIGHT: Dict[int, int] = {
    0: 0, 1: 1,  # 0 and 1 don't change
    2: 3, 3: 2,  # 2 <-> 3
    4: 5, 5: 4,  # 4 <-> 5
    6: 7, 7: 8, 8: 9, 9: 6,  # 6->7->8->9->6
    10: 11, 11: 12, 12: 13, 13: 10,  # 10->11->12->13->10
}

ROTATE_LEFT: Dict[int, int] = {v: k for k, v in ROTATE_RIGHT.items() if k != v}
# Fix cycles
ROTATE_LEFT.update({0: 0, 1: 1, 2: 3, 3: 2, 4: 5, 5: 4})
ROTATE_LEFT.update({6: 9, 7: 6, 8: 7, 9: 8})
ROTATE_LEFT.update({10: 13, 11: 10, 12: 11, 13: 12})


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
class Entity:
    """Position and entry direction of Indy or a rock."""
    x: int
    y: int
    entry: str  # TOP, LEFT, RIGHT


@dataclass
class State:
    """Current game state."""
    grid: List[List[int]]  # Current room types (positive = mutable)
    locked: List[List[bool]]  # True if room is locked
    indy: Entity
    rocks: List[Entity] = field(default_factory=list)
    turn: int = 0


@dataclass
class Environment:
    """Game environment (static)."""
    width: int
    height: int
    exit_x: int
    initial_grid: List[List[int]]
    locked: List[List[bool]]


@dataclass
class Control:
    """Player's output command."""
    action: str  # WAIT, LEFT, RIGHT
    x: int = -1
    y: int = -1

    @staticmethod
    def parse(line: str) -> 'Control':
        parts = line.strip().upper().split()
        if parts[0] == "WAIT":
            return Control(action="WAIT")
        elif len(parts) >= 3:
            x, y = int(parts[0]), int(parts[1])
            action = parts[2]
            if action not in ("LEFT", "RIGHT"):
                raise ValueError(f"Invalid action: {action}")
            return Control(action=action, x=x, y=y)
        else:
            raise ValueError(f"Invalid command: {line}")


class TheFallModel(GameModel):
    """The Fall Episode 3 game model."""

    name = "the_fall"
    description = "The Fall Episode 3"

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
        exit_x = tc["exit_x"]
        grid_data = tc["grid"]

        # Parse grid
        initial_grid = []
        locked = []
        for row_data in grid_data:
            row = []
            lock_row = []
            for val in row_data:
                if val < 0:
                    row.append(abs(val))
                    lock_row.append(True)
                else:
                    row.append(val)
                    lock_row.append(False)
            initial_grid.append(row)
            locked.append(lock_row)

        # Initial Indy position
        indy_data = tc.get("indy", {"x": 0, "y": 0, "entry": "TOP"})
        indy = Entity(indy_data["x"], indy_data["y"], indy_data["entry"])

        # Initial rocks
        rocks = []
        for r in tc.get("rocks", []):
            rocks.append(Entity(r["x"], r["y"], r["entry"]))

        # Scheduled rocks (appear on specific turns)
        scheduled_rocks = tc.get("scheduled_rocks", [])

        env = Environment(
            width=width,
            height=height,
            exit_x=exit_x,
            initial_grid=initial_grid,
            locked=locked
        )

        state = State(
            grid=[row[:] for row in initial_grid],
            locked=[row[:] for row in locked],
            indy=indy,
            rocks=rocks,
            turn=0
        )

        # Store scheduled rocks in environment for later
        env.scheduled_rocks = scheduled_rocks

        return env, state

    def format_init_input(self, env: Environment) -> List[str]:
        """Format initialization input."""
        lines = [f"{env.width} {env.height}"]
        for y, row in enumerate(env.initial_grid):
            row_str = []
            for x, val in enumerate(row):
                if env.locked[y][x]:
                    row_str.append(str(-val))
                else:
                    row_str.append(str(val))
            lines.append(" ".join(row_str))
        lines.append(str(env.exit_x))
        return lines

    def format_turn_input(self, state: State) -> str:
        """Format turn input: Indy position, then rocks."""
        lines = [f"{state.indy.x} {state.indy.y} {state.indy.entry}"]
        lines.append(str(len(state.rocks)))
        for rock in state.rocks:
            lines.append(f"{rock.x} {rock.y} {rock.entry}")
        return "\n".join(lines)

    def parse_output(self, line: str) -> Control:
        return Control.parse(line)

    def _move_entity(self, entity: Entity, grid: List[List[int]], width: int, height: int) -> Optional[Entity]:
        """Move an entity through the grid. Returns None if blocked/exits."""
        room_type = grid[entity.y][entity.x]
        if room_type not in ROOM_TYPES:
            return None

        movement = ROOM_TYPES[room_type].get(entity.entry)
        if movement is None:
            return None

        dx, dy, new_entry = movement
        new_x = entity.x + dx
        new_y = entity.y + dy

        # Check bounds
        if new_x < 0 or new_x >= width or new_y < 0 or new_y >= height:
            return None  # Exits grid

        # Check if destination room accepts the entry direction
        dest_room_type = grid[new_y][new_x]
        if dest_room_type not in ROOM_TYPES:
            return None  # Invalid room
        dest_movement = ROOM_TYPES[dest_room_type].get(new_entry)
        if dest_movement is None:
            return None  # Destination room doesn't accept this entry

        return Entity(new_x, new_y, new_entry)

    def simulate(self, state: State, control: Control, env: Environment) -> Tuple[State, SimResult]:
        """Simulate one turn."""
        new_grid = [row[:] for row in state.grid]

        # Apply rotation if requested
        if control.action in ("LEFT", "RIGHT"):
            x, y = control.x, control.y

            # Validation
            if x < 0 or x >= env.width or y < 0 or y >= env.height:
                return state, SimResult('failure', f"Position ({x},{y}) out of bounds")

            if state.locked[y][x]:
                return state, SimResult('failure', f"Room ({x},{y}) is locked")

            # Can't rotate room with Indy
            if state.indy.x == x and state.indy.y == y:
                return state, SimResult('failure', f"Cannot rotate room with Indy")

            # Can't rotate room with rock
            for rock in state.rocks:
                if rock.x == x and rock.y == y:
                    return state, SimResult('failure', f"Cannot rotate room with rock")

            # Apply rotation
            current_type = new_grid[y][x]
            if control.action == "RIGHT":
                new_grid[y][x] = ROTATE_RIGHT.get(current_type, current_type)
            else:
                new_grid[y][x] = ROTATE_LEFT.get(current_type, current_type)

        # Move Indy
        new_indy = self._move_entity(state.indy, new_grid, env.width, env.height)
        if new_indy is None:
            return state, SimResult('failure', f"Indy blocked at ({state.indy.x},{state.indy.y})")

        # Check if Indy reached exit
        if new_indy.y >= env.height - 1 and new_indy.y == env.height - 1:
            # Check next move would go to exit
            room_type = new_grid[new_indy.y][new_indy.x]
            movement = ROOM_TYPES.get(room_type, {}).get(new_indy.entry)
            if movement:
                dx, dy, _ = movement
                exit_y = new_indy.y + dy
                exit_x = new_indy.x + dx
                if exit_y >= env.height and exit_x == env.exit_x:
                    return State(
                        grid=new_grid,
                        locked=state.locked,
                        indy=new_indy,
                        rocks=[],
                        turn=state.turn + 1
                    ), SimResult('success')

        # Move rocks
        new_rocks = []
        destroyed_positions = set()

        for rock in state.rocks:
            new_rock = self._move_entity(rock, new_grid, env.width, env.height)
            if new_rock is not None:
                new_rocks.append(new_rock)

        # Add scheduled rocks for this turn
        if hasattr(env, 'scheduled_rocks'):
            for sr in env.scheduled_rocks:
                if sr.get("turn") == state.turn + 1:
                    new_rocks.append(Entity(sr["x"], sr["y"], sr["entry"]))

        # Check rock collisions (rocks at same position destroy each other)
        rock_positions = {}
        for i, rock in enumerate(new_rocks):
            pos = (rock.x, rock.y)
            if pos in rock_positions:
                destroyed_positions.add(pos)
            else:
                rock_positions[pos] = i

        # Remove destroyed rocks
        new_rocks = [r for r in new_rocks if (r.x, r.y) not in destroyed_positions]

        # Check if Indy collides with any rock
        for rock in new_rocks:
            if rock.x == new_indy.x and rock.y == new_indy.y:
                # Return state with updated positions for the collision frame
                collision_state = State(
                    grid=new_grid,
                    locked=state.locked,
                    indy=new_indy,
                    rocks=new_rocks,
                    turn=state.turn + 1
                )
                return collision_state, SimResult('failure', f"Indy hit rock at ({rock.x},{rock.y})")

        new_state = State(
            grid=new_grid,
            locked=state.locked,
            indy=new_indy,
            rocks=new_rocks,
            turn=state.turn + 1
        )

        return new_state, SimResult('running')

    def format_result(self, state: State) -> str:
        rocks_str = ", ".join(f"({r.x},{r.y},{r.entry})" for r in state.rocks)
        return f"Indy@({state.indy.x},{state.indy.y},{state.indy.entry}) rocks=[{rocks_str}]"

    def get_traces_dir(self):
        return TRACES_DIR

    def compare_state(self, state: State, expected: dict) -> List[str]:
        """Compare state with expected trace entry."""
        mismatches = []

        exp_indy = expected.get("indy", [])
        if exp_indy:
            actual_indy = [state.indy.x, state.indy.y, state.indy.entry]
            if actual_indy != exp_indy:
                mismatches.append(f"indy: got {actual_indy}, expected {exp_indy}")

        exp_rocks = expected.get("rocks", [])
        actual_rocks = sorted([[r.x, r.y, r.entry] for r in state.rocks])
        exp_rocks_sorted = sorted(exp_rocks)
        if actual_rocks != exp_rocks_sorted:
            mismatches.append(f"rocks: got {actual_rocks}, expected {exp_rocks_sorted}")

        return mismatches
