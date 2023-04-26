import unittest

from narfecritters.db.models import *


class TestModels(unittest.TestCase):
    def test_encyclopedia_load(self):
        encyclopedia = Encyclopedia.load()
        self.assertTrue(len(encyclopedia.name_to_id) > 10)

    def test_level_up(self):
        random = Random(x=12345)
        encyclopedia = Encyclopedia.load()
        critter = encyclopedia.create(random, id=4, level=5)
        self.assertEqual(5, critter.level)
        self.assertEqual(10, critter.attack)
        self.assertEqual(20, critter.max_hp)
        critter.experience += 92
        self.assertEqual(6, critter.level)
        self.assertEqual(11, critter.attack)
        self.assertEqual(22, critter.max_hp)
