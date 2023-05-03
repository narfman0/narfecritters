from random import Random
import unittest

from narfecritters.db.models import *
from narfecritters.game.move_damage import calculate_move_damage


class TestMoveDamage(unittest.TestCase):
    def test_calculate_move_damage(self):
        random = Random(x=12345)
        encyclopedia = Encyclopedia.load()
        critter2 = encyclopedia.create(random, id=1, level=5)
        critter1 = encyclopedia.create(random, id=4, level=5)

        scratch = Move(id=1, name="scratch", power=35, type_id=1)
        self.assertEqual(
            4, calculate_move_damage(critter1, critter2, scratch, random).damage
        )
        ember = Move(id=2, name="ember", power=35, type_id=10)
        self.assertEqual(
            14, calculate_move_damage(critter1, critter2, ember, random).damage
        )
