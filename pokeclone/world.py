import logging

LOGGER = logging.getLogger(__name__)


from pokeclone import npc

MOVE_SPEED = 5


class World:
    def __init__(self):
        self.player = npc.NPC(x=10, y=10)

    def update(self, time_delta):
        pass
