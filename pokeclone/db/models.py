import copy
from enum import Enum

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


class Type(Enum):
    NORMAL = 1
    FIRE = 2
    WATER = 3
    ELECTRIC = 4
    GRASS = 5
    ICE = 6
    FIGHTING = 7
    POISON = 8
    GROUND = 9
    FLYING = 10
    PSYCHIC = 11
    BUG = 12
    ROCK = 13
    GHOST = 14
    DRAGON = 15
    DARK = 16
    STEEL = 17
    FAIRY = 18
    SHADOW = 19  # e.g. move 10001 :shrugs:


@dataclass
class NPC:
    x: int
    y: int
    pokemon: list


@dataclass
class Move:
    id: int
    name: str
    power: int
    type: Type


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
    base_stats: Stats
    types: list[Type]
    move_ids: list[int]
    current_hp: int = field(default=False, init=False)
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


@dataclass
class Pokedex(YAMLWizard):
    pokemon: list[Pokemon]

    @classmethod
    def load(cls):
        return Pokedex.from_yaml_file(f"data/db/pokemon.yml")

    def find(self, name):
        for pokemon in self.pokemon:
            if pokemon.name == name:
                return pokemon

    def create(self, name, level) -> Pokemon:
        instance = copy.copy(self.find(name))
        instance.level = level
        return instance
