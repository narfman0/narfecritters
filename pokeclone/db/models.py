import copy
from enum import Enum

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


class Type(Enum):
    NORMAL = 1
    FIRE = 2
    GRASS = 5
    POISON = 8


@dataclass
class NPC:
    x: int
    y: int
    pokemon: list


@dataclass
class Move:
    name: str
    power: int


@dataclass
class Stats:
    hp: int = 0
    attack: int = 0
    defense: int = 0
    spattack: int = 0
    spdefense: int = 0
    speed: int = 0


@dataclass
class Pokemon:
    id: int
    name: str
    current_hp: int
    base_stats: Stats
    types: list[Type]
    moves: list[Move]
    level: int = field(default=False, init=False)

    @property
    def attack(self):
        return self.base_stats.attack

    @property
    def defense(self):
        return self.base_stats.defense

    @property
    def max_hp(self):
        return self.base_stats.hp

    @property
    def spattack(self):
        return self.base_stats.spattack

    @property
    def spdefense(self):
        return self.base_stats.spdefense

    @property
    def speed(self):
        return self.base_stats.speed


@dataclass
class Pokedex(YAMLWizard):
    pokemon: list[Pokemon]

    @classmethod
    def load(cls):
        return Pokedex.from_yaml_file(f"data/pokemon.yml")

    def find(self, name):
        for pokemon in self.pokemon:
            if pokemon.name == name:
                return pokemon

    def create(self, name, level) -> Pokemon:
        instance = copy.copy(self.find(name))
        instance.level = level
        return instance
