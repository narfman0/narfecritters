import logging

LOGGER = logging.getLogger(__name__)


from pokeclone import models

MOVE_SPEED = 5


class World:
    def __init__(self):
        self.player = models.NPC(x=10, y=10)

    def update(self, dt):
        pass
