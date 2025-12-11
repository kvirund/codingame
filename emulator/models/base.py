"""Base classes for game model plugins."""
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Tuple, Optional


@dataclass
class SimResult:
    """Result of a simulation step."""
    status: str  # 'running', 'success', 'failure'
    reason: Optional[str] = None


class GameModel(ABC):
    """Base class for game model plugins."""

    name: str  # e.g. "mars_lander"
    description: str  # e.g. "Mars Lander Episode 3"

    @abstractmethod
    def get_test_cases(self) -> dict[str, str]:
        """Return {test_name: description}."""
        pass

    @abstractmethod
    def load_test_case(self, name: str) -> Tuple[Any, Any]:
        """Returns (environment, initial_state)."""
        pass

    @abstractmethod
    def format_init_input(self, env: Any) -> List[str]:
        """Lines to send before game loop (e.g. surface points)."""
        pass

    @abstractmethod
    def format_turn_input(self, state: Any) -> str:
        """Single line of state sent each turn."""
        pass

    @abstractmethod
    def parse_output(self, line: str) -> Any:
        """Parse program's output into control object."""
        pass

    @abstractmethod
    def simulate(self, state: Any, control: Any, env: Any) -> Tuple[Any, SimResult]:
        """One simulation step. Returns (new_state, result)."""
        pass

    def format_result(self, state: Any) -> str:
        """Format final state for display."""
        return str(state)

    # Trace support methods (optional, override in subclass)

    def get_traces_dir(self) -> Optional[Path]:
        """Return traces directory for this model, or None if not supported."""
        return None

    def load_trace(self, name: str) -> Optional[dict]:
        """Load trace file if exists."""
        traces_dir = self.get_traces_dir()
        if not traces_dir:
            return None
        trace_file = traces_dir / f"{name}.json"
        if trace_file.exists():
            with open(trace_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def list_traces(self) -> List[str]:
        """List available trace names."""
        traces_dir = self.get_traces_dir()
        if not traces_dir or not traces_dir.exists():
            return []
        return sorted([f.stem for f in traces_dir.glob("*.json")])

    def compare_state(self, state: Any, expected: dict) -> List[str]:
        """Compare state with expected trace entry. Return list of mismatches."""
        return []  # Override in subclass for actual comparison

    def get_required_actions(self, state: Any, player_id: int = 0) -> int:
        """Return number of actions expected from player each turn. Default 1."""
        return 1
