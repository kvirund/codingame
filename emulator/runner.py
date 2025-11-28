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
    turn_timeout_ms: int = 150
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

            # Get control output with timeout
            control_line = readline_with_timeout(proc.stdout, turn_timeout_ms)

            if control_line is None:
                # Timeout
                return f'timeout: turn {turn} exceeded {turn_timeout_ms}ms', trajectory, turn

            control_line = control_line.strip()
            if not control_line:
                stderr = proc.stderr.read()
                if stderr:
                    print(f"Program stderr: {stderr}", file=sys.stderr)
                return 'program_error', trajectory, turn

            try:
                control = model.parse_output(control_line)
            except (ValueError, IndexError) as e:
                print(f"Invalid output: '{control_line}' - {e}", file=sys.stderr)
                return 'invalid_output', trajectory, turn

            if verbose:
                print(f"T{turn}: {model.format_result(state)} -> {control_line}")

            # Simulate
            state, result = model.simulate(state, control, env)
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
