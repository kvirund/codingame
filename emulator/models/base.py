"""Base classes for game model plugins."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
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
