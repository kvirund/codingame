"""Mars Lander game model plugin."""
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from .base import GameModel, SimResult


GRAVITY = 3.711
MAX_X = 7000
MAX_Y = 3000
MAX_ANGLE_CHANGE = 15
MAX_POWER_CHANGE = 1
MAX_ANGLE = 90
MIN_ANGLE = -90
MAX_POWER = 4
MIN_POWER = 0

TESTS_DIR = Path(__file__).parent.parent / "tests" / "mars_lander"


def load_test_cases_from_files() -> dict:
    """Load all test cases from JSON files in tests/mars_lander/."""
    test_cases = {}
    if not TESTS_DIR.exists():
        return test_cases

    for json_file in sorted(TESTS_DIR.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert JSON format to internal format
            name = json_file.stem  # e.g. "test_case_03"
            lz = data["landingZone"]
            init = data["initial"]

            test_cases[name] = {
                "name": data.get("name", name),
                "surface": data["surface"],
                "landing_zone": (lz["x1"], lz["x2"], lz["y"]),
                "initial": (init["x"], init["y"], init["hSpeed"], init["vSpeed"],
                           init["fuel"], init["rotate"], init["power"])
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load {json_file}: {e}")

    return test_cases


@dataclass
class State:
    x: int
    y: int
    hSpeed: int
    vSpeed: int
    fuel: int
    rotate: int
    power: int

    def to_input_line(self) -> str:
        return f"{self.x} {self.y} {self.hSpeed} {self.vSpeed} {self.fuel} {self.rotate} {self.power}"


@dataclass
class FloatState:
    """Internal state with floating point precision."""
    x: float
    y: float
    hSpeed: float
    vSpeed: float
    fuel: int
    rotate: int
    power: int

    def to_int_state(self) -> State:
        return State(
            x=round_half_away(self.x),
            y=round_half_away(self.y),
            hSpeed=round_half_away(self.hSpeed),
            vSpeed=round_half_away(self.vSpeed),
            fuel=self.fuel,
            rotate=self.rotate,
            power=self.power
        )

    @staticmethod
    def from_state(s: State) -> 'FloatState':
        return FloatState(
            x=float(s.x), y=float(s.y),
            hSpeed=float(s.hSpeed), vSpeed=float(s.vSpeed),
            fuel=s.fuel, rotate=s.rotate, power=s.power
        )


@dataclass
class Control:
    rotate: int
    power: int

    @staticmethod
    def parse(line: str) -> 'Control':
        parts = line.strip().split()
        return Control(int(parts[0]), int(parts[1]))


@dataclass
class Point:
    x: float
    y: float


@dataclass
class LandingZone:
    x1: int
    x2: int
    y: int


@dataclass
class Surface:
    points: List[Point]
    landing_zone: LandingZone


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def round_half_away(x: float) -> int:
    """Round half away from zero."""
    if x >= 0:
        return int(math.floor(x + 0.5))
    else:
        return int(math.ceil(x - 0.5))


def apply_control_constraints(current: Control, requested: Control) -> Control:
    new_rotate = clamp(
        requested.rotate,
        current.rotate - MAX_ANGLE_CHANGE,
        current.rotate + MAX_ANGLE_CHANGE
    )
    new_power = clamp(
        requested.power,
        current.power - MAX_POWER_CHANGE,
        current.power + MAX_POWER_CHANGE
    )
    return Control(
        rotate=int(clamp(new_rotate, MIN_ANGLE, MAX_ANGLE)),
        power=int(clamp(new_power, MIN_POWER, MAX_POWER))
    )


def line_intersection(
    x1: float, y1: float, x2: float, y2: float,
    x3: float, y3: float, x4: float, y4: float
) -> Optional[Tuple[float, float]]:
    """Check if two line segments intersect."""
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def check_collision(
    surface: List[Point], x1: float, y1: float, x2: float, y2: float
) -> Optional[Tuple[float, float, int]]:
    """Check if path intersects with surface."""
    for i in range(len(surface) - 1):
        sx1, sy1 = surface[i].x, surface[i].y
        sx2, sy2 = surface[i + 1].x, surface[i + 1].y
        intersection = line_intersection(x1, y1, x2, y2, sx1, sy1, sx2, sy2)
        if intersection:
            return (intersection[0], intersection[1], i)
    return None


def get_surface_y(surface: Surface, x: float) -> float:
    """Get surface Y at position X. For caves, returns floor height within LZ."""
    lz = surface.landing_zone
    if lz.x1 <= x <= lz.x2:
        return lz.y
    for i in range(len(surface.points) - 1):
        p1, p2 = surface.points[i], surface.points[i + 1]
        if p1.x <= x <= p2.x:
            t = (x - p1.x) / (p2.x - p1.x)
            return p1.y + t * (p2.y - p1.y)
    return 0


def check_landing_conditions(state: State) -> Tuple[bool, Optional[str]]:
    if state.rotate != 0:
        return False, f"angle not vertical ({state.rotate} deg)"
    if abs(state.vSpeed) > 40:
        return False, f"vertical speed too high ({state.vSpeed} m/s)"
    if abs(state.hSpeed) > 20:
        return False, f"horizontal speed too high ({state.hSpeed} m/s)"
    return True, None


def simulate_turn(fstate: FloatState, requested: Control, surface: Surface) -> Tuple[FloatState, State, SimResult]:
    """Simulate one turn with internal float state."""
    control = apply_control_constraints(
        Control(fstate.rotate, fstate.power), requested
    )

    # Can't use thrust without fuel!
    actual_power = min(control.power, fstate.fuel)

    angle_rad = math.radians(control.rotate)
    thrust_h = -math.sin(angle_rad) * actual_power
    thrust_v = math.cos(angle_rad) * actual_power

    accel_h = thrust_h
    accel_v = thrust_v - GRAVITY

    new_h_speed = fstate.hSpeed + accel_h
    new_v_speed = fstate.vSpeed + accel_v
    new_x = fstate.x + fstate.hSpeed + 0.5 * accel_h
    new_y = fstate.y + fstate.vSpeed + 0.5 * accel_v
    new_fuel = max(0, fstate.fuel - actual_power)

    new_fstate = FloatState(
        x=new_x, y=new_y,
        hSpeed=new_h_speed, vSpeed=new_v_speed,
        fuel=new_fuel, rotate=control.rotate, power=control.power
    )
    new_state = new_fstate.to_int_state()

    # Collision detection
    old_int = State(int(fstate.x), int(fstate.y), 0, 0, 0, 0, 0)
    collision = check_collision(
        surface.points, old_int.x, old_int.y, new_state.x, new_state.y
    )
    surface_y = get_surface_y(surface, new_state.x)
    below_surface = new_state.y <= surface_y

    if collision or below_surface:
        collision_x = collision[0] if collision else new_state.x
        lz = surface.landing_zone
        if lz.x1 <= collision_x <= lz.x2:
            success, reason = check_landing_conditions(new_state)
            if success:
                return new_fstate, new_state, SimResult('success')
            return new_fstate, new_state, SimResult('failure', f"landing zone: {reason}")
        return new_fstate, new_state, SimResult('failure', "non-flat ground")

    if new_state.x < 0 or new_state.x >= MAX_X:
        return new_fstate, new_state, SimResult('failure', "horizontal bounds")
    if new_state.y < 0 or new_state.y >= MAX_Y:
        return new_fstate, new_state, SimResult('failure', "vertical bounds")

    return new_fstate, new_state, SimResult('running')


class MarsLanderModel(GameModel):
    """Mars Lander Episode 3 game model."""

    name = "mars_lander"
    description = "Mars Lander Episode 3"

    def __init__(self):
        self._float_state: Optional[FloatState] = None
        self._test_cases = load_test_cases_from_files()

    def get_test_cases(self) -> dict[str, str]:
        return {name: tc["name"] for name, tc in self._test_cases.items()}

    def load_test_case(self, name: str) -> Tuple[Surface, State]:
        if name not in self._test_cases:
            raise ValueError(f"Unknown test case: {name}. Available: {list(self._test_cases.keys())}")

        tc = self._test_cases[name]
        surface = Surface(
            points=[Point(p[0], p[1]) for p in tc["surface"]],
            landing_zone=LandingZone(*tc["landing_zone"])
        )
        init = tc["initial"]
        state = State(x=init[0], y=init[1], hSpeed=init[2], vSpeed=init[3],
                      fuel=init[4], rotate=init[5], power=init[6])
        self._float_state = FloatState.from_state(state)
        return surface, state

    def format_init_input(self, surface: Surface) -> List[str]:
        lines = [str(len(surface.points))]
        for p in surface.points:
            lines.append(f"{int(p.x)} {int(p.y)}")
        return lines

    def format_turn_input(self, state: State) -> str:
        return state.to_input_line()

    def parse_output(self, line: str) -> Control:
        return Control.parse(line)

    def simulate(self, state: State, control: Control, surface: Surface) -> Tuple[State, SimResult]:
        if self._float_state is None:
            self._float_state = FloatState.from_state(state)

        new_fstate, new_state, result = simulate_turn(self._float_state, control, surface)
        self._float_state = new_fstate
        return new_state, result

    def format_result(self, state: State) -> str:
        return f"pos=({state.x}, {state.y}), speed=({state.hSpeed}, {state.vSpeed}), angle={state.rotate}, fuel={state.fuel}"
