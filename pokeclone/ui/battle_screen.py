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
        current = 0
        for move_id in self.world.active_pokemon.move_ids:
            if current >= 4:
                continue
            move = self.world.moves.find_by_id(move_id)
            self.fight_buttons.append(UIButton((WINDOW_SIZE[0] - 128, y), move.name))
            y += 32
            current += 1
        self.to_kill.extend(self.fight_buttons)
        self.enemy_pokemon_image = pygame.image.load(
            f"data/sprites/pokemon/front/{world.enemy.id}.png"
        ).convert()
        self.self_pokemon_image = pygame.image.load(
            f"data/sprites/pokemon/back/{world.active_pokemon.id}.png"
        ).convert()
        LOGGER.info(
            f"You are fighting a level {self.world.enemy.level} {self.world.enemy.name}"
        )

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.fight_buttons:
                move_name = event.ui_element.text
                self.world.turn(move_name)
                if self.world.enemy is None:
                    self.screen_manager.pop()
                    self.kill()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.enemy_pokemon_image, (WINDOW_SIZE[0] - 128, 32))
        surface.blit(self.self_pokemon_image, (32, WINDOW_SIZE[1] - 128))
