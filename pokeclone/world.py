import logging
import math
from random import Random

LOGGER = logging.getLogger(__name__)


from pokeclone.db.models import *

MOVE_SPEED = 200
TYPES = Types.load()  # this is a trick for performance and usability in tests, refactor


class World:
    def __init__(self, pokedex=None, random=None):
        self.pokedex = pokedex if pokedex else Pokedex.load()
        self.moves = Moves.load()
        self.random = random if random else Random()
        self.player = NPC(x=16, y=16)
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

        if self.random.random() < 0.01:
            self.enemy = self.pokedex.create(
                self.random,
                name=self.random.choice(["charmander", "bulbasaur"]),
                level=round(self.random.random() * 3 + 1),
            )

    def end_encounter(self):
        # xp gain formula described: https://bulbapedia.bulbagarden.net/wiki/Experience
        xp_gain_level_scalar_numerator = int(
            round(math.sqrt(2 * self.enemy.level + 10))
            * (2 * self.enemy.level + 10) ** 2
        )
        xp_gain_level_scalar_denominator = int(
            round(math.sqrt(self.enemy.level + self.active_pokemon.level + 10))
            * (self.enemy.level + self.active_pokemon.level + 10) ** 2
        )
        xp_gain = (
            round(
                ((self.enemy.base_experience * self.enemy.level) / 5)
                * (xp_gain_level_scalar_numerator / xp_gain_level_scalar_denominator)
            )
            + 1
        )
        current_level = self.active_pokemon.level
        self.active_pokemon.experience += xp_gain
        LOGGER.info(f"{self.active_pokemon.name} gained {xp_gain} experience!")
        if current_level < self.active_pokemon.level:
            LOGGER.info(
                f"{self.active_pokemon.name} leveled up to {self.active_pokemon.level}"
            )
        self.enemy = None
        self.active_pokemon.current_hp = self.active_pokemon.max_hp

    def turn(self, move_name):
        self.turn_player(move_name)
        if self.enemy:
            self.turn_enemy()

    def turn_player(self, move_name):
        move = self.moves.find_by_name(move_name)
        enemy_damage = self.attack(self.active_pokemon, self.enemy, move, self.random)
        self.enemy.take_damage(enemy_damage)
        LOGGER.info(f"Enemy {self.enemy.name} took {enemy_damage} dmg from {move_name}")
        if self.enemy.current_hp <= 0:
            LOGGER.info(f"Enemy {self.active_pokemon.name} fainted!")
            self.end_encounter()

    def turn_enemy(self):
        enemy_move = self.moves.find_by_id(self.random.choice(self.enemy.moves).id)
        player_damage = self.attack(
            self.enemy, self.active_pokemon, enemy_move, self.random
        )
        self.active_pokemon.take_damage(player_damage)

        LOGGER.info(
            f"{self.active_pokemon.name} took {player_damage} dmg from {enemy_move.name}"
        )
        if self.active_pokemon.current_hp <= 0:
            LOGGER.info(f"Your {self.active_pokemon.name} fainted!")
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
                type_factor *= 0
        if type_factor > 1:
            LOGGER.info(f"{move.name} was super effective!")
        elif type_factor < 1:
            LOGGER.info(f"{move.name} was not very effective.")
        return round(
            base_damage * critical_hit_scalar * random_factor * stab * type_factor
        )

    @property
    def active_pokemon(self) -> Pokemon:
        return self.player.active_pokemon
