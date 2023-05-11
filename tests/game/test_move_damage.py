from random import Random
import unittest

from narfecritters.models import *
from narfecritters.game.move_damage import calculate_move_damage


class TestMoveDamage(unittest.TestCase):
    def test_calculate_move_damage(self):
        random = Random(x=12345)
        encyclopedia = Encyclopedia.load()
        critter2 = encyclopedia.create(random, id=1, level=5)
        critter1 = encyclopedia.create(random, id=4, level=5)
        c1stages = EncounterStages()
        c2stages = EncounterStages()

        scratch = Move(
            id=1,
            name="scratch",
            power=35,
            type_id=1,
            target=MoveTarget.ALL_OPPONENTS,
            crit_rate=0,
            flinch_chance=0,
            healing=0,
            stat_chance=0,
        )
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
        ember = Move(
            id=2,
            name="ember",
            power=35,
            type_id=10,
            target=MoveTarget.ALL_OPPONENTS,
            crit_rate=0,
            flinch_chance=0,
            healing=0,
            stat_chance=0,
        )
        self.assertEqual(
            14,
            calculate_move_damage(
                critter1, critter2, c1stages, c2stages, ember, random
            ).damage,
        )
