import os
from typing import Optional

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard

from narfecritters.models.critters import *
from narfecritters.models.direction import *
from narfecritters.models.items import *
from narfecritters.models.moves import *
from narfecritters.models.stats import *

ACTIVE_CRITTERS_MAX = 6


@dataclass
class NPC:
    x: int = 0
    y: int = 0
    respawn_x: int = 0
    respawn_y: int = 0
    money: int = 0
    direction: Direction = Direction.DOWN
    respawn_area: Optional[str] = None
    inventory: dict[ItemType, int] = field(default_factory=dict)
    critters: list[Critter] = field(default_factory=list)
    active_critters: list[UUID] = field(default_factory=list)
    sprite: Optional[str] = "player"

    @property
    def active_critter(self):
        for active_critter_uuid in self.active_critters:
            active_critter = self.find_critter_by_uuid(active_critter_uuid)
            if not active_critter.fainted:
                return active_critter
        return None

    def add_critter(self, critter: Critter):
        self.critters.append(critter)
        if len(self.active_critters) < ACTIVE_CRITTERS_MAX:
            self.active_critters.append(critter.uuid)

    def remove_critter(self, critter: Critter):
        self.critters.remove(critter)
        self.active_critters.remove(critter.uuid)

    def find_critter_by_uuid(self, uuid):
        for critter in self.critters:
            if critter.uuid == uuid:
                return critter
        return None

    def add_item(self, item: ItemType, amount: int = 1):
        current = self.inventory.get(item, 0)
        self.inventory[item] = current + amount

    def remove_item(self, item: ItemType, amount: int = 1):
        current = self.inventory.get(item, 0)
        if current >= amount:
            self.inventory[item] = current - amount

    def has_item(self, item: ItemType, amount: int = 1):
        return self.inventory.get(item, 0) >= amount

    def get_item_count(self, item: ItemType):
        return self.inventory.get(item, 0)


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
