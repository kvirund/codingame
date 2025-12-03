"""Model registry for game plugins."""
from .base import GameModel, SimResult
from .mars_lander import MarsLanderModel
from .shadows_of_the_knight_1 import ShadowsOfTheKnight1Model
from .shadows_of_the_knight_2 import ShadowsOfTheKnight2Model
from .there_is_no_spoon import ThereIsNoSpoonModel
from .the_fall import TheFallModel
from .cellularena import CellularenaModel

MODELS = {
    "mars_lander": MarsLanderModel,
    "shadows_of_the_knight_1": ShadowsOfTheKnight1Model,
    "shadows_of_the_knight_2": ShadowsOfTheKnight2Model,
    "there_is_no_spoon": ThereIsNoSpoonModel,
    "the_fall": TheFallModel,
    "cellularena": CellularenaModel,
}


def get_model(name: str) -> GameModel:
    """Get a model instance by name."""
    if name not in MODELS:
        raise ValueError(f"Unknown model: {name}. Available: {list(MODELS.keys())}")
    return MODELS[name]()


def list_models() -> dict[str, str]:
    """Return {name: description} for all available models."""
    return {name: cls.description for name, cls in MODELS.items()}
