from random import Random
import unittest

from narfecritters.models import *
from narfecritters.game.move_damage import calculate_move_damage


class TestMoveDamage(unittest.TestCase):
    def test_calculate_move_damage(self):
        random = Random(x=12345)
        encyclopedia = Encyclopedia.load()
        moves = Moves.load()
        critter2 = encyclopedia.create(random, moves, id=1, level=5)
        critter1 = encyclopedia.create(random, moves, id=4, level=5)
        c1stages = EncounterStages()
        c2stages = EncounterStages()
        scratch = moves.find_by_name("scratch")
        ember = moves.find_by_name("ember")

        self.assertEqual(
            4,
            calculate_move_damage(
                critter1,
                critter2,
                c1stages,
                c2stages,
                scratch,
                random,
            ).damage,
        )
        self.assertEqual(
            14,
            calculate_move_damage(
                critter1, critter2, c1stages, c2stages, ember, random
            ).damage,
        )
