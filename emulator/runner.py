"""Generic subprocess runner for game models."""
import subprocess
import sys
import threading
import queue
from typing import List, Tuple, Any, Optional

from models.base import GameModel


def readline_with_timeout(pipe, timeout_ms: int) -> Optional[str]:
    """Read a line from pipe with timeout (works on Windows)."""
    result_queue = queue.Queue()

    def reader():
        try:
            line = pipe.readline()
            result_queue.put(line)
        except Exception as e:
            result_queue.put(None)

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    thread.join(timeout=timeout_ms / 1000.0)

    if thread.is_alive():
        # Timeout - thread is still waiting for input
        return None

    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return None


def run_program(
    model: GameModel,
    program_cmd: List[str],
    test_name: str,
    max_turns: int = 500,
    verbose: bool = False,
    turn_timeout_ms: int = 150,
    debug: bool = False
) -> Tuple[str, List[Any], int]:
    """
    Run a program through the emulator via bidirectional stdio.

    Args:
        model: Game model to use
        program_cmd: Command to run the program
        test_name: Name of the test case
        max_turns: Maximum number of turns before timeout
        verbose: Print debug output
        turn_timeout_ms: Timeout per turn in milliseconds (default 150ms)
        debug: If True, continuously print stderr from the program

    Returns: (result_status, trajectory, turns_used)
    """
    env, initial_state = model.load_test_case(test_name)

    proc = subprocess.Popen(
        program_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Start stderr reader thread if debug mode
    stderr_lines = []
    def stderr_reader():
        try:
            for line in proc.stderr:
                stderr_lines.append(line)
                if debug:
                    print(f"[DBG] {line}", end='', file=sys.stderr)
        except:
            pass

    stderr_thread = threading.Thread(target=stderr_reader, daemon=True)
    stderr_thread.start()

    try:
        # Send initialization input
        for line in model.format_init_input(env):
            proc.stdin.write(line + "\n")
        proc.stdin.flush()

        state = initial_state
        trajectory = [state]

        for turn in range(max_turns):
            # Send current state (if model requires turn input)
            turn_input = model.format_turn_input(state)
            if turn_input:
                try:
                    proc.stdin.write(turn_input + "\n")
                    proc.stdin.flush()
                except OSError:
                    pass  # Process may have exited

            # Get number of expected actions
            required_actions = model.get_required_actions(state, player_id=0)

            # Get control outputs with timeout
            controls = []
            for action_idx in range(required_actions):
                control_line = readline_with_timeout(proc.stdout, turn_timeout_ms)

                if control_line is None:
                    # Timeout
                    return f'timeout: turn {turn} action {action_idx} exceeded {turn_timeout_ms}ms', trajectory, turn

                control_line = control_line.strip()
                if not control_line:
                    return 'program_error', trajectory, turn

                try:
                    control = model.parse_output(control_line)
                    control.player_id = 0  # Single player mode
                    controls.append(control)
                except (ValueError, IndexError) as e:
                    print(f"Invalid output: '{control_line}' - {e}", file=sys.stderr)
                    return 'invalid_output', trajectory, turn

                if verbose:
                    if action_idx == 0:
                        print(f"T{turn}: {model.format_result(state)} -> {control_line}")
                    else:
                        print(f"     {' ' * len(model.format_result(state))} -> {control_line}")

            # Simulate all controls at once
            state, result = model.simulate(state, controls, env)
            trajectory.append(state)

            if result.status == 'success':
                return 'success', trajectory, turn + 1
            elif result.status == 'failure':
                return f'failure: {result.reason}', trajectory, turn + 1

        return 'max_turns_exceeded', trajectory, max_turns

    finally:
        try:
            proc.stdin.close()
        except OSError:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()


def run_program_multi(
    model: GameModel,
    program_cmds: List[List[str]],
    test_name: str,
    max_turns: int = 100,
    verbose: bool = False,
    turn_timeout_ms: int = 150,
    debug: bool = False
) -> Tuple[str, List[Any], int]:
    """
    Run multiple programs (one per player) in a multi-agent game.

    Args:
        model: Game model to use
        program_cmds: List of commands for each player. If fewer than num_players,
                      last command is reused for remaining players.
        test_name: Name of the test case
        max_turns: Maximum number of turns
        verbose: Print debug output
        turn_timeout_ms: Timeout per turn in milliseconds
        debug: Print stderr from programs

    Returns: (result_status, trajectory, turns_used)
    """
    env, initial_state = model.load_test_case(test_name)

    # Determine number of players from model/env
    num_players = getattr(env, 'num_players', 2)

    # Expand program_cmds to match num_players
    while len(program_cmds) < num_players:
        program_cmds.append(program_cmds[-1])

    # Start one process per player
    procs = []
    for pid in range(num_players):
        proc = subprocess.Popen(
            program_cmds[pid],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        procs.append(proc)

        # Start stderr reader thread
        def make_stderr_reader(p, player_id):
            def reader():
                try:
                    for line in p.stderr:
                        if debug:
                            print(f"[P{player_id}] {line}", end='', file=sys.stderr)
                except:
                    pass
            return reader

        t = threading.Thread(target=make_stderr_reader(proc, pid), daemon=True)
        t.start()

    try:
        # Send initialization input to all players
        init_lines = model.format_init_input(env)
        for proc in procs:
            for line in init_lines:
                proc.stdin.write(line + "\n")
            proc.stdin.flush()

        state = initial_state
        trajectory = [state]

        for turn in range(max_turns):
            controls = []

            # Get command from each player
            for pid, proc in enumerate(procs):
                # Send turn input (with player perspective)
                turn_input = model.format_turn_input(state, player_id=pid)
                if turn_input:
                    try:
                        proc.stdin.write(turn_input + "\n")
                        proc.stdin.flush()
                    except OSError:
                        controls.append(None)
                        continue

                # Get output
                control_line = readline_with_timeout(proc.stdout, turn_timeout_ms)

                if control_line is None:
                    return f'timeout: P{pid} turn {turn} exceeded {turn_timeout_ms}ms', trajectory, turn

                control_line = control_line.strip()
                if not control_line:
                    controls.append(None)
                    continue

                try:
                    control = model.parse_output(control_line)
                    control.player_id = pid
                    controls.append(control)

                    if verbose:
                        print(f"T{turn} P{pid}: {control_line}")
                except (ValueError, IndexError) as e:
                    print(f"P{pid} Invalid output: '{control_line}' - {e}", file=sys.stderr)
                    controls.append(None)

            # Simulate all controls
            state, result = model.simulate(state, controls, env)
            trajectory.append(state)

            if verbose:
                print(f"  -> {model.format_result(state)}")

            if result.status == 'success':
                return 'success', trajectory, turn + 1
            elif result.status == 'failure':
                return f'failure: {result.reason}', trajectory, turn + 1

        return 'max_turns_exceeded', trajectory, max_turns

    finally:
        for proc in procs:
            try:
                proc.stdin.close()
            except OSError:
                pass
            proc.terminate()
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                proc.kill()


def run_replay(
    model: GameModel,
    test_name: str,
    trace: dict,
    verbose: bool = False
) -> Tuple[List[Tuple[int, List[str]]], List[Any], int]:
    """
    Replay a trace and compare emulator results with expected CG states.

    Trace format: each entry has the state AT that turn and the command
    that was executed to REACH that state (command at entry N produces state at entry N).

    For turn 0, command is null (initial state, nothing executed yet).

    Args:
        model: Game model to use
        test_name: Name of the test case
        trace: Trace data with cg_trace list
        verbose: Print debug output

    Returns: (mismatches, trajectory, turns)
        mismatches: List of (turn, [mismatch_descriptions])
    """
    env, state = model.load_test_case(test_name)
    cg_trace = trace.get("cg_trace", [])
    mismatches = []
    trajectory = [state]

    for i, entry in enumerate(cg_trace):
        turn = entry.get("turn", i)

        # Get command - this command was executed to reach THIS state
        cmd = entry.get("command")

        # If there's a command, simulate first, then compare
        if cmd is not None:
            try:
                control = model.parse_output(cmd)
                state, result = model.simulate(state, control, env)
                trajectory.append(state)

                if result.status in ('success', 'failure'):
                    # Check final state before breaking
                    diffs = model.compare_state(state, entry)
                    if diffs:
                        mismatches.append((turn, diffs))
                        if verbose:
                            print(f"T{turn}: MISMATCH - {diffs}")
                    elif verbose:
                        print(f"T{turn}: {cmd} -> OK (game ended: {result.status})")
                    break
            except (ValueError, IndexError) as e:
                if verbose:
                    print(f"T{turn}: Invalid command '{cmd}' - {e}")
                break

        # Compare current state with expected
        diffs = model.compare_state(state, entry)
        if diffs:
            mismatches.append((turn, diffs))
            if verbose:
                print(f"T{turn}: MISMATCH - {diffs}")
        elif verbose:
            if cmd:
                print(f"T{turn}: {cmd} -> OK")
            else:
                print(f"T{turn}: (initial) -> OK")

    return mismatches, trajectory, len(cg_trace)


def run_replay_multi(
    model: GameModel,
    test_name: str,
    trace: dict,
    verbose: bool = False
) -> Tuple[List[Tuple[int, List[str]]], List[Any], int]:
    """
    Replay a multi-agent trace and compare emulator results with expected CG states.

    Trace format for multi-agent:
    - "order": [0, 1, ...] - order of players
    - "cg_trace": list of entries with:
      - "turn": turn number
      - "commands": [cmd_p0, cmd_p1, ...] - commands for each player
      - other expected state data

    Args:
        model: Game model to use
        test_name: Name of the test case
        trace: Trace data with cg_trace list
        verbose: Print debug output

    Returns: (mismatches, trajectory, turns)
        mismatches: List of (turn, [mismatch_descriptions])
    """
    env, state = model.load_test_case(test_name)
    cg_trace = trace.get("cg_trace", [])
    order = trace.get("order", [0, 1])  # Default order
    mismatches = []
    trajectory = [state]

    for i, entry in enumerate(cg_trace):
        turn = entry.get("turn", i)

        # Get commands for all players
        commands = entry.get("commands", [])
        if not commands or all(c is None for c in commands):
            # No commands = initial state or no action
            diffs = model.compare_state(state, entry)
            if diffs:
                mismatches.append((turn, diffs))
                if verbose:
                    print(f"T{turn}: MISMATCH - {diffs}")
            elif verbose:
                print(f"T{turn}: (initial) -> OK")
            continue

        # Parse commands in order
        controls = []
        for pid in order:
            if pid < len(commands) and commands[pid] is not None:
                try:
                    ctrl = model.parse_output(commands[pid])
                    ctrl.player_id = pid
                    controls.append(ctrl)
                except (ValueError, IndexError) as e:
                    if verbose:
                        print(f"T{turn}: Invalid command for P{pid}: '{commands[pid]}' - {e}")
                    controls.append(None)
            else:
                controls.append(None)

        # Simulate
        try:
            state, result = model.simulate(state, controls, env)
            trajectory.append(state)
        except Exception as e:
            if verbose:
                print(f"T{turn}: Simulation error - {e}")
            break

        # Compare state
        diffs = model.compare_state(state, entry)
        if diffs:
            mismatches.append((turn, diffs))
            if verbose:
                cmd_str = ", ".join(str(c) if c else "None" for c in commands)
                print(f"T{turn}: MISMATCH - {diffs}")
        elif verbose:
            cmd_str = ", ".join(str(c) if c else "None" for c in commands)
            print(f"T{turn}: [{cmd_str}] -> OK")

        if result.status in ('success', 'failure'):
            if verbose:
                print(f"T{turn}: Game ended: {result.status}")
            break

    return mismatches, trajectory, len(cg_trace)
