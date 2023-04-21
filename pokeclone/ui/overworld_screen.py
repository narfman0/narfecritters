import logging
import random

import pygame
from pygame_gui import UIManager, UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton

from pokeclone.world import MOVE_SPEED, World
from pokeclone.ui.settings import WINDOW_SIZE, TILE_SIZE

LOGGER = logging.getLogger(__name__)

ENCOUNTER_CHANCE = 0.05


class OverworldScreen:
    def __init__(self):
        self.world = World()
        self.npc_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.npc_surface.fill((255, 0, 0))
        self.fight_buttons = []
        self.pokemon_til_boss = 10
        self.is_boss = False

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.fight_buttons:
                if not self.world.in_encounter:
                    return
                move_name = event.ui_element.text
                player_dmg, enemy_dmg = self.world.turn(move_name)
                print(
                    f"{self.world.active_pokemon().name} used {move_name} for {enemy_dmg}, took {player_dmg}"
                )
                if self.world.active_pokemon().current_hp <= 0:
                    LOGGER.info(f"Your {self.world.active_pokemon().name} passed out!")
                    self.end_encounter()
                if self.world.enemy.current_hp <= 0:
                    LOGGER.info(f"Enemy {self.world.active_pokemon().name} passed out!")
                    self.end_encounter()
                    if self.is_boss:
                        UIButton((350, 280), "You Win wowooowowwowooo!!!!!")

    def update(self, dt: float, manager: UIManager):
        if not self.world.in_encounter:
            self.update_overworld_movement()
        self.world.update(dt)

    def draw(self, surface):
        surface.blit(
            self.npc_surface,
            (
                self.world.player.x - TILE_SIZE / 2,
                WINDOW_SIZE[1] - self.world.player.y - TILE_SIZE / 2,
            ),
        )

    def update_overworld_movement(self):
        if (
            pygame.key.get_pressed()[pygame.K_LEFT]
            or pygame.key.get_pressed()[pygame.K_a]
        ) and self.world.player.x > 0:
            self.world.player.x -= MOVE_SPEED
            self.maybe_create_encounter()
        elif (
            pygame.key.get_pressed()[pygame.K_RIGHT]
            or pygame.key.get_pressed()[pygame.K_d]
        ) and self.world.player.x < WINDOW_SIZE[0]:
            self.world.player.x += MOVE_SPEED
            self.maybe_create_encounter()
        if (
            pygame.key.get_pressed()[pygame.K_UP]
            or pygame.key.get_pressed()[pygame.K_w]
        ) and self.world.player.y < WINDOW_SIZE[1]:
            self.world.player.y += MOVE_SPEED
            self.maybe_create_encounter()
        elif (
            pygame.key.get_pressed()[pygame.K_DOWN]
            or pygame.key.get_pressed()[pygame.K_s]
        ) and self.world.player.y > 0:
            self.world.player.y -= MOVE_SPEED
            self.maybe_create_encounter()

    def end_encounter(self):
        self.world.end_encounter()
        for button in self.fight_buttons:
            button.kill()
        self.pokemon_til_boss -= 1
        if self.pokemon_til_boss == 0:
            self.world.create_boss_encounter()
            LOGGER.info(f"You are fighting a {self.world.enemy}")
            self.create_encounter_fight_buttons()
            self.is_boss = True

    def maybe_create_encounter(self):
        if random.random() > ENCOUNTER_CHANCE or self.world.in_encounter:
            return
        self.world.create_encounter()
        LOGGER.info(f"You are fighting a {self.world.enemy}")
        self.create_encounter_fight_buttons()

    def create_encounter_fight_buttons(self):
        y = 280
        for move in self.world.active_pokemon().moves:
            self.fight_buttons.append(UIButton((350, y), move.name))
            y += 32
