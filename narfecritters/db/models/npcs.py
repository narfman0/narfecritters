import os
from typing import Optional

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard

from narfecritters.db.models.areas import *
from narfecritters.db.models.critters import *
from narfecritters.db.models.moves import *
from narfecritters.db.models.stats import *

ACTIVE_CRITTERS_MAX = 6


@dataclass
class NPC:
    x: int = 0
    y: int = 0
    respawn_x: int = 0
    respawn_y: int = 0
    respawn_area: Optional[Area] = None
    critters: list[Critter] = field(default_factory=list)
    active_critters: list[int] = field(default_factory=list)
    sprite: Optional[str] = "player"

    @property
    def active_critter(self):
        active_idx = self.active_critter_index
        if active_idx is not None:
            return self.critters[active_idx]
        return None

    @property
    def active_critter_index(self):
        for active_critter_idx in self.active_critters:
            if not self.critters[active_critter_idx].fainted:
                return active_critter_idx
        return None

    def add_critter(self, critter):
        self.critters.append(critter)
        if len(self.active_critters) < ACTIVE_CRITTERS_MAX:
            self.active_critters.append(len(self.critters) - 1)


@dataclass
class Save(YAMLWizard):
    SLOT_COUNT = 6
    players: list[NPC | None]

    def save(self):
        return self.to_yaml_file(f"data/db/save.yml")

    @classmethod
    def load(cls):
        if not os.path.exists("data/db/save.yml"):
            return Save(players=[None] * Save.SLOT_COUNT)
        return Save.from_yaml_file("data/db/save.yml")
