import copy
from typing import Optional
from random import Random

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


@dataclass
class Type:
    id: int
    name: str
    double_damage_from: list[int] = field(default_factory=set)
    double_damage_to: list[int] = field(default_factory=set)
    half_damage_from: list[int] = field(default_factory=set)
    half_damage_to: list[int] = field(default_factory=set)
    no_damage_from: list[int] = field(default_factory=set)
    no_damage_to: list[int] = field(default_factory=set)


@dataclass
class Move:
    id: int
    name: str
    power: int
    type_id: int


@dataclass
class Stats:
    hp: int = 0
    attack: int = 0
    defense: int = 0
    spattack: int = 0
    spdefense: int = 0
    speed: int = 0

    @classmethod
    def create_random_ivs(cls, random: Random):
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
    type_ids: list[int]
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
class Types(YAMLWizard):
    types: list[Type]

    @classmethod
    def load(cls):
        return Types.from_yaml_file(f"data/db/types.yml")

    def find_by_name(self, name: str):
        for type in self.types:
            if type.name == name:
                return type

    def find_by_id(self, id: int):
        for type in self.types:
            if type.id == id:
                return type


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

    def create(self, random: Random, name=None, id=None, level=0) -> Pokemon:
        pokemon = None
        if id is not None:
            pokemon = self.find_by_id(id)
        elif name is not None:
            pokemon = self.find_by_name(name)
        if pokemon is None:
            raise Exception(f"Pokemon name {name} or id {id} not found")
        instance = copy.copy(self.find_by_name(name))
        instance.evs = Stats()
        instance.ivs = Stats.create_random_ivs(random)
        instance.level = level
        instance.current_hp = instance.max_hp
        return instance
