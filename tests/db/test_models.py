import unittest

from pokeclone.db.models import *


class TestModels(unittest.TestCase):
    def test_pokedex_load(self):
        pokedex = Pokedex.load(yaml_path="tests/fixtures/pokemon.yml")
        self.assertTrue(len(pokedex.pokemon) > 1)

    def test_level_up(self):
        random = Random(x=12345)
        pokedex = Pokedex.load(yaml_path="tests/fixtures/pokemon.yml")
        charmander = pokedex.create(random, name="charmander", level=5)
        self.assertEqual(5, charmander.level)
        self.assertEqual(10, charmander.attack)
        self.assertEqual(20, charmander.max_hp)
        charmander.experience += 92
        self.assertEqual(6, charmander.level)
        self.assertEqual(11, charmander.attack)
        self.assertEqual(22, charmander.max_hp)
