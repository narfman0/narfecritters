import os

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


@dataclass
class XYPair:
    x: int
    y: int


def window_size_default():
    return XYPair(800, 600)


def candidate_starter_species_default():
    return [1, 4, 7, 25, 133]


@dataclass
class Settings(YAMLWizard):
    window_size: XYPair = field(default_factory=window_size_default)
    tile_size: int = 32
    candidate_starter_species: list[int] = field(
        default_factory=candidate_starter_species_default
    )
    encounter_probability: float = 0.05
    default_area: str = "overworld"

    @classmethod
    def load(cls, path="settings.yml"):
        if os.path.exists(path):
            return Settings.from_yaml_file(path)
        return Settings()


SETTINGS = Settings.load()
WINDOW_SIZE = (SETTINGS.window_size.x, SETTINGS.window_size.y)
TILE_SIZE = SETTINGS.tile_size
ENCOUNTER_PROBABILITY = SETTINGS.encounter_probability
DEFAULT_AREA = SETTINGS.default_area
