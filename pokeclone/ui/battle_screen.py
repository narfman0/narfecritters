import logging

import pygame
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton

from pokeclone.ui.screen import Screen, ScreenManager
from pokeclone.ui.settings import WINDOW_SIZE
from pokeclone.world import World


LOGGER = logging.getLogger(__name__)


class BattleScreen(Screen):
    def __init__(self, screen_manager: ScreenManager, world: World):
        super().__init__()
        self.screen_manager = screen_manager
        self.world = world
        self.fight_buttons = []
        y = WINDOW_SIZE[1] - 156
        for move in self.world.active_pokemon.moves:
            self.fight_buttons.append(UIButton((WINDOW_SIZE[0] - 100, y), move.name))
            y += 32
        self.enemy_pokemon_image = pygame.image.load(
            f"data/sprites/pokemon/{world.enemy.id}.png"
        ).convert()
        self.self_pokemon_image = pygame.image.load(
            f"data/sprites/pokemon/back/{world.active_pokemon.id}.png"
        ).convert()
        LOGGER.info(f"You are fighting a {self.world.enemy}")

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.fight_buttons:
                move_name = event.ui_element.text
                self.world.turn(move_name)
                if self.world.enemy is None:
                    for button in self.fight_buttons:
                        button.kill()
                    self.screen_manager.pop()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.enemy_pokemon_image, (WINDOW_SIZE[0] - 128, 32))
        surface.blit(self.self_pokemon_image, (32, WINDOW_SIZE[1] - 128))
