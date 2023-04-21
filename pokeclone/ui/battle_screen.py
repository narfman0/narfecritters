import logging
import random

import pygame
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton

from pokeclone.ui.screen import Screen, ScreenManager
from pokeclone.ui.settings import WINDOW_SIZE
from pokeclone.world import World


LOGGER = logging.getLogger(__name__)


class BattleScreen(Screen):
    def __init__(self, screen_manager: ScreenManager, world: World):
        self.screen_manager = screen_manager
        self.world = world
        self.fight_buttons = []
        y = WINDOW_SIZE[1] - 156
        for move in self.world.active_pokemon().moves:
            self.fight_buttons.append(UIButton((WINDOW_SIZE[0] - 100, y), move.name))
            y += 32
        self.world.create_encounter()
        self.enemy_pokemon_image = pygame.image.load(
            f"data/sprites/pokemon/{world.enemy.id}.png"
        ).convert()
        self.self_pokemon_image = pygame.image.load(
            f"data/sprites/pokemon/back/{world.active_pokemon().id}.png"
        ).convert()
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
        self.world.end_encounter()
        for button in self.fight_buttons:
            button.kill()
        self.screen_manager.pop()

    def draw(self, surface: pygame.Surface):
        background = pygame.Surface(WINDOW_SIZE)
        background.fill((128, 128, 128))
        surface.blit(background, (0, 0))
        surface.blit(self.enemy_pokemon_image, (WINDOW_SIZE[0] - 128, 32))
        surface.blit(self.self_pokemon_image, (32, WINDOW_SIZE[1] - 128))
