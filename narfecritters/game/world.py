import logging
import math
from dataclasses import dataclass
from random import Random

from pygame.math import Vector2

from narfecritters.ui.settings import TILE_SIZE
from narfecritters.models import *
from narfecritters.game.move_damage import calculate_move_damage
from narfecritters.game.map import Map

LOGGER = logging.getLogger(__name__)
ENCOUNTER_PROBABILITY = 0.1
MOVE_SPEED = 200


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
        self.map: Optional[Map] = None
        self.candidate_encounters: list[int] = []
        self.move_action = None
        self.merchant = None

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
            if (
                self.map.get_tile_type(px, py, layer) == "tallgrass"
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
            if self.map.get_tile_type(px, py, layer) == "heal":
                for critters in self.player.critters:
                    critters.current_hp = critters.max_hp
                self.update_respawn()
                LOGGER.info("Healed!")
            if self.map.get_tile_type(px, py, layer) == "transition":
                details = self.map.get_transition_details(px, py)
                LOGGER.info(f"Transitioning to {details.destination_area.name.lower()}")
                self.player.x = TILE_SIZE * details.destination_x + TILE_SIZE // 2
                self.player.y = TILE_SIZE * details.destination_y + TILE_SIZE // 2
                return details.destination_area
        return None

    def detect_and_handle_collisions(self, target_x, target_y):
        px = target_x // TILE_SIZE
        py = target_y // TILE_SIZE
        for layer in range(0, 2):
            if self.map.has_colliders(px, py, layer):
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
        player_critter = self.active_critter

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
            self.use_move(
                defender=player_critter,
                attacker=self.enemy,
                attacker_encounter_stages=self.encounter.enemy_stat_stages,
                defender_encounter_stages=self.encounter.player_stat_stages,
                information=information,
            )
        return TurnResult(information, player_critter.fainted)

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
        player_critter = self.active_critter

        odds_escape = (
            int((player_critter.speed * 128) / self.enemy.speed)
            + 30 * self.encounter.run_attempts
        ) % 256
        if odds_escape >= self.random.randint(0, 255):
            information.append(f"{player_critter.name} escaped successfully!")
            self.end_encounter(False, information)
        else:
            information.append(f"{player_critter.name} failed to run away.")
            self.encounter.run_attempts += 1
            self.use_move(
                defender=player_critter,
                attacker=self.enemy,
                attacker_encounter_stages=self.encounter.enemy_stat_stages,
                defender_encounter_stages=self.encounter.player_stat_stages,
                information=information,
            )
        return TurnResult(information, player_critter.fainted)

    def turn(self, move_name) -> TurnResult:
        """Take each critters turn. Observes speeds for priority order."""
        information: list[str] = []
        player_move = self.moves.find_by_name(move_name)
        player_critter = self.active_critter
        if self.encounter.order_player_first:
            first = player_critter
            first_move = player_move
            second = self.enemy
            second_move = None
            first_encounter_stages = self.encounter.player_stat_stages
            second_encounter_stages = self.encounter.enemy_stat_stages
        else:
            first = self.enemy
            first_move = None
            second = player_critter
            second_move = player_move
            first_encounter_stages = self.encounter.enemy_stat_stages
            second_encounter_stages = self.encounter.player_stat_stages
        self.use_move(
            defender=second,
            attacker=first,
            attacker_encounter_stages=first_encounter_stages,
            defender_encounter_stages=second_encounter_stages,
            information=information,
            move=first_move,
        )
        if not second.fainted:
            self.use_move(
                defender=first,
                attacker=second,
                attacker_encounter_stages=second_encounter_stages,
                defender_encounter_stages=first_encounter_stages,
                information=information,
                move=second_move,
            )
        return TurnResult(information, player_critter.fainted)

    def use_move(
        self,
        attacker: Critter,
        defender: Critter,
        attacker_encounter_stages: EncounterStages,
        defender_encounter_stages: EncounterStages,
        information: list[str],
        move: Optional[Move] = None,
    ):
        """Use a move, if not given, choose randomly"""
        if not move:
            move = self.moves.find_by_id(self.random.choice(attacker.moves).id)
        result = calculate_move_damage(attacker, defender, move, self.random)
        if result and result.damage:
            player_damage = result.damage
            defender.take_damage(player_damage)

            information_suffix = self.get_type_effectiveness_response_suffix(
                result.type_factor
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
        self.move_stat_changes(
            attacker,
            defender,
            attacker_encounter_stages,
            defender_encounter_stages,
            move,
            information,
        )

    def move_stat_changes(
        self,
        attacker: Critter,
        defender: Critter,
        attacker_encounter_stages: EncounterStages,
        defender_encounter_stages: EncounterStages,
        move: Move,
        information: list[str],
    ):
        if not move.stat_changes:
            return
        for stat_change in move.stat_changes:
            if move.target in [
                MoveTarget.ALL_CRITTERS,
                MoveTarget.ENTIRE_FIELD,
                MoveTarget.ALL_OPPONENTS,
                MoveTarget.OPPONENTS_FIELD,
                MoveTarget.RANDOM_OPPONENT,
                MoveTarget.ALL_OTHER_CRITTERS,
            ]:
                current_stat = getattr(defender_encounter_stages, stat_change.name)
                setattr(
                    defender_encounter_stages,
                    stat_change.name,
                    current_stat + stat_change.amount,
                )
                information.append(f"{stat_change.name} changed for {defender.name}")
            if move.target in [
                MoveTarget.ALL_CRITTERS,
                MoveTarget.ENTIRE_FIELD,
                MoveTarget.ALL_ALLIES,
                MoveTarget.USER_AND_ALLIES,
                MoveTarget.USER,
                MoveTarget.USER_OR_ALLY,
                MoveTarget.SELECTED_CRITTERS_ME_FIRST,
                MoveTarget.ALLY,
            ]:
                current_stat = getattr(attacker_encounter_stages, stat_change.name)
                setattr(
                    attacker_encounter_stages,
                    stat_change.name,
                    current_stat + stat_change.amount,
                )
                information.append(f"{stat_change.name} changed for {attacker.name}")

    def set_area(self, area: Area):
        self.area = area
        self.map = Map(area)
        if not self.player.respawn_area:
            start_x, start_y = self.map.get_start_tile()
            self.player.x = TILE_SIZE * start_x + TILE_SIZE // 2
            self.player.y = TILE_SIZE * start_y + TILE_SIZE // 2
            self.update_respawn()

        if area == Area.DEFAULT:
            start_x, start_y = self.map.get_start_tile()
            merchant_x, merchant_y = self.random.choices([-3, -2, -1, 1, 2, 3], k=2)
            self.spawn_merchant(start_x + merchant_x, start_y + merchant_y)
        else:
            self.merchant = None

        self.candidate_encounters = self.map.get_candidate_encounters(self.encyclopedia)

    def spawn_merchant(self, tile_x, tile_y):
        x = TILE_SIZE * tile_x + TILE_SIZE // 2
        y = TILE_SIZE * tile_y + TILE_SIZE // 2
        self.merchant = NPC(x, y, sprite="npc06")

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
