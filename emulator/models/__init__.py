"""Model registry for game plugins."""
from .base import GameModel, SimResult
from .mars_lander import MarsLanderModel
from .shadows_of_the_knight import ShadowsOfTheKnightModel
from .there_is_no_spoon import ThereIsNoSpoonModel

MODELS = {
    "mars_lander": MarsLanderModel,
    "shadows_of_the_knight": ShadowsOfTheKnightModel,
    "there_is_no_spoon": ThereIsNoSpoonModel,
}


def get_model(name: str) -> GameModel:
    """Get a model instance by name."""
    if name not in MODELS:
        raise ValueError(f"Unknown model: {name}. Available: {list(MODELS.keys())}")
    return MODELS[name]()


def list_models() -> dict[str, str]:
    """Return {name: description} for all available models."""
    return {name: cls.description for name, cls in MODELS.items()}
