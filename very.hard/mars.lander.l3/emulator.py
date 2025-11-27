"""
Mars Lander Physics Emulator
Follows the exact game protocol for testing control algorithms.

Protocol:
- Initialization: surfaceN, then surfaceN lines of "landX landY"
- Each turn: output "X Y hSpeed vSpeed fuel rotate power"
- Each turn: read "rotate power"

Physics:
- Gravity: 3.711 m/s²
- Zone: 7000m x 3000m
- Angle change limit: ±15° per turn
- Power change limit: ±1 per turn

Landing conditions:
- On flat ground
- Angle = 0°
- vSpeed ≤ 40 m/s (absolute)
- hSpeed ≤ 20 m/s (absolute)
"""

import json
import math
import sys
import subprocess
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any, TextIO

GRAVITY = 3.711
MAX_X = 7000
MAX_Y = 3000
MAX_ANGLE_CHANGE = 15
MAX_POWER_CHANGE = 1
MAX_ANGLE = 90
MIN_ANGLE = -90
MAX_POWER = 4
MIN_POWER = 0


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
        """Format state as game input line"""
        return f"{self.x} {self.y} {self.hSpeed} {self.vSpeed} {self.fuel} {self.rotate} {self.power}"


@dataclass
class FloatState:
    """Internal state with floating point precision"""
    x: float
    y: float
    hSpeed: float
    vSpeed: float
    fuel: int
    rotate: int
    power: int

    def to_int_state(self) -> State:
        """Convert to integer state for output using round half away from zero"""
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
            x=float(s.x),
            y=float(s.y),
            hSpeed=float(s.hSpeed),
            vSpeed=float(s.vSpeed),
            fuel=s.fuel,
            rotate=s.rotate,
            power=s.power
        )


@dataclass
class Control:
    rotate: int
    power: int

    @staticmethod
    def parse(line: str) -> 'Control':
        """Parse control from output line"""
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

    def to_init_lines(self) -> List[str]:
        """Format surface as initialization output"""
        lines = [str(len(self.points))]
        for p in self.points:
            lines.append(f"{int(p.x)} {int(p.y)}")
        return lines


@dataclass
class SimResult:
    status: str  # 'flying', 'landed', 'crashed'
    state: State
    reason: Optional[str] = None


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def round_half_away(x: float) -> int:
    """Round half away from zero (standard rounding, not banker's)"""
    if x >= 0:
        return int(math.floor(x + 0.5))
    else:
        return int(math.ceil(x - 0.5))


def apply_control_constraints(current: Control, requested: Control) -> Control:
    """Apply angle and power change limits"""
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


def deg_to_rad(deg: float) -> float:
    return deg * math.pi / 180


def get_surface_y_for_landing_zone(surface_obj, x: float) -> float:
    """
    Get the Y coordinate of the surface at a given X position.
    For caves: if x is within landing zone, return LZ height (floor), not roof!
    """
    # Check if within landing zone first
    lz = surface_obj.landing_zone
    if lz.x1 <= x <= lz.x2:
        return lz.y  # Return floor height for cave interiors

    # Otherwise search normally
    for i in range(len(surface_obj.points) - 1):
        p1 = surface_obj.points[i]
        p2 = surface_obj.points[i + 1]
        if p1.x <= x <= p2.x:
            t = (x - p1.x) / (p2.x - p1.x)
            return p1.y + t * (p2.y - p1.y)
    return 0


def get_surface_y(surface: List[Point], x: float) -> float:
    """Get the Y coordinate of the surface at a given X position"""
    for i in range(len(surface) - 1):
        p1 = surface[i]
        p2 = surface[i + 1]
        if p1.x <= x <= p2.x:
            t = (x - p1.x) / (p2.x - p1.x)
            return p1.y + t * (p2.y - p1.y)
    return 0


def line_intersection(
    x1: float, y1: float, x2: float, y2: float,
    x3: float, y3: float, x4: float, y4: float
) -> Optional[Tuple[float, float]]:
    """Check if two line segments intersect"""
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def check_collision(
    surface: List[Point],
    x1: float, y1: float,
    x2: float, y2: float
) -> Optional[Tuple[float, float, int]]:
    """Check if path intersects with surface"""
    for i in range(len(surface) - 1):
        sx1, sy1 = surface[i].x, surface[i].y
        sx2, sy2 = surface[i + 1].x, surface[i + 1].y

        intersection = line_intersection(x1, y1, x2, y2, sx1, sy1, sx2, sy2)
        if intersection:
            return (intersection[0], intersection[1], i)
    return None


