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

    def evolve(self, critter, target_species_id):
        target_species = self.find_by_id(target_species_id)
        old_moves = critter.moves
        critter.__dict__.update(target_species.__dict__)
        critter.moves = old_moves

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
        instance = Critter(uuid=uuid.uuid1(), **species.__dict__)
        instance.name = (
            instance.name.capitalize()
        )  # the species has the template name, this is a specific noun
        instance.evs = Stats()
        instance.ivs = Stats.create_random_ivs(random)
        # only modeling medium-fast xp group
        instance.experience = max(instance.base_experience, level**3)
        instance.current_hp = instance.max_hp
        available_moves = [
            move
            for move in instance.moves
            if (
                move.learn_method == "level-up"
                and move.level_learned_at <= instance.level
            )
        ]
        instance.moves = random.sample(
            [moves.find_by_id(move.id) for move in available_moves],
            k=min(4, len(available_moves)),
        )
        return instance
