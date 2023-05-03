from random import Random
import unittest

from narfecritters.db.models import *
from narfecritters.game.world import Encounter, World


class TestWorld(unittest.TestCase):
    def test_debuff(self):
        random = Random(x=12345)
        world = World(random=random)
        critter2 = world.encyclopedia.create(random, id=1, level=5)
        critter1 = world.encyclopedia.create(random, id=4, level=5)
        world.player.add_critter(critter1)
        move = Move(
            id=45,
            name="growl",
            type_id=1,
            category=MoveCategory.NET_GOOD_STATS,
            stat_changes=[
                StatChange(amount=-1, name="attack", target=MoveTarget.ALL_OPPONENTS)
            ],
        )
        world.encounter = Encounter(critter2, active_critter_index=0)
        world.use_move(
            defender=critter2,
            attacker=critter1,
            information=[],
            move=move,
        )
        self.assertEqual(-1, world.encounter.enemy_stat_stages.attack)
        world.use_move(
            defender=critter1,
            attacker=critter2,
            information=[],
            move=move,
        )
        self.assertEqual(-1, world.encounter.player_stat_stages.attack)

    def test_turn(self):
        random = Random(x=12345)
        world = World(random=random)
        critter1 = world.encyclopedia.create(random, id=4, level=5)
        critter2 = world.encyclopedia.create(random, id=1, level=5)
        world.player.add_critter(critter1)
        world.encounter = Encounter(critter2, active_critter_index=0)

        player_move = world.moves.find_by_id(critter1.moves[0].id)
        self.assertEqual(5, critter1.level)
        self.assertEqual(125, critter1.experience)
        world.use_move(
            defender=critter2,
            attacker=critter1,
            information=[],
            move=player_move,
        )
        world.use_move(
            defender=critter1,
            attacker=critter2,
            information=[],
        )
        self.assertEqual(11, critter1.current_hp)
        self.assertEqual(16, critter2.current_hp)

        for x in range(4):
            world.use_move(critter1, critter2, [], player_move)
        self.assertEqual(0, critter2.current_hp)
        self.assertEqual(190, critter1.experience)

    def test_save_load(self):
        npc = NPC(x=15, y=15)
        npc_slot = 5
        saves = Save.load()
        saves.players[npc_slot] = npc
        saves.save()
        saves = Save.load()
        new_npc = saves.players[npc_slot]
        self.assertEqual(npc.x, new_npc.x)
        self.assertEqual(npc.y, new_npc.y)
        self.assertEqual(npc, new_npc)
