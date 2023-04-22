import logging
import random

LOGGER = logging.getLogger(__name__)


from pokeclone.db.models import *

MOVE_SPEED = 200
TYPES = (
    Types.load()
)  # TODO this is a trick for performance and usability in tests, refactor


class World:
    def __init__(self):
        self.pokedex = Pokedex.load()
        self.moves = Moves.load()
        self.random = random.Random()
        starting_pokemon = self.pokedex.create(self.random, name="charmander", level=4)
        self.player = NPC(x=10, y=10, pokemon=[starting_pokemon])
        self.enemy = None

    def move(self, distance: int, up=False, down=False, left=False, right=False):
        if left:
            self.player.x -= distance
        elif right:
            self.player.x += distance
        if up:
            self.player.y += distance
        elif down:
            self.player.y -= distance

        if random.random() < 0.01:
            self.enemy = self.pokedex.create(
                self.random,
                name=random.choice(["charmander", "bulbasaur"]),
                level=round(random.random() * 3 + 1),
            )

    def end_encounter(self):
        self.enemy = None
        self.active_pokemon.current_hp = self.active_pokemon.max_hp
        # TODO add experience :D

    def turn(self, move_name):
        self.turn_player(move_name)
        if self.enemy:
            self.turn_enemy()

    def turn_player(self, move_name):
        move = self.moves.find_by_name(move_name)
        # TODO model active pokemon
        enemy_damage = self.attack(self.active_pokemon, self.enemy, move, self.random)
        self.enemy.current_hp -= enemy_damage
        LOGGER.info(f"Enemy {self.enemy.name} took {enemy_damage} from {move_name}")
        if self.enemy.current_hp <= 0:
            LOGGER.info(f"Enemy {self.active_pokemon.name} passed out!")
            self.end_encounter()

    def turn_enemy(self):
        enemy_move = self.moves.find_by_id(random.choice(self.enemy.move_ids))
        player_damage = self.attack(
            self.enemy, self.active_pokemon, enemy_move, self.random
        )
        self.active_pokemon.current_hp -= player_damage

        LOGGER.info(
            f"{self.active_pokemon.name} took {player_damage} from {enemy_move.name}"
        )
        if self.active_pokemon.current_hp <= 0:
            LOGGER.info(f"Your {self.active_pokemon.name} passed out!")
            self.end_encounter()

    @classmethod
    def attack(cls, attacker: Pokemon, defender: Pokemon, move: Move, random: Random):
        """Follows gen5 dmg formula as defined: https://bulbapedia.bulbagarden.net/wiki/Damage#Generation_V_onward"""
        base_damage = (
            round(
                (
                    (round((2 * attacker.level) / 5) + 2)
                    * move.power
                    * round(attacker.attack / defender.defense)
                )
                / 50
            )
            + 2
        )
        # TODO critical hits in gen5 use interesting stages, leaving at stage +0 for now
        # see https://bulbapedia.bulbagarden.net/wiki/Critical_hit for implementation details
        critical_hit_scalar = 1 if random.random() > 0.0625 else 2
        random_factor = random.random() * 0.15 + 0.85
        stab = 1.5 if move.type_id in attacker.type_ids else 1

        type_factor = 1
        for type_id in defender.type_ids:
            if move.type_id in TYPES.find_by_id(type_id).double_damage_from:
                type_factor *= 2
            if move.type_id in TYPES.find_by_id(type_id).half_damage_from:
                type_factor /= 2
            if move.type_id in TYPES.find_by_id(type_id).no_damage_from:
                type_factor *= 0  # TODO confirm this is really how this works
        return round(
            base_damage * critical_hit_scalar * random_factor * stab * type_factor
        )

    @property
    def active_pokemon(self) -> Pokemon:
        return self.player.active_pokemon
