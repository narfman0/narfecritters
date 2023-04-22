from random import Random
import unittest

from pokeclone.db.models import *
from pokeclone.world import World


class TestPokedex(unittest.TestCase):
    def test_attack(self):
        pokedex = Pokedex.load(yaml_path="tests/fixtures/pokemon.yml")
        random = Random(x=12345)
        bulbasaur = pokedex.create(random, name="bulbasaur", level=5)
        charmander = pokedex.create(random, name="charmander", level=5)

        scratch = Move(id=1, name="scratch", power=35, type_id=1)
        self.assertEqual(4, World.attack(charmander, bulbasaur, scratch, random))
        ember = Move(id=2, name="ember", power=35, type_id=10)
        self.assertEqual(14, World.attack(charmander, bulbasaur, ember, random))
