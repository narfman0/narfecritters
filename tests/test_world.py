import unittest

from pokeclone.db.models import Move, Pokedex, Type
from pokeclone.world import World


class TestPokedox(unittest.TestCase):
    def test_attack(self):
        pokedex = Pokedex.load()
        scratch = Move(id=1, name="scratch", power=35, type=Type.NORMAL)
        bulbasaur = pokedex.create("bulbasaur", 5)
        charmander = pokedex.create("charmander", 5)
        self.assertEqual(5, World.attack(charmander, bulbasaur, scratch))
