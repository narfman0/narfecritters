import logging

LOGGER = logging.getLogger(__name__)


from pokeclone import models

MOVE_SPEED = 5


class World:
    def __init__(self):
        self.pokedex = models.Pokedex.load()
        self.player = models.NPC(
            x=10, y=10, pokemon=[self.pokedex.create("charmander", 5)]
        )

    def update(self, dt):
        pass
