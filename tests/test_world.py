import unittest

from pokeclone.db.models import Move, Pokedex
from pokeclone.world import World


class TestPokedox(unittest.TestCase):
    def test_attack(self):
        pokedex = Pokedex.load()
        scratch = Move("scratch", 35)
        bulbasaur = pokedex.create("bulbasaur", 5)
        charmander = pokedex.create("charmander", 5)
        self.assertEqual(5, World.attack(charmander, bulbasaur, scratch))