def is_in_landing_zone(x: float, landing_zone: LandingZone) -> bool:
    return landing_zone.x1 <= x <= landing_zone.x2


def check_landing_conditions(state: State) -> Tuple[bool, Optional[str]]:
    """Check if landing conditions are met"""
    if state.rotate != 0:
        return False, f"angle not vertical ({state.rotate}°)"
    if abs(state.vSpeed) > 40:
        return False, f"vertical speed too high ({state.vSpeed} m/s)"
    if abs(state.hSpeed) > 20:
        return False, f"horizontal speed too high ({state.hSpeed} m/s)"
    return True, None


def simulate_turn_float(fstate: FloatState, requested: Control, surface: Surface,
                        use_float32: bool = False) -> Tuple[FloatState, SimResult]:
    """
    Simulate one turn keeping internal float state.
    Returns both the new float state AND the integer result for comparison.
    """
    # Apply control constraints
    control = apply_control_constraints(
        Control(fstate.rotate, fstate.power),
        requested
    )

    # Calculate thrust acceleration
    angle_rad = deg_to_rad(control.rotate)

    if use_float32:
        # Use single precision
        import numpy as np
        angle_rad = np.float32(angle_rad)
        thrust_h = np.float32(-np.sin(angle_rad) * control.power)
        thrust_v = np.float32(np.cos(angle_rad) * control.power)
        gravity = np.float32(GRAVITY)
    else:
        thrust_h = -math.sin(angle_rad) * control.power
        thrust_v = math.cos(angle_rad) * control.power
        gravity = GRAVITY

    # Total acceleration
    accel_h = thrust_h
    accel_v = thrust_v - gravity

    # Update velocities (keep as float internally)
    new_h_speed = fstate.hSpeed + accel_h
    new_v_speed = fstate.vSpeed + accel_v

    # Update position using velocity + 0.5*accel (Verlet-like)
    new_x = fstate.x + fstate.hSpeed + 0.5 * accel_h
    new_y = fstate.y + fstate.vSpeed + 0.5 * accel_v

    # Consume fuel
    new_fuel = max(0, fstate.fuel - control.power)

    # Create new float state
    new_fstate = FloatState(
        x=float(new_x),
        y=float(new_y),
        hSpeed=float(new_h_speed),
        vSpeed=float(new_v_speed),
        fuel=new_fuel,
        rotate=control.rotate,
        power=control.power
    )

    # Convert to integer state for collision detection and output
    new_state = new_fstate.to_int_state()

    # Check for collision using integer positions
    old_int = State(int(fstate.x), int(fstate.y), 0, 0, 0, 0, 0)
    collision = check_collision(
        surface.points,
        old_int.x, old_int.y,
        new_state.x, new_state.y
    )

    surface_y = get_surface_y_for_landing_zone(surface, new_state.x)
    below_surface = new_state.y <= surface_y

    if collision or below_surface:
        collision_x = collision[0] if collision else new_state.x
        if is_in_landing_zone(collision_x, surface.landing_zone):
            success, reason = check_landing_conditions(new_state)
            if success:
                return new_fstate, SimResult('landed', new_state)
            else:
                return new_fstate, SimResult('crashed', new_state, f"crashed on landing zone: {reason}")
        else:
            return new_fstate, SimResult('crashed', new_state, "crashed on non-flat ground")

    if new_state.x < 0 or new_state.x >= MAX_X:
        return new_fstate, SimResult('crashed', new_state, "out of horizontal bounds")
    if new_state.y < 0:
        return new_fstate, SimResult('crashed', new_state, "below ground")
    if new_state.y >= MAX_Y:
        return new_fstate, SimResult('crashed', new_state, "too high")

    return new_fstate, SimResult('flying', new_state)


