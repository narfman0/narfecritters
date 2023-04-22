from random import Random
import unittest

from pokeclone.db.models import *
from pokeclone.world import World


class TestPokedex(unittest.TestCase):
    def test_attack(self):
        pokedex = Pokedex.load()
        random = Random(x=12345)
        bulbasaur = pokedex.create(random, name="bulbasaur", level=5)
        charmander = pokedex.create(random, name="charmander", level=5)

        scratch = Move(id=1, name="scratch", power=35, type_id=1)
        self.assertEqual(4, World.attack(charmander, bulbasaur, scratch, random))
        ember = Move(id=2, name="ember", power=35, type_id=10)
        self.assertEqual(14, World.attack(charmander, bulbasaur, ember, random))

    def test_turn(self):
        random = Random(x=12345)
        pokedex = Pokedex.load()
        charmander = pokedex.create(random, name="charmander", level=5)
        bulbasaur = pokedex.create(random, name="bulbasaur", level=5)
        world = World(pokedex=pokedex, random=random)
        world.player.pokemon.append(charmander)
        world.enemy = bulbasaur

        player_move = world.moves.find_by_id(charmander.moves[0].id)
        self.assertEqual(5, charmander.level)
        self.assertEqual(125, charmander.experience)
        world.turn_player(player_move.name)
        world.turn_enemy()
        self.assertEqual(11, charmander.current_hp)
        self.assertEqual(16, bulbasaur.current_hp)

        world.turn_player(player_move.name)
        world.turn_player(player_move.name)
        world.turn_player(player_move.name)
        world.turn_player(player_move.name)
        self.assertEqual(0, bulbasaur.current_hp)
        self.assertEqual(190, charmander.experience)
