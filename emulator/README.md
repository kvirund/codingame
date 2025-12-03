# CodinGame Emulator

> ⚠️ **Disclaimer**: This emulator was fully implemented by Claude Opus 4.5. The human author provided requirements and feedback on how things should work, but all code was written by the AI.

Local emulator for testing CodinGame solutions without the web interface. Supports multiple game types with accurate physics/logic simulation.

## Features

- **Fast iteration** - Test solutions locally without uploading to CodinGame
- **Accurate simulation** - Physics and game logic match CodinGame's behavior
- **Multiple languages** - Works with any compiled executable or interpreted script
- **Timeout control** - Configurable per-turn timeout (default 150ms)
- **Verbose mode** - Debug output showing each turn's input/output

## Installation

```bash
# No external dependencies required (Python 3.8+)
cd emulator
python emulator.py --list-models
```

## Quick Start

```bash
# List available games
python emulator.py --list-models

# List test cases for a game
python emulator.py --model mars_lander --list

# Test a Python solution
python emulator.py --model mars_lander --test python solution.py test_case_01

# Test a compiled C++ solution
python emulator.py --model there_is_no_spoon --test ./solution.exe test_case_11

# Verbose mode (shows each turn)
python emulator.py -v --model shadows_of_the_knight --test python sol.py test_case_08

# Custom timeout (milliseconds)
python emulator.py -t 2000 --model there_is_no_spoon --test ./solution test_case_13
```

## Supported Games

| Model | Game | Type | Difficulty |
|-------|------|------|------------|
| `mars_lander` | Mars Lander Episode 3 | Single-agent | Very Hard |
| `shadows_of_the_knight_1` | Shadows of the Knight Episode 1 | Single-agent | Medium |
| `shadows_of_the_knight_2` | Shadows of the Knight Episode 2 | Single-agent | Very Hard |
| `there_is_no_spoon` | There is no Spoon Episode 2 | Single-agent | Very Hard |
| `the_fall` | The Fall Episode 3 | Single-agent | Very Hard |
| `cellularena` | Cellularena (Winter Challenge 2024) | Multi-agent | Contest |

## Project Structure

```
emulator/
├── emulator.py              # CLI entry point
├── runner.py                # Subprocess runner with I/O handling
├── models/
│   ├── __init__.py          # Model registry
│   ├── base.py              # GameModel abstract base class
│   ├── mars_lander.py       # Mars Lander physics simulation
│   ├── shadows_of_the_knight_1.py  # Binary search (Episode 1)
│   ├── shadows_of_the_knight_2.py  # Binary search (Episode 2)
│   ├── there_is_no_spoon.py # Hashiwokakero puzzle logic
│   ├── the_fall.py          # Rotating tiles puzzle
│   └── cellularena.py       # Multi-agent organism growth game
├── tests/
│   ├── mars_lander/         # 7 test cases
│   ├── shadows-of-the-knight-1/  # Test cases
│   ├── shadows-of-the-knight-2/  # 9 test cases
│   ├── there-is-no-spoon-2/ # 14 test cases
│   ├── the-fall-3/          # Test cases
│   └── cellularena/         # Test cases
└── traces/
    └── cellularena/         # Game traces for replay validation
```

## Adding New Games

### 1. Create Game Model

Create `models/your_game.py`:

```python
from .base import GameModel, SimResult
from dataclasses import dataclass

@dataclass
class State:
    # Your game state fields
    pass

@dataclass
class Environment:
    # Static game environment (doesn't change during game)
    pass

class YourGameModel(GameModel):
    name = "your_game"
    description = "Your Game Name"

    def get_test_cases(self) -> dict[str, str]:
        """Return {test_name: description} dict"""
        pass

    def load_test_case(self, name: str) -> tuple[Environment, State]:
        """Load test case, return (env, initial_state)"""
        pass

    def format_init_input(self, env: Environment) -> list[str]:
        """Format initialization input lines for the program"""
        pass

    def format_turn_input(self, state: State) -> str:
        """Format per-turn input (empty string if single-output game)"""
        pass

    def parse_output(self, line: str) -> Control:
        """Parse program output into control object"""
        pass

    def simulate(self, state: State, control: Control, env: Environment) -> tuple[State, SimResult]:
        """Simulate one step, return (new_state, result)"""
        # result is SimResult('running'), SimResult('success'), or SimResult('failure', reason)
        pass
```

### 2. Register Model

In `models/__init__.py`:

```python
from .your_game import YourGameModel
MODELS['your_game'] = YourGameModel
```

### 3. Add Test Cases

Create `tests/your-game/test_case_01.json`:

```json
{
  "name": "Test Name",
  // ... game-specific fields
}
```

## Test Case Format

### Mars Lander

```json
{
  "name": "Cave, correct side",
  "surface": [[0, 450], [300, 750], [1000, 450], ...],
  "landingZone": {"x1": 2200, "x2": 3200, "y": 150},
  "initial": {
    "x": 6500, "y": 2600,
    "hSpeed": -20, "vSpeed": 0,
    "fuel": 1000, "rotate": 45, "power": 0
  }
}
```

### Shadows of the Knight

```json
{
  "name": "Corner bomb",
  "width": 8000,
  "height": 8000,
  "max_jumps": 31,
  "start_x": 3200,
  "start_y": 2100,
  "bomb_x": 0,
  "bomb_y": 1
}
```

### There is no Spoon

```json
{
  "name": "CG",
  "width": 5,
  "height": 14,
  "grid": [
    "..4..",
    "3.5.2",
    "..3..",
    ...
  ]
}
```

## Output Format

```
Model: mars_lander
Program: python solution.py
Test: test_case_01 (Cave, correct side)

==================================================
Result: success
Turns: 127
Final: x=2734, y=151, hSpeed=2, vSpeed=-39

[OK] SUCCESS!
```

## Multi-Agent Games

Some games (like Cellularena) support multiple agents competing against each other.

### Replay Mode

Test emulator accuracy by replaying recorded game traces:

```bash
# Replay a specific trace
python emulator.py --model cellularena --replay test_01 -v

# Test all traces for a model
python emulator.py --model cellularena --test-traces

# Test all traces for all models
python emulator.py --test-all-traces
```

### Trace Format (Multi-Agent)

```json
{
  "test_name": "test_01",
  "order": [0, 1],
  "cg_trace": [
    {
      "turn": 0,
      "commands": [null, null],
      "proteins": {"0": {"A": 10, "B": 0, "C": 0, "D": 0}, "1": {"A": 10, "B": 0, "C": 0, "D": 0}},
      "new_organs": []
    },
    {
      "turn": 1,
      "commands": ["GROW 2 2 6 BASIC", "WAIT"],
      "proteins": {"0": {"A": 9, "B": 0, "C": 0, "D": 0}, "1": {"A": 10, "B": 0, "C": 0, "D": 0}},
      "new_organs": [{"x": 2, "y": 6, "type": "BASIC", "owner": 0, "organId": 3}]
    }
  ]
}
```

## Tips

- **Test locally first** - Catch bugs without CodinGame's slow feedback loop
- **Use verbose mode** - `-v` flag shows each turn for debugging
- **Adjust timeout** - Some solutions need more time, use `-t 5000` for 5 seconds
- **Test edge cases** - The hardest test cases often reveal subtle bugs
- **Replay traces** - Validate emulator accuracy against CodinGame recordings

## License

MIT
