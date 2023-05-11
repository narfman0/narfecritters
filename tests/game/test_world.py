from random import Random
import unittest

from narfecritters.models import *
from narfecritters.game.world import Encounter, World


class TestWorld(unittest.TestCase):
    def test_debuff(self):
        random = Random(x=12345)
        world = World(random=random)
        critter2 = world.encyclopedia.create(random, id=1, level=5)
        critter1 = world.encyclopedia.create(random, id=4, level=5)
        world.player.add_critter(critter1)
        move = world.moves.find_by_name("growl")
        move.target = MoveTarget.ALL_OPPONENTS
        world.encounter = Encounter(critter2, active_player_critter=critter1)
        self.assertEqual(0, world.encounter.enemy_stat_stages.attack)
        world.use_move(
            defender=critter2,
            attacker=critter1,
            attacker_encounter_stages=world.encounter.player_stat_stages,
            defender_encounter_stages=world.encounter.enemy_stat_stages,
            information=[],
            move=move,
        )
        self.assertEqual(-1, world.encounter.enemy_stat_stages.attack)
        self.assertEqual(0, world.encounter.player_stat_stages.attack)
        world.use_move(
            defender=critter1,
            attacker=critter2,
            attacker_encounter_stages=world.encounter.enemy_stat_stages,
            defender_encounter_stages=world.encounter.player_stat_stages,
            information=[],
            move=move,
        )
        self.assertEqual(-1, world.encounter.enemy_stat_stages.attack)
        self.assertEqual(-1, world.encounter.player_stat_stages.attack)
        self.assertAlmostEqual(
            2 / 3, world.encounter.player_stat_stages.attack_multipler
        )

    def test_turn(self):
        random = Random(x=12345)
        world = World(random=random)
        critter1 = world.encyclopedia.create(random, id=4, level=5)
        critter2 = world.encyclopedia.create(random, id=1, level=5)
        world.player.add_critter(critter1)
        world.encounter = Encounter(critter2, active_player_critter=critter1)

        player_move = world.moves.find_by_id(critter1.moves[0].id)
        self.assertEqual(5, critter1.level)
        self.assertEqual(125, critter1.experience)
        world.use_move(
            defender=critter2,
            attacker=critter1,
            attacker_encounter_stages=world.encounter.player_stat_stages,
            defender_encounter_stages=world.encounter.enemy_stat_stages,
            information=[],
            move=player_move,
        )
        world.use_move(
            defender=critter1,
            attacker=critter2,
            attacker_encounter_stages=world.encounter.enemy_stat_stages,
            defender_encounter_stages=world.encounter.player_stat_stages,
            information=[],
            move=player_move,
        )
        self.assertEqual(15, critter1.current_hp)
        self.assertEqual(16, critter2.current_hp)

        for x in range(4):
            world.use_move(
                attacker=critter1,
                defender=critter2,
                attacker_encounter_stages=world.encounter.player_stat_stages,
                defender_encounter_stages=world.encounter.enemy_stat_stages,
                information=[],
                move=player_move,
            )
        self.assertEqual(0, critter2.current_hp)
        self.assertEqual(190, critter1.experience)

    def test_all_moves(self):
        world = World()
        attacker = world.encyclopedia.create(random=world.random, id=1, level=5)
        world.player.add_critter(attacker)
        for move in world.moves.moves:
            defender_encounter_stages = EncounterStages()
            attacker_encounter_stages = EncounterStages()
            defender = world.encyclopedia.create(random=world.random, id=1, level=1)
            world.encounter = Encounter(defender, active_player_critter=attacker)
            world.use_move(
                attacker,
                defender,
                attacker_encounter_stages,
                defender_encounter_stages,
                [],
                move=move,
            )

    def test_evolution(self):
        world = World()
        critter = world.encyclopedia.create(random=world.random, id=1, level=16)
        world.player.add_critter(critter)
        world.detect_and_execute_evolution([])
        self.assertEqual(2, world.player.active_critter.id)

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
