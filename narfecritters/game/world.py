import logging
import math
from dataclasses import dataclass
from random import Random
from xml.etree import ElementTree

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
    enemy: Critter
    active_critter_index: int
    order_player_first: bool = True
    run_attempts: int = 0
    enemy_stat_stages: EncounterStages = EncounterStages()
    player_stat_stages: EncounterStages = EncounterStages()


@dataclass
class MoveResult:
    encounter: bool = False
    area_change: Area = None


@dataclass
class MoveAction:
    target_x: int
    target_y: int
    running: bool


@dataclass
class AttackResult:
    damage: Optional[int] = None
    type_factor: Optional[float] = None


@dataclass
class TurnResult:
    information: list[str]
    fainted: bool


@dataclass
class AreaEncounter:
    id: int
    probability: int


class World:
    def __init__(self, random=None):
        self.encyclopedia = Encyclopedia.load()
        self.moves = Moves.load()
        self.random = random if random else Random()
        self.player = NPC()
        self.encounter: Optional[Encounter] = None
        self.area: Optional[Area] = None
        self.tmxdata: Optional[pytmx.TiledMap] = None
        self.candidate_encounters: list[int] = []
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
                if self.active_critter is None:
                    LOGGER.warn("All critters fainted!")
                    self.respawn()
                elif self.detect_and_handle_random_encounter():
                    return MoveResult(encounter=True)
        return MoveResult()

    def respawn(self):
        """Heal critters and udate player location, generally due to blackout"""
        self.player.x = self.player.respawn_x
        self.player.y = self.player.respawn_y
        self.set_area(self.player.respawn_area)
        for critter in self.player.critters:
            critter.current_hp = critter.max_hp

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
        elif up:
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
                enemy_id = self.random.choice(self.candidate_encounters)
                enemy = self.encyclopedia.create(
                    self.random,
                    id=enemy_id,
                    level=round(self.random.random() * 3 + 1),
                )
                order_player_first = enemy.speed < self.active_critter.speed
                if enemy.speed == self.active_critter.speed:
                    order_player_first = self.random.choice([False, True])
                self.encounter = Encounter(
                    enemy=enemy,
                    order_player_first=order_player_first,
                    active_critter_index=self.player.active_critter_index,
                )
                return True

    def detect_area_transition(self):
        px = int(self.player.x // TILE_SIZE)
        py = int(self.player.y // TILE_SIZE)
        for layer in range(0, 2):
            tile_props = self.tmxdata.get_tile_properties(px, py, layer) or {}
            if tile_props.get("type") == "heal":
                for critters in self.player.critters:
                    critters.current_hp = critters.max_hp
                self.update_respawn()
                LOGGER.info("Healed!")
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

    def end_encounter(self, win, information: list[str]):
        if win:
            self.grant_experience(information)
        self.encounter = None
        if self.active_critter is None:
            self.respawn()

    def update_respawn(self):
        self.player.respawn_area = self.area
        self.player.respawn_x = self.player.x
        self.player.respawn_y = self.player.y

    def grant_experience(self, information: list[str]):
        # xp gain formula described: https://bulbapedia.bulbagarden.net/wiki/Experience
        xp_gain_level_scalar_numerator = int(
            round(math.sqrt(2 * self.enemy.level + 10))
            * (2 * self.enemy.level + 10) ** 2
        )
        xp_gain_level_scalar_denominator = int(
            round(math.sqrt(self.enemy.level + self.active_critter.level + 10))
            * (self.enemy.level + self.active_critter.level + 10) ** 2
        )
        xp_gain = (
            round(
                ((self.enemy.base_experience * self.enemy.level) / 5)
                * (xp_gain_level_scalar_numerator / xp_gain_level_scalar_denominator)
            )
            + 1
        )
        current_level = self.active_critter.level
        self.active_critter.experience += xp_gain
        LOGGER.info(f"{self.active_critter.name} gained {xp_gain} experience!")
        if current_level < self.active_critter.level:
            information.append(
                f"{self.active_critter.name} leveled up to {self.active_critter.level}"
            )
            LOGGER.info(information[-1])

    def catch(self) -> TurnResult:
        """
        Attempt to catch the attacking critter. See:
        https://bulbapedia.bulbagarden.net/wiki/Catch_rate#Capture_method_.28Generation_V.2B.29
        """
        information: list[str] = []
        fainted = False

        bonus_ball = 1
        status_bonus = 1  # TODO
        numerator = (
            (3 * self.enemy.max_hp - 2 * self.enemy.current_hp)
            * 4096
            * self.enemy.capture_rate
            * bonus_ball
        )
        a = math.floor(numerator / 3 * self.enemy.max_hp) * status_bonus
        if a >= self.random.randint(0, 1044480) or self.shake_check(a):
            information.append(f"{self.enemy.name} caught successfully!")
            self.player.add_critter(self.enemy)
            self.end_encounter(True, information)
        else:
            information.append(f"Failed to catch {self.enemy.name}.")
            fainted = self.use_move(
                defender=self.active_critter,
                attacker=self.enemy,
                information=information,
            )
        return TurnResult(information, fainted)

    def shake_check(self, a) -> bool:
        """Perform 3 shake checkes as described:
        https://bulbapedia.bulbagarden.net/wiki/Catch_rate#Shake_probability_4
        """
        for _x in range(3):
            b = math.floor(65536 / math.sqrt(math.sqrt(1044480 / a)))
            if self.random.randint(0, 65535) >= b:
                return False
        return True

    def run(self) -> TurnResult:
        """Attempt to flee the attacking critter"""
        information: list[str] = []
        fainted = False

        odds_escape = (
            int((self.active_critter.speed * 128) / self.enemy.speed)
            + 30 * self.encounter.run_attempts
        ) % 256
        if odds_escape >= self.random.randint(0, 255):
            information.append(f"{self.active_critter.name} escaped successfully!")
            self.end_encounter(False, information)
        else:
            information.append(f"{self.active_critter.name} failed to run away.")
            self.encounter.run_attempts += 1
            fainted = self.use_move(
                defender=self.active_critter,
                attacker=self.enemy,
                information=information,
            )
        return TurnResult(information, fainted)

    def turn(self, move_name) -> TurnResult:
        """Take each critters turn. Observes speeds for priority order."""
        information: list[str] = []
        fainted = False
        move = self.moves.find_by_name(move_name)
        if self.encounter.order_player_first:
            self.use_move(
                defender=self.enemy,
                attacker=self.active_critter,
                information=information,
                move=move,
            )
        else:
            fainted = self.use_move(
                defender=self.active_critter,
                attacker=self.enemy,
                information=information,
            )

        if self.encounter:
            if self.encounter.order_player_first:
                fainted = self.use_move(
                    defender=self.active_critter,
                    attacker=self.enemy,
                    information=information,
                )
            else:
                self.use_move(
                    defender=self.enemy,
                    attacker=self.active_critter,
                    information=information,
                    move=move,
                )
        return TurnResult(information, fainted)

    def use_move(
        self,
        attacker: Critter,
        defender: Critter,
        information: list[str],
        move: Optional[Move] = None,
    ) -> bool:
        """Use a move, if not given, choose randomly"""
        if not move:
            move = self.moves.find_by_id(self.random.choice(attacker.moves).id)
        attack_result = self.attack(attacker, defender, move)
        if attack_result and attack_result.damage:
            player_damage = attack_result.damage
            defender.take_damage(player_damage)

            information_suffix = self.get_type_effectiveness_response_suffix(
                attack_result.type_factor
            )
            information.append(
                f"{defender.name} took {player_damage} dmg from {move.name}. "
                + information_suffix
            )
            LOGGER.info(information[-1])
        if defender.current_hp <= 0:
            information.append(f"{defender.name} fainted!")
            LOGGER.info(information[-1])
            if defender in self.player.critters:
                self.encounter.active_critter_index = self.player.active_critter_index
                if self.encounter.active_critter_index is None:
                    self.end_encounter(False, information)
            else:
                self.end_encounter(True, information)
            return True
        self.move_stat_changes(attacker, defender, move)
        return False

    def move_stat_changes(self, attacker: Critter, defender: Critter, move: Move):
        if not move.stat_changes:
            return
        # TODO implement buffs, return information, add targets, make this cleaner
        defender_stat_stages = (
            self.encounter.enemy_stat_stages
            if attacker == self.active_critter
            else self.encounter.player_stat_stages
        )
        for stat_change in move.stat_changes:
            current_stat = getattr(defender_stat_stages, stat_change.name)
            setattr(
                defender_stat_stages,
                stat_change.name,
                current_stat + stat_change.amount,
            )

    def attack(
        self, attacker: Critter, defender: Critter, move: Move
    ) -> Optional[AttackResult]:
        """Follows gen5 dmg formula as defined: https://bulbapedia.bulbagarden.net/wiki/Damage#Generation_V_onward"""
        APPLICABILITY = [
            MoveCategory.DAMAGE,
            MoveCategory.DAMAGE_AILMENT,
            MoveCategory.DAMAGE_HEAL,
            MoveCategory.DAMAGE_LOWER,
            MoveCategory.DAMAGE_RAISE,
        ]
        if move.category not in APPLICABILITY:
            return
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
        return AttackResult(
            damage=round(
                base_damage * critical_hit_scalar * random_factor * stab * type_factor
            ),
            type_factor=type_factor,
        )

    def set_area(self, area: Area):
        self.area = area
        self.tmxdata = pytmx.load_pygame(f"data/tiled/{area.name.lower()}.tmx")
        if not self.player.respawn_area:
            start_x, start_y = map(
                int, self.tmxdata.properties.get("StartTile").split(",")
            )
            self.player.x = TILE_SIZE * start_x + TILE_SIZE // 2
            self.player.y = TILE_SIZE * start_y + TILE_SIZE // 2
            self.update_respawn()
        self.candidate_encounters: list[int] = []
        encounters_str = self.tmxdata.properties.get("Encounters")
        if not encounters_str:
            return
        for encounter in encounters_str.split("\n"):
            name, probability = str(encounter).split(",")
            id = self.encyclopedia.name_to_id[name]
            self.candidate_encounters.extend([id] * int(probability))

    @classmethod
    def get_type_effectiveness_response_suffix(cls, type_factor: float):
        if type_factor == 0:
            return " It had no effect."
        elif type_factor < 1:
            return " It wasn't very effective."
        elif type_factor > 1:
            return " It was super effective!"
        return ""

    @property
    def active_critter(self) -> Critter:
        if self.encounter:
            return self.player.critters[self.encounter.active_critter_index]
        return self.player.active_critter

    @property
    def enemy(self) -> Critter:
        return self.encounter.enemy
