from random import Random

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard

from narfecritters.models.areas import *
from narfecritters.models.critters import *
from narfecritters.models.moves import *
from narfecritters.models.npcs import *
from narfecritters.models.stats import *
from narfecritters.models.types import *


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
