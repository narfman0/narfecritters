from enum import Enum
from typing import Optional
from dataclasses import dataclass, field

from dataclass_wizard import YAMLWizard


class MoveTarget(Enum):
    SPECIFIC_MOVE = 1
    SELECTED_CRITTERS_ME_FIRST = 2
    ALLY = 3
    USERS_FIELD = 4
    USER_OR_ALLY = 5
    OPPONENTS_FIELD = 6
    USER = 7
    RANDOM_OPPONENT = 8
    ALL_OTHER_CRITTERS = 9
    SELECTED_CRITTERS = 10
    ALL_OPPONENTS = 11
    ENTIRE_FIELD = 12
    USER_AND_ALLIES = 13
    ALL_CRITTERS = 14
    ALL_ALLIES = 15
    FAINTING_CRITTERS = 16


class MoveCategory(Enum):
    DAMAGE = 0
    AILMENT = 1
    NET_GOOD_STATS = 2
    HEAL = 3
    DAMAGE_AILMENT = 4
    SWAGGER = 5
    DAMAGE_LOWER = 6
    DAMAGE_RAISE = 7
    DAMAGE_HEAL = 8
    OHKO = 9
    WHOLE_FIELD_EFFECT = 10
    FIELD_EFFECT = 11
    FORCE_SWITCH = 12
    UNIQUE = 13


@dataclass
class StatChange:
    amount: int
    name: str


@dataclass
class Move:
    id: int
    name: str
    type_id: int
    target: MoveTarget
    crit_rate: int
    flinch_chance: int
    healing: int
    stat_chance: int
    category: MoveCategory = MoveCategory.DAMAGE
    power: Optional[int] = None
    stat_changes: list[StatChange] = field(default_factory=list)

    @property
    def name_pretty(self):
        return self.name.replace("-", " ").capitalize()


@dataclass
class Moves(YAMLWizard):
    moves: list[Move]

    @classmethod
    def load(cls):
        return Moves.from_yaml_file(f"data/db/moves.yml")

    def find_by_name(self, name: str):
        for move in self.moves:
            if move.name == name:
                return move

    def find_by_id(self, id: int):
        for move in self.moves:
            if move.id == id:
                return move
