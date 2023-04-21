import logging
import random

LOGGER = logging.getLogger(__name__)


from pokeclone import models

MOVE_SPEED = 5


class World:
    def __init__(self):
        self.pokedex = models.Pokedex.load()
        self.player = models.NPC(
            x=10, y=10, pokemon=[self.pokedex.create("charmander", 5)]
        )
        self.in_encounter = False

    def create_encounter(self):
        self.in_encounter = True
        enemy_pokemon_name = random.choice(["charmander", "bulbasaur"])
        self.enemy = self.pokedex.create(
            enemy_pokemon_name, round(random.random() * 4 + 1)
        )

    def update(self, dt):
        pass
