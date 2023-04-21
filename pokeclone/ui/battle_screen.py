import logging
import random

import pygame
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton

from pokeclone.ui.settings import WINDOW_SIZE
from pokeclone.world import World


LOGGER = logging.getLogger(__name__)


class BattleScreen:
    def __init__(self, screens: list, world: World):
        self.screens = screens
        self.world = world
        self.fight_buttons = []
        y = 280
        for move in self.world.active_pokemon().moves:
            self.fight_buttons.append(UIButton((350, y), move.name))
            y += 32
        self.world.create_encounter()
        LOGGER.info(f"You are fighting a {self.world.enemy}")

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.fight_buttons:
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

    def end_encounter(self):
        for button in self.fight_buttons:
            button.kill()
        self.world.end_encounter()
        self.screens.pop()

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        background = pygame.Surface(WINDOW_SIZE)
        background.fill((128, 128, 128))
        surface.blit(background, (0, 0))
