import unittest

from pokeclone.db.models import *


class TestPokedox(unittest.TestCase):
    def test_load(self):
        pokedex = Pokedex.load(yaml_path="tests/fixtures/pokemon.yml")
        self.assertTrue(len(pokedex.pokemon) > 1)