def simulate_turn(state: State, requested: Control, surface: Surface) -> SimResult:
    """Simulate one turn of physics (original integer-based version)"""
    # Apply control constraints
    control = apply_control_constraints(
        Control(state.rotate, state.power),
        requested
    )

    # Calculate thrust acceleration
    angle_rad = deg_to_rad(control.rotate)
    thrust_h = -math.sin(angle_rad) * control.power
    thrust_v = math.cos(angle_rad) * control.power

    # Total acceleration
    accel_h = thrust_h
    accel_v = thrust_v - GRAVITY

    # Update velocities using round half away from zero
    new_h_speed = round_half_away(state.hSpeed + accel_h)
    new_v_speed = round_half_away(state.vSpeed + accel_v)

    # Update position: p_new = p + v + 0.5*a (standard kinematic equation)
    # Using Python's round() which uses banker's rounding
    new_x = round(state.x + state.hSpeed + 0.5 * accel_h)
    new_y = round(state.y + state.vSpeed + 0.5 * accel_v)

    # Consume fuel
    new_fuel = max(0, state.fuel - control.power)

    # Create new state
    new_state = State(
        x=new_x,
        y=new_y,
        hSpeed=new_h_speed,
        vSpeed=new_v_speed,
        fuel=new_fuel,
        rotate=control.rotate,
        power=control.power
    )

    # Check for collision
    collision = check_collision(
        surface.points,
        state.x, state.y,
        new_x, new_y
    )

    # Check if below surface at new position
    surface_y = get_surface_y(surface.points, new_x)
    below_surface = new_y <= surface_y

    if collision or below_surface:
        collision_x = collision[0] if collision else new_x

        if is_in_landing_zone(collision_x, surface.landing_zone):
            success, reason = check_landing_conditions(new_state)
            if success:
                return SimResult('landed', new_state)
            else:
                return SimResult('crashed', new_state, f"crashed on landing zone: {reason}")
        else:
            return SimResult('crashed', new_state, "crashed on non-flat ground")

    # Check bounds
    if new_x < 0 or new_x >= MAX_X:
        return SimResult('crashed', new_state, "out of horizontal bounds")
    if new_y < 0:
        return SimResult('crashed', new_state, "below ground")
    if new_y >= MAX_Y:
        return SimResult('crashed', new_state, "too high")

    return SimResult('flying', new_state)


class Emulator:
    """Game emulator following the exact protocol with internal float state"""

    def __init__(self, surface: Surface, initial_state: State,
                 output: TextIO = sys.stdout, input_stream: TextIO = sys.stdin):
        self.surface = surface
        self.fstate = FloatState.from_state(initial_state)  # Internal float state
        self.output = output
        self.input_stream = input_stream
        self.turn = 0

    @property
    def state(self) -> State:
        """Get current state as integers (for display)"""
        return self.fstate.to_int_state()

    def send_init(self):
        """Send initialization data (surface points)"""
        for line in self.surface.to_init_lines():
            print(line, file=self.output)
        self.output.flush()

    def send_state(self):
        """Send current state to client"""
        print(self.state.to_input_line(), file=self.output)
        self.output.flush()

    def receive_control(self) -> Control:
        """Receive control command from client"""
        line = self.input_stream.readline()
        return Control.parse(line)

    def step(self, control: Control) -> SimResult:
        """Execute one simulation step using internal float state"""
        self.fstate, result = simulate_turn_float(self.fstate, control, self.surface)
        self.turn += 1
        return result

    def run(self) -> SimResult:
        """Run the full simulation loop"""
        self.send_init()

        while True:
            self.send_state()
            control = self.receive_control()
            result = self.step(control)

            if result.status != 'flying':
                return result


