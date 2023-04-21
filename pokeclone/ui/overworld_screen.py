import logging
import random

import pygame

from pokeclone.world import MOVE_SPEED, World
from pokeclone.ui.battle_screen import BattleScreen
from pokeclone.ui.screen import Screen, ScreenManager
from pokeclone.ui.settings import WINDOW_SIZE

LOGGER = logging.getLogger(__name__)


class OverworldScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager
        self.world = World()
        self.player_image = pygame.image.load(
            "data/sprites/overworld/player_standing.png"
        ).convert()

    def update(self, dt: float):
        if (
            pygame.key.get_pressed()[pygame.K_LEFT]
            or pygame.key.get_pressed()[pygame.K_a]
        ) and self.world.player.x > 0:
            self.world.move(dt * MOVE_SPEED, left=True)
        elif (
            pygame.key.get_pressed()[pygame.K_RIGHT]
            or pygame.key.get_pressed()[pygame.K_d]
        ) and self.world.player.x < WINDOW_SIZE[0]:
            self.world.move(dt * MOVE_SPEED, right=True)
        if (
            pygame.key.get_pressed()[pygame.K_UP]
            or pygame.key.get_pressed()[pygame.K_w]
        ) and self.world.player.y < WINDOW_SIZE[1]:
            self.world.move(dt * MOVE_SPEED, up=True)
        elif (
            pygame.key.get_pressed()[pygame.K_DOWN]
            or pygame.key.get_pressed()[pygame.K_s]
        ) and self.world.player.y > 0:
            self.world.move(dt * MOVE_SPEED, down=True)
        if self.world.enemy:
            # an encounter has been generated!
            self.screen_manager.push(BattleScreen(self.screen_manager, self.world))

    def draw(self, surface: pygame.Surface):
        background = pygame.Surface(WINDOW_SIZE)
        background.fill((0, 255, 0))
        surface.blit(background, (0, 0))
        self.draw_overworld(
            surface, self.player_image, self.world.player.x, self.world.player.y
        )

    @classmethod
    def draw_overworld(cls, surface: pygame.Surface, image, x, y):
        """Converts world coordinates to screen coordinates"""
        screen_y = WINDOW_SIZE[1] - y - image.get_height() / 2
        surface.blit(image, (x + image.get_width() / 2, screen_y))
