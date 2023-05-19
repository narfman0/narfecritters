from random import Random
import uuid

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard

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

    def evolve(self, critter: Critter, target_species_id):
        target_species = self.find_by_id(target_species_id)
        critter.__dict__.update(target_species.critter_attributes)

    def create(
        self,
        random: Random,
        moves: Moves,
        name=None,
        id=None,
        level=0,
    ) -> Critter:
        species = None
        if id:
            species = self.find_by_id(id)
        elif name:
            species = self.find_by_name(name)
        if species is None:
            raise Exception(f"Species name {name} or id {id} not found")

        ivs = Stats.create_random_ivs(random)
        available_moves = [
            move
            for move in species.moves
            if (move.learn_method == "level-up" and move.level_learned_at <= level)
        ]
        moves = random.sample(
            [moves.find_by_id(move.id) for move in available_moves],
            k=min(4, len(available_moves)),
        )
        # only modeling medium-fast xp group
        experience = max(species.base_experience, level**3)
        instance = Critter(
            uuid=uuid.uuid1(),
            moves=moves,
            ivs=ivs,
            evs=Stats(),
            experience=experience,
            **species.critter_attributes,
            name=species.name_pretty,
        )
        instance.heal()
        return instance
