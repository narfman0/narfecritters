import copy
from enum import Enum
from typing import Optional
from random import Random
from functools import lru_cache

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


class Area(Enum):
    OVERWORLD = 1
    POKECENTER = 2


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
class PokemonMove:
    id: int
    name: str
    learn_method: str
    level_learned_at: int


@dataclass
class Pokemon(YAMLWizard):
    id: int
    name: str
    base_experience: int
    base_stats: Stats
    type_ids: list[int]
    moves: list[PokemonMove]
    capture_rate: Optional[int]
    flavor_text: Optional[str]
    ivs: Optional[Stats] = field(default=False, init=False)
    evs: Optional[Stats] = field(default=False, init=False)
    current_hp: Optional[int] = field(default=False, init=False)
    experience: Optional[int] = field(default=False, init=False)

    def take_damage(self, damage: int):
        self.current_hp = max(0, self.current_hp - damage)

    @property
    def level(self):
        # only modeling medium-fast experience group for now
        return self.level_for_medium_fast_xp(self.experience)

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

    @classmethod
    @lru_cache(maxsize=100)
    def level_for_medium_fast_xp(cls, experience):
        candidate_level = 1
        while candidate_level**3 <= experience:
            candidate_level += 1
        return candidate_level - 1


@dataclass
class NPC:
    x: int
    y: int
    critters: list[Pokemon] = field(default_factory=list)
    active_critters_index: int = 0

    @property
    def active_critter(self):
        return self.critters[self.active_critters_index]


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
class Encyclopedia(YAMLWizard):
    name_to_id: dict[str, int]
    id_to_critter: dict[int, Pokemon] = field(default_factory=dict)

    @classmethod
    def load(cls):
        return Encyclopedia.from_yaml_file("data/db/encyclopedia.yml")

    def find_by_id(self, id: int):
        if id not in self.id_to_critter:
            self.id_to_critter[id] = Pokemon.from_yaml_file(
                f"data/db/critters/{id}.yml"
            )
        return self.id_to_critter[id]

    def find_by_name(self, name):
        return self.find_by_id(self.name_to_id[name])

    def create(self, random: Random, name=None, id=None, level=0) -> Pokemon:
        critter = None
        if id:
            critter = self.find_by_id(id)
        elif name:
            critter = self.find_by_name(name)
        if critter is None:
            raise Exception(f"Pokemon name {name} or id {id} not found")
        instance = copy.copy(critter)
        instance.evs = Stats()
        instance.ivs = Stats.create_random_ivs(random)
        # only modeling medium-fast xp group
        instance.experience = max(instance.base_experience, level**3)
        instance.current_hp = instance.max_hp
        instance.moves = [
            move
            for move in instance.moves
            if move.learn_method == "egg"
            or (
                move.learn_method == "level-up"
                and move.level_learned_at <= instance.level
            )
        ][0::4]
        return instance
