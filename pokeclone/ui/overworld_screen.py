import logging
import random

import pygame

from pokeclone.world import MOVE_SPEED, World
from pokeclone.ui.battle_screen import BattleScreen
from pokeclone.ui.screen import Screen, ScreenManager
from pokeclone.ui.settings import WINDOW_SIZE, TILE_SIZE

LOGGER = logging.getLogger(__name__)

ENCOUNTER_CHANCE = 0.05


class OverworldScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager
        self.world = World()
        self.npc_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.npc_surface.fill((255, 0, 0))

    def update(self, dt: float):
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

    def draw(self, surface):
        background = pygame.Surface(WINDOW_SIZE)
        background.fill((0, 255, 0))
        surface.blit(background, (0, 0))
        surface.blit(
            self.npc_surface,
            (
                self.world.player.x - TILE_SIZE / 2,
                WINDOW_SIZE[1] - self.world.player.y - TILE_SIZE / 2,
            ),
        )

    def maybe_create_encounter(self):
        if random.random() > ENCOUNTER_CHANCE:
            return
        self.screen_manager.push(BattleScreen(self.screen_manager, self.world))
