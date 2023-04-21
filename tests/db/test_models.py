import unittest

from pokeclone.db.models import Move, Pokedex


class TestPokedox(unittest.TestCase):
    def test_load(self):
        pokedex = Pokedex.load()
        self.assertTrue(len(pokedex.pokemon) > 1)

    def test_attack(self):
        pokedex = Pokedex.load()
        bulbasaur = pokedex.create("bulbasaur", 5)
        charmander = pokedex.create("charmander", 5)
        self.assertNotEqual(charmander.id, bulbasaur.id)
