import os

from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class XYPair:
    x: int
    y: int


@dataclass
class Settings(YAMLWizard):
    window_size: XYPair = XYPair(800, 600)
    tile_size: int = 32

    @classmethod
    def load(cls, path="settings.yml"):
        if os.path.exists(path):
            return Settings.from_yaml_file(path)
        return Settings()


SETTINGS = Settings.load()
WINDOW_SIZE = (SETTINGS.window_size.x, SETTINGS.window_size.y)
TILE_SIZE = SETTINGS.tile_size
