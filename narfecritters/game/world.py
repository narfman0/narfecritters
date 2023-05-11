import logging
import math
from dataclasses import dataclass
from random import Random

from pygame.math import Vector2

from narfecritters.ui.settings import TILE_SIZE
from narfecritters.models import *
from narfecritters.game.move_damage import calculate_move_damage
from narfecritters.game.move_stat_changes import calculate_move_stat_changes
from narfecritters.game.map import Map

LOGGER = logging.getLogger(__name__)
ENCOUNTER_PROBABILITY = 0.1
MOVE_SPEED = 200
DEFAULT_AREA = "overworld"


@dataclass
class Encounter:
    enemy: Critter
    active_player_critter: Critter
    order_player_first: bool = True
    run_attempts: int = 0
    enemy_stat_stages: EncounterStages = EncounterStages()
    player_stat_stages: EncounterStages = EncounterStages()


@dataclass
class TurnStepResult:
    defender_flinched: bool


@dataclass
class MoveResult:
    encounter: bool = False
    area_change: str = None


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
        self.player.add_item(ItemType.BALL, 3)
        self.encounter: Optional[Encounter] = None
        self.area: Optional[str] = None
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
        for layer in range(self.map.get_tile_layer_count()):
            if (
                self.map.get_tile_type(px, py, layer) == "tallgrass"
                and self.random.random() < ENCOUNTER_PROBABILITY
            ):
                enemy_id = self.random.choice(self.candidate_encounters)
                encounter_level = self.map.get_area_encounter_level()
                level = round(
                    self.random.gauss(encounter_level.mean, encounter_level.sigma)
                )
                enemy = self.encyclopedia.create(
                    self.random,
                    id=enemy_id,
                    level=level,
                )
                order_player_first = enemy.speed < self.active_critter.speed
                if enemy.speed == self.active_critter.speed:
                    order_player_first = self.random.choice([False, True])
                self.encounter = Encounter(
                    enemy=enemy,
                    order_player_first=order_player_first,
                    active_player_critter=self.player.active_critter,
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
                LOGGER.info(f"Transitioning to {details.destination_area}")
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

    def detect_merchant(self):
        """TODO track which way we are facing and interact with that thing on map"""
        if not self.merchant:
            return False
        x_dist = math.pow(self.merchant.x - self.player.x, 2)
        y_dist = math.pow(self.merchant.y - self.player.y, 2)
        dist = math.sqrt(x_dist + y_dist)
        return dist // TILE_SIZE <= 1

    def end_encounter(self, win, information: list[str]):
        current_level = self.active_critter.level
        if win:
            self.grant_experience(information)
            if current_level < self.active_critter.level:
                information.append(
                    f"{self.active_critter.name} leveled up to {self.active_critter.level}"
                )
                self.detect_and_execute_evolution(information)
        self.encounter = None
        if self.active_critter is None:
            self.respawn()

    def detect_and_execute_evolution(self, information: list[str]):
        previous_name = self.active_critter.name
        for evolution_trigger in self.active_critter.evolution_triggers:
            if (
                evolution_trigger.min_level
                and evolution_trigger.min_level <= self.active_critter.level
            ):
                target_species_id = evolution_trigger.evolved_species_id
                self.encyclopedia.evolve(self.active_critter, target_species_id)
                information.append(
                    f"{previous_name} has evolved into {self.active_critter.name}"
                )
                return

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
        self.active_critter.experience += xp_gain
        LOGGER.info(f"{self.active_critter.name} gained {xp_gain} experience!")

    def catch(self, ball_type: ItemType) -> TurnResult:
        """
        Attempt to catch the attacking critter. See:
        https://bulbapedia.bulbagarden.net/wiki/Catch_rate#Capture_method_.28Generation_V.2B.29
        """
        information: list[str] = []
        if self.player.inventory[ball_type] > 0:
            self.player.remove_item(ball_type)
        else:
            information.append(f"No balls left!")
            return TurnResult(information, False)
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
            self.turn_step(
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
            self.turn_step(
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
        result = self.turn_step(
            defender=second,
            attacker=first,
            attacker_encounter_stages=first_encounter_stages,
            defender_encounter_stages=second_encounter_stages,
            information=information,
            move=first_move,
        )
        if not second.fainted:
            if result.defender_flinched:
                information.append(f"{second.name} flinched!")
            else:
                self.turn_step(
                    defender=first,
                    attacker=second,
                    attacker_encounter_stages=second_encounter_stages,
                    defender_encounter_stages=first_encounter_stages,
                    information=information,
                    move=second_move,
                )
        if first.has_ailment(Ailment.POISON):
            first.take_damage(first.max_hp // 8)
            self.check_and_observe_critter_faint(first, information)
        if second.has_ailment(Ailment.POISON):
            second.take_damage(second.max_hp // 8)
            self.check_and_observe_critter_faint(second, information)
        return TurnResult(information, player_critter.fainted)

    def turn_step(
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
        hit = (
            move.accuracy
            * attacker_encounter_stages.accuracy_multipler
            * defender_encounter_stages.evasion_multipler
            >= self.random.randint(1, 100)
        )
        if not hit:
            information.append(f"{attacker.name} missed!")
            return TurnStepResult(defender_flinched=False)
        self.calculate_and_apply_move_damage(
            attacker,
            defender,
            attacker_encounter_stages,
            defender_encounter_stages,
            move,
            information,
        )
        self.check_and_observe_critter_faint(defender, information)
        if move.healing:
            defender.heal(round(defender.max_hp * (move.healing / 100)))
        calculate_move_stat_changes(
            attacker,
            defender,
            attacker_encounter_stages,
            defender_encounter_stages,
            move,
            information,
        )
        if move.ailment and move.ailment_chance >= self.random.randint(1, 100):
            defender.ailments.add(move.ailment)
        return TurnStepResult(move.flinch_chance >= self.random.randint(1, 100))

    def check_and_observe_critter_faint(self, critter: Critter, information: list[str]):
        if critter.current_hp <= 0:
            information.append(f"{critter.name} fainted!")
            if critter in self.player.critters:
                self.encounter.active_player_critter = self.player.active_critter
                if self.encounter.active_player_critter is None:
                    self.end_encounter(False, information)
            else:
                self.end_encounter(True, information)

    def calculate_and_apply_move_damage(
        self,
        attacker: Critter,
        defender: Critter,
        attacker_encounter_stages: EncounterStages,
        defender_encounter_stages: EncounterStages,
        move: Move,
        information: list[str],
    ):
        result = calculate_move_damage(
            attacker,
            defender,
            attacker_encounter_stages,
            defender_encounter_stages,
            move,
            self.random,
        )
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

    def set_area(self, area: str):
        self.area = area
        self.map = Map(area)
        if not self.player.respawn_area:
            start_x, start_y = self.map.get_start_tile()
            self.player.x = TILE_SIZE * start_x + TILE_SIZE // 2
            self.player.y = TILE_SIZE * start_y + TILE_SIZE // 2
            self.update_respawn()

        if area == DEFAULT_AREA:
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
            return self.encounter.active_player_critter
        return self.player.active_critter

    @property
    def enemy(self) -> Critter:
        return self.encounter.enemy
