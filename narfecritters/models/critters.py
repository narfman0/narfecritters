from enum import Enum, auto
from typing import Optional
from functools import lru_cache
from uuid import UUID

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard

from narfecritters.models.moves import *
from narfecritters.models.stats import *


@dataclass
class EvolutionTrigger:
    evolved_species_id: int
    min_level: Optional[int]


@dataclass
class SpeciesMove:
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
    moves: list[SpeciesMove]
    evolution_triggers: list[EvolutionTrigger]
    capture_rate: Optional[int]
    flavor_text: Optional[str]

    @property
    def name_pretty(self):
        return self.name.replace("-", " ").capitalize()

    @property
    def critter_attributes(self):
        attributes = dict(self.__dict__)
        del attributes["moves"]
        del attributes["name"]
        return attributes


@dataclass
class Critter(YAMLWizard):
    id: int
    name: str
    base_experience: int
    base_stats: Stats
    type_ids: list[int]
    moves: list[Move]
    evolution_triggers: list[EvolutionTrigger]
    capture_rate: Optional[int]
    flavor_text: Optional[str]

    uuid: UUID
    ivs: Optional[Stats] = None
    evs: Optional[Stats] = None
    current_hp: Optional[int] = None
    experience: Optional[int] = None
    ailments: set[Ailment] = field(default_factory=set)

    def heal(self):
        self.current_hp = self.max_hp
        self.ailments.clear()

    def add_current_hp(self, amount: int):
        self.current_hp = max(0, min(self.max_hp, self.current_hp + amount))

    def has_ailment(self, status: Ailment):
        return status in self.ailments

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