def load_test_case(filepath: str) -> Tuple[Surface, State]:
    """Load test case from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)

    surface = Surface(
        points=[Point(p[0], p[1]) for p in data['surface']],
        landing_zone=LandingZone(
            data['landingZone']['x1'],
            data['landingZone']['x2'],
            data['landingZone']['y']
        )
    )

    initial = data['initial']
    state = State(
        x=initial['x'],
        y=initial['y'],
        hSpeed=initial['hSpeed'],
        vSpeed=initial['vSpeed'],
        fuel=initial['fuel'],
        rotate=initial['rotate'],
        power=initial['power']
    )

    return surface, state


def validate_float_mode(filepath: str, use_float32: bool = False) -> Tuple[int, int]:
    """Validate using internal float state (not resetting to integers each turn)"""
    with open(filepath, 'r') as f:
        data = json.load(f)

    mode = "float32" if use_float32 else "float64"
    print(f"\n=== Validating ({mode}): {data['name']} ===\n")

    surface, init_state = load_test_case(filepath)
    fstate = FloatState.from_state(init_state)
    errors = 0
    correct = 0
    trace = data['trace']

    for i, entry in enumerate(trace):
        if entry.get('result') == 'CRASH':
            print(f"Turn {entry['turn']}: CRASH")
            break

        if 'output' not in entry:
            continue

        control = Control.parse(entry['output'])
        fstate, result = simulate_turn_float(fstate, control, surface, use_float32)

        if i + 1 < len(trace) and 'state' in trace[i + 1]:
            expected = trace[i + 1]['state']
            actual = result.state

            matches = (
                actual.x == expected['x'] and
                actual.y == expected['y'] and
                actual.hSpeed == expected['hSpeed'] and
                actual.vSpeed == expected['vSpeed']
            )

            if not matches:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"Turn {entry['turn']} -> {trace[i+1]['turn']}: MISMATCH")
                    print(f"  Expected: x={expected['x']}, y={expected['y']}, "
                          f"hSpeed={expected['hSpeed']}, vSpeed={expected['vSpeed']}")
                    print(f"  Actual:   x={actual.x}, y={actual.y}, "
                          f"hSpeed={actual.hSpeed}, vSpeed={actual.vSpeed}")
                    print(f"  Float:    x={fstate.x:.2f}, y={fstate.y:.2f}, "
                          f"hSpeed={fstate.hSpeed:.2f}, vSpeed={fstate.vSpeed:.2f}")
            else:
                correct += 1

    print(f"\nResults: {correct} correct, {errors} errors out of {correct + errors} turns")
    return correct, errors


def validate_against_trace(filepath: str) -> Tuple[int, int]:
    """Validate emulator physics against recorded trace"""
    with open(filepath, 'r') as f:
        data = json.load(f)

    print(f"\n=== Validating: {data['name']} ===\n")

    surface, state = load_test_case(filepath)
    errors = 0
    correct = 0
    trace = data['trace']

    for i, entry in enumerate(trace):
        if entry.get('result') == 'CRASH':
            final = entry.get('final', {})
            print(f"Turn {entry['turn']}: CRASH")
            print(f"  Final: x={final.get('x')}, y={final.get('y')}, "
                  f"hSpeed={final.get('hSpeed')}, vSpeed={final.get('vSpeed')}")
            break

        if 'output' not in entry:
            continue

        control = Control.parse(entry['output'])
        result = simulate_turn(state, control, surface)

        # Compare with next trace entry
        if i + 1 < len(trace) and 'state' in trace[i + 1]:
            expected = trace[i + 1]['state']
            actual = result.state

            matches = (
                actual.x == expected['x'] and
                actual.y == expected['y'] and
                actual.hSpeed == expected['hSpeed'] and
                actual.vSpeed == expected['vSpeed'] and
                actual.fuel == expected['fuel'] and
                actual.rotate == expected['rotate'] and
                actual.power == expected['power']
            )

            if not matches:
                errors += 1
                print(f"Turn {entry['turn']} -> {trace[i+1]['turn']}: MISMATCH")
                print(f"  Control: rotate={control.rotate}, power={control.power}")
                print(f"  Expected: x={expected['x']}, y={expected['y']}, "
                      f"hSpeed={expected['hSpeed']}, vSpeed={expected['vSpeed']}")
                print(f"  Actual:   x={actual.x}, y={actual.y}, "
                      f"hSpeed={actual.hSpeed}, vSpeed={actual.vSpeed}")
                print(f"  Diff:     x={actual.x - expected['x']}, y={actual.y - expected['y']}, "
                      f"hSpeed={actual.hSpeed - expected['hSpeed']}, vSpeed={actual.vSpeed - expected['vSpeed']}")
            else:
                correct += 1

        # Use expected state for next iteration to isolate errors
        if i + 1 < len(trace) and 'state' in trace[i + 1]:
            expected = trace[i + 1]['state']
            state = State(
                x=expected['x'],
                y=expected['y'],
                hSpeed=expected['hSpeed'],
                vSpeed=expected['vSpeed'],
                fuel=expected['fuel'],
                rotate=expected['rotate'],
                power=expected['power']
            )
        else:
            state = result.state

    print(f"\nResults: {correct} correct, {errors} errors out of {correct + errors} turns")
    return correct, errors


def run_program(program_cmd: List[str], test_file: str, max_turns: int = 500, verbose: bool = False) -> Tuple[str, List[State], int]:
    """
    Run a program through the emulator via bidirectional stdio.

    Args:
        program_cmd: Command to run the program (e.g., ['python', 'solution.py'])
        test_file: Path to test case JSON file
        max_turns: Maximum number of turns before timeout
        verbose: Print each turn's state and control

    Returns:
        Tuple of (result_status, trajectory, turns_used)
    """
    surface, initial_state = load_test_case(test_file)

    # Start the subprocess
    proc = subprocess.Popen(
        program_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )

    try:
        # Send surface data
        proc.stdin.write(f"{len(surface.points)}\n")
        for p in surface.points:
            proc.stdin.write(f"{int(p.x)} {int(p.y)}\n")
        proc.stdin.flush()

        fstate = FloatState.from_state(initial_state)
        trajectory = [initial_state]

        for turn in range(max_turns):
            # Send current state
            state = fstate.to_int_state()
            state_line = f"{state.x} {state.y} {state.hSpeed} {state.vSpeed} {state.fuel} {state.rotate} {state.power}"
            proc.stdin.write(state_line + "\n")
            proc.stdin.flush()

            # Read control from program
            control_line = proc.stdout.readline().strip()
            if not control_line:
                # Program ended or crashed
                stderr = proc.stderr.read()
                if stderr:
                    print(f"Program stderr: {stderr}", file=sys.stderr)
                return 'program_error', trajectory, turn

            try:
                control = Control.parse(control_line)
            except (ValueError, IndexError) as e:
                print(f"Invalid control output: '{control_line}' - {e}", file=sys.stderr)
                return 'invalid_output', trajectory, turn

            if verbose:
                print(f"Turn {turn}: state=({state.x}, {state.y}, {state.hSpeed}, {state.vSpeed}) -> control=({control.rotate}, {control.power})")

            # Simulate
            fstate, result = simulate_turn_float(fstate, control, surface)
            trajectory.append(result.state)

            if result.status == 'landed':
                return 'landed', trajectory, turn + 1
            elif result.status == 'crashed':
                return f'crashed: {result.reason}', trajectory, turn + 1

        return 'timeout', trajectory, max_turns

    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=1)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Mars Lander Emulator')
    parser.add_argument('--validate', type=str, help='Validate against trace file')
    parser.add_argument('--run', type=str, help='Run emulator with test case file')
    parser.add_argument('--float', action='store_true', help='Test float mode (internal float state)')
    parser.add_argument('--float32', action='store_true', help='Test float32 mode')
    parser.add_argument('--test', type=str, nargs='+',
                        help='Test a program: --test "python solution.py" test_case.json')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    if args.test:
        # Parse --test arguments: program command(s) and test file
        # Format: --test program [args...] test_case.json
        # The last argument is always the test file
        if len(args.test) < 2:
            print("Usage: --test <program> [args...] <test_case.json>")
            sys.exit(1)

        test_file = args.test[-1]
        program_cmd = args.test[:-1]

        # If program is a single string with spaces, split it
        if len(program_cmd) == 1 and ' ' in program_cmd[0]:
            program_cmd = program_cmd[0].split()

        print(f"Testing program: {' '.join(program_cmd)}")
        print(f"Test case: {test_file}")
        print()

        result, trajectory, turns = run_program(program_cmd, test_file, verbose=args.verbose)

        print(f"\n{'='*50}")
        print(f"Result: {result}")
        print(f"Turns: {turns}")

        if trajectory:
            final = trajectory[-1]
            print(f"Final state: pos=({final.x}, {final.y}), "
                  f"speed=({final.hSpeed}, {final.vSpeed}), "
                  f"angle={final.rotate}, fuel={final.fuel}")

        if result == 'landed':
            print("\n[OK] SUCCESS!")
            sys.exit(0)
        else:
            print("\n[FAIL] FAILED")
            # Show last 5 states
            print("\nLast 5 states:")
            for i, s in enumerate(trajectory[-5:]):
                print(f"  {len(trajectory)-5+i}: pos=({s.x}, {s.y}), "
                      f"speed=({s.hSpeed}, {s.vSpeed}), "
                      f"angle={s.rotate}, power={s.power}")
            sys.exit(1)
    elif args.validate:
        validate_against_trace(args.validate)
    elif args.run:
        surface, state = load_test_case(args.run)
        emulator = Emulator(surface, state)
        result = emulator.run()
        print(f"\nResult: {result.status}", file=sys.stderr)
        if result.reason:
            print(f"Reason: {result.reason}", file=sys.stderr)
    elif args.float or args.float32:
        # Test float modes
        tc1 = 'c:\\dev\\codingame\\workbench\\test_case_01.json'
        tc2 = 'c:\\dev\\codingame\\workbench\\test_case_02.json'
        validate_float_mode(tc1, use_float32=args.float32)
        validate_float_mode(tc2, use_float32=args.float32)
    else:
        # Default: validate both test cases with all modes
        print("=" * 60)
        print("Mode 1: Integer state (reset each turn)")
        print("=" * 60)
        validate_against_trace('c:\\dev\\codingame\\workbench\\test_case_01.json')
        validate_against_trace('c:\\dev\\codingame\\workbench\\test_case_02.json')

        print("\n" + "=" * 60)
        print("Mode 2: Float64 internal state (accumulated)")
        print("=" * 60)
        validate_float_mode('c:\\dev\\codingame\\workbench\\test_case_01.json', use_float32=False)
        validate_float_mode('c:\\dev\\codingame\\workbench\\test_case_02.json', use_float32=False)


if __name__ == '__main__':
    main()
