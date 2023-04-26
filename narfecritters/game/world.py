import logging
import math
from dataclasses import dataclass
from random import Random

from pygame.math import Vector2
import pytmx

from narfecritters.ui.settings import TILE_SIZE
from narfecritters.db.models import *

LOGGER = logging.getLogger(__name__)
ENCOUNTER_PROBABILITY = 0.1
MOVE_SPEED = 200
TYPES = Types.load()  # this is a trick for performance and usability in tests, refactor


@dataclass
class Encounter:
    enemy: Pokemon


@dataclass
class MoveResult:
    encounter: bool = False
    area_change: Area = None


@dataclass
class MoveAction:
    target_x: int
    target_y: int
    running: bool


class World:
    def __init__(self, encyclopedia=None, random=None):
        self.encyclopedia = encyclopedia if encyclopedia else Encyclopedia.load()
        self.moves = Moves.load()
        self.random = random if random else Random()
        self.player = NPC(
            x=TILE_SIZE * 10 + TILE_SIZE // 2, y=TILE_SIZE * 10 + TILE_SIZE // 2
        )
        self.encounter = None
        self.area: Optional[Area] = None
        self.tmxdata: Optional[pytmx.TiledMap] = None
        self.move_action = None

    def update(self, dt: float):
        if self.move_action:
            direction = Vector2(
                self.move_action.target_x - self.player.x,
                self.move_action.target_y - self.player.y,
            )
            velocity = direction.normalize() * 2
            if self.move_action.running:
                velocity *= 2
            self.player.x += int(velocity.x)
            self.player.y += int(velocity.y)
            if (
                abs(self.player.x - self.move_action.target_x) == 0
                and abs(self.player.y - self.move_action.target_y) == 0
            ):
                self.move_action = None
                destination_area = self.detect_area_transition()
                if destination_area:
                    return MoveResult(area_change=destination_area)
                if self.detect_and_handle_random_encounter():
                    return MoveResult(encounter=True)
        return MoveResult()

    def move(
        self,
        up=False,
        down=False,
        left=False,
        right=False,
        running=False,
    ):
        if self.move_action:
            return
        target_x = self.player.x
        target_y = self.player.y
        if left:
            target_x -= TILE_SIZE
        elif right:
            target_x += TILE_SIZE
        if up:
            target_y -= TILE_SIZE
        elif down:
            target_y += TILE_SIZE

        if self.detect_and_handle_collisions(target_x, target_y):
            return
        self.move_action = MoveAction(
            running=running, target_x=target_x, target_y=target_y
        )

    def detect_and_handle_random_encounter(self):
        px = int(self.player.x // TILE_SIZE)
        py = int(self.player.y // TILE_SIZE)
        for layer in range(0, 2):
            tile_props = self.tmxdata.get_tile_properties(px, py, layer) or {}
            if (
                tile_props.get("type") == "tallgrass"
                and self.random.random() < ENCOUNTER_PROBABILITY
            ):
                self.encounter = Encounter(
                    enemy=self.encyclopedia.create(
                        self.random,
                        name=self.random.choice(
                            [
                                "charmander",
                                "bulbasaur",
                                "squirtle",
                                "eevee",
                                "pikachu",
                            ]
                        ),
                        level=round(self.random.random() * 3 + 1),
                    )
                )
                return True

    def detect_area_transition(self):
        px = int(self.player.x // TILE_SIZE)
        py = int(self.player.y // TILE_SIZE)
        for layer in range(0, 2):
            tile_props = self.tmxdata.get_tile_properties(px, py, layer) or {}
            if tile_props.get("type") == "heal":
                for pokemon in self.player.pokemon:
                    pokemon.current_hp = pokemon.max_hp
                LOGGER.info("All pokemon healed!")
            if tile_props.get("type") == "transition":
                object = self.tmxdata.get_object_by_name(
                    f"transition,{self.area.name.lower()},{px},{py}"
                )
                destination_area = Area[object.properties["Destination"].upper()]
                dest_x, dest_y = map(int, object.properties["DestinationXY"].split(","))
                LOGGER.info(f"Transitioning to {destination_area.name.lower()}")
                self.player.x = TILE_SIZE * dest_x + TILE_SIZE // 2
                self.player.y = TILE_SIZE * dest_y + TILE_SIZE // 2
                return destination_area
        return None

    def detect_and_handle_collisions(self, target_x, target_y):
        px = target_x // TILE_SIZE
        py = target_y // TILE_SIZE
        for layer in range(0, 2):
            tile_props = self.tmxdata.get_tile_properties(px, py, layer) or {}
            if tile_props.get("colliders"):
                return True
        return False

    def end_encounter(self, win):
        if win:
            self.grant_experience()
        self.encounter = None

    def grant_experience(self):
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

    def turn(self, move_name):
        self.turn_player(move_name)
        if self.encounter:
            self.turn_enemy()

    def turn_player(self, move_name):
        move = self.moves.find_by_name(move_name)
        enemy_damage = self.attack(self.active_pokemon, self.enemy, move)
        self.enemy.take_damage(enemy_damage)
        LOGGER.info(f"Enemy {self.enemy.name} took {enemy_damage} dmg from {move_name}")
        if self.enemy.current_hp <= 0:
            LOGGER.info(f"Enemy {self.active_pokemon.name} fainted!")
            self.end_encounter(True)

    def turn_enemy(self):
        enemy_move = self.moves.find_by_id(self.random.choice(self.enemy.moves).id)
        player_damage = self.attack(self.enemy, self.active_pokemon, enemy_move)
        self.active_pokemon.take_damage(player_damage)

        LOGGER.info(
            f"{self.active_pokemon.name} took {player_damage} dmg from {enemy_move.name}"
        )
        if self.active_pokemon.current_hp <= 0:
            LOGGER.info(f"Your {self.active_pokemon.name} fainted!")
            self.end_encounter(False)

    def attack(self, attacker: Pokemon, defender: Pokemon, move: Move):
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
        critical_hit_scalar = 1 if self.random.random() > 0.0625 else 2
        random_factor = self.random.random() * 0.15 + 0.85
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

    @property
    def enemy(self) -> Pokemon:
        return self.encounter.enemy
