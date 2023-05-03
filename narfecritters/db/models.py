import copy
from enum import Enum
import os
from typing import Optional
from random import Random
from functools import lru_cache

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


ACTIVE_CRITTERS_MAX = 6


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


class MoveTarget(Enum):
    ALL_OPPONENTS = 1


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
    target: MoveTarget
    crit_rate: int = 0
    flinch_chance: int = 0
    healing: int = 0
    stat_chance: int = 0


@dataclass
class Move:
    id: int
    name: str
    type_id: int
    category: MoveCategory = MoveCategory.DAMAGE
    power: Optional[int] = None
    stat_changes: list[StatChange] = field(default_factory=list)

    @property
    def name_pretty(self):
        return self.name.replace("-", " ").capitalize()


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
class EncounterStages(Stats):
    evasion: int = 0
    accuracy: int = 0


@dataclass
class CritterMove:
    id: int
    name: str
    learn_method: str
    level_learned_at: int

    @property
    def name_pretty(self):
        return self.name.replace("-", " ").capitalize()


@dataclass
class Species(YAMLWizard):
    id: int
    name: str
    base_experience: int
    base_stats: Stats
    type_ids: list[int]
    moves: list[CritterMove]
    capture_rate: Optional[int]
    flavor_text: Optional[str]

    @property
    def name_pretty(self):
        return self.name.replace("-", " ").capitalize()


@dataclass
class Critter(Species, YAMLWizard):
    ivs: Optional[Stats] = None
    evs: Optional[Stats] = None
    current_hp: Optional[int] = None
    experience: Optional[int] = None

    def take_damage(self, damage: int):
        self.current_hp = max(0, self.current_hp - damage)

    @property
    def fainted(self):
        return self.current_hp <= 0

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
    id_to_species: dict[int, Species] = field(default_factory=dict)

    @classmethod
    def load(cls):
        return Encyclopedia.from_yaml_file("data/db/encyclopedia.yml")

    def find_by_id(self, id: int):
        if id not in self.id_to_species:
            self.id_to_species[id] = Species.from_yaml_file(f"data/db/species/{id}.yml")
        return self.id_to_species[id]

    def find_by_name(self, name):
        return self.find_by_id(self.name_to_id[name])

    def create(self, random: Random, name=None, id=None, level=0) -> Critter:
        species = None
        if id:
            species = self.find_by_id(id)
        elif name:
            species = self.find_by_name(name)
        if species is None:
            raise Exception(f"Species name {name} or id {id} not found")
        instance = Critter(**species.__dict__)
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
