from random import Random
import unittest

from narfecritters.db.models import *
from narfecritters.game.world import Encounter, World


class TestWorld(unittest.TestCase):
    def test_attack(self):
        encyclopedia = Encyclopedia.load()
        random = Random(x=12345)
        world = World(encyclopedia=encyclopedia, random=random)
        critter2 = encyclopedia.create(random, id=1, level=5)
        critter1 = encyclopedia.create(random, id=4, level=5)

        scratch = Move(id=1, name="scratch", power=35, type_id=1)
        self.assertEqual(4, world.attack(critter1, critter2, scratch))
        ember = Move(id=2, name="ember", power=35, type_id=10)
        self.assertEqual(14, world.attack(critter1, critter2, ember))

    def test_turn(self):
        random = Random(x=12345)
        encyclopedia = Encyclopedia.load()
        critter1 = encyclopedia.create(random, id=4, level=5)
        critter2 = encyclopedia.create(random, id=1, level=5)
        world = World(encyclopedia=encyclopedia, random=random)
        world.player.critters.append(critter1)
        world.encounter = Encounter(critter2)

        player_move = world.moves.find_by_id(critter1.moves[0].id)
        self.assertEqual(5, critter1.level)
        self.assertEqual(125, critter1.experience)
        world.turn_player(player_move.name)
        world.turn_enemy()
        self.assertEqual(11, critter1.current_hp)
        self.assertEqual(16, critter2.current_hp)

        world.turn_player(player_move.name)
        world.turn_player(player_move.name)
        world.turn_player(player_move.name)
        world.turn_player(player_move.name)
        self.assertEqual(0, critter2.current_hp)
        self.assertEqual(190, critter1.experience)
