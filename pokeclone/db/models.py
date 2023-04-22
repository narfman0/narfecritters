import copy
from enum import auto, Enum
from typing import Optional
import random

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


class Type(Enum):
    NORMAL = auto()
    FIGHTING = auto()
    FLYING = auto()
    POISON = auto()
    GROUND = auto()
    ROCK = auto()
    BUG = auto()
    GHOST = auto()
    STEEL = auto()
    FIRE = auto()
    WATER = auto()
    GRASS = auto()
    ELECTRIC = auto()
    PSYCHIC = auto()
    ICE = auto()
    DRAGON = auto()
    DARK = auto()
    FAIRY = auto()
    UNKNOWN = 10001
    SHADOW = 10002


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

    @classmethod
    def create_random_ivs(cls):
        return Stats(
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
        )


@dataclass
class Pokemon:
    id: int
    name: str
    base_stats: Stats
    types: list[Type]
    move_ids: list[int]
    ivs: Optional[Stats] = field(default=False, init=False)
    evs: Optional[Stats] = field(default=False, init=False)
    current_hp: Optional[int] = field(default=False, init=False)
    level: Optional[int] = field(default=False, init=False)

    @property
    def max_hp(self):
        numerator = 2 * self.base_stats.hp + self.ivs.hp + self.evs.hp // 4
        return (numerator * self.level) // 100 + self.level + 10

    @property
    def attack(self):
        return (
            2 * self.base_stats.attack + self.evs.attack // 4 + self.ivs.attack
        ) * self.level // 100 + 5

    @property
    def defense(self):
        return (
            2 * self.base_stats.defense + self.evs.defense // 4 + self.ivs.defense
        ) * self.level // 100 + 5

    @property
    def spattack(self):
        return (
            2 * self.base_stats.spattack + self.evs.spattack // 4 + self.ivs.spattack
        ) * self.level // 100 + 5

    @property
    def spdefense(self):
        return (
            2 * self.base_stats.spdefense + self.evs.spdefense // 4 + self.ivs.spdefense
        ) * self.level // 100 + 5

    @property
    def speed(self):
        return (
            2 * self.base_stats.speed + self.evs.speed // 4 + self.ivs.speed
        ) * self.level // 100 + 5


@dataclass
class NPC:
    x: int
    y: int
    pokemon: list[Pokemon]
    active_pokemon_index: int = 0

    @property
    def active_pokemon(self):
        return self.pokemon[self.active_pokemon_index]


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
    def load(cls, yaml_path="data/db/pokemon.yml"):
        return Pokedex.from_yaml_file(yaml_path)

    def find_by_id(self, id: int):
        for pokemon in self.pokemon:
            if pokemon.id == id:
                return pokemon

    def find_by_name(self, name):
        for pokemon in self.pokemon:
            if pokemon.name == name:
                return pokemon

    def create(self, name=None, id=None, level=0) -> Pokemon:
        pokemon = None
        if id is not None:
            pokemon = self.find_by_id(id)
        elif name is not None:
            pokemon = self.find_by_name(name)
        if pokemon is None:
            raise Exception(f"Pokemon name {name} or id {id} not found")
        instance = copy.copy(self.find_by_name(name))
        instance.evs = Stats()
        instance.ivs = Stats.create_random_ivs()
        instance.level = level
        instance.current_hp = instance.max_hp
        return instance
