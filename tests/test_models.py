import unittest

from pokeclone.models import attack, Move, Pokedex


class TestPokedox(unittest.TestCase):
    def test_load(self):
        pokedex = Pokedex.load()
        self.assertEqual(2, len(pokedex.pokemon))

    def test_attack(self):
        pokedex = Pokedex.load()
        scratch = Move("scratch", 35)
        bulbasaur = pokedex.create("bulbasaur", 5)
        charmander = pokedex.create("charmander", 5)
        self.assertEqual(5, attack(charmander, bulbasaur, scratch))
