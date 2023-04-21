import unittest

from pokeclone.db.models import *
from pokeclone.world import World


class TestPokedex(unittest.TestCase):
    def test_attack(self):
        pokedex = Pokedex.load(yaml_path="tests/fixtures/pokemon.yml")
        scratch = Move(id=1, name="scratch", power=35, type=Type.NORMAL)
        bulbasaur = pokedex.create(name="bulbasaur", level=5)
        charmander = pokedex.create(name="charmander", level=5)
        self.assertEqual(5, World.attack(charmander, bulbasaur, scratch))
