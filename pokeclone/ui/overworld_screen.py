import logging

import pygame
import pytmx

from pokeclone.world import MOVE_SPEED, World
from pokeclone.ui.battle_screen import BattleScreen
from pokeclone.ui.screen import Screen, ScreenManager
from pokeclone.ui.settings import TILE_SIZE, WINDOW_SIZE

LOGGER = logging.getLogger(__name__)
TILE_VIEW_SPAN = 16  # how many tiles away shall we paint


class OverworldScreen(Screen):
    def __init__(self, screen_manager: ScreenManager, world: World):
        super().__init__()
        self.screen_manager = screen_manager
        self.world = world
        self.load_player_image()
        self.tmxdata = pytmx.load_pygame("data/tiled/overworld.tmx")
        self.world.tmxdata = self.tmxdata

    def update(self, dt: float):
        if (
            pygame.key.get_pressed()[pygame.K_LEFT]
            or pygame.key.get_pressed()[pygame.K_a]
        ) and self.world.player.x > 0:
            self.world.move(dt * MOVE_SPEED, left=True)
        elif (
            pygame.key.get_pressed()[pygame.K_RIGHT]
            or pygame.key.get_pressed()[pygame.K_d]
        ) and self.world.player.x < self.tmxdata.width * TILE_SIZE:
            self.world.move(dt * MOVE_SPEED, right=True)
        if (
            pygame.key.get_pressed()[pygame.K_UP]
            or pygame.key.get_pressed()[pygame.K_w]
        ) and self.world.player.y > 0:
            self.world.move(dt * MOVE_SPEED, up=True)
        elif (
            pygame.key.get_pressed()[pygame.K_DOWN]
            or pygame.key.get_pressed()[pygame.K_s]
        ) and self.world.player.y < self.tmxdata.height * TILE_SIZE:
            self.world.move(dt * MOVE_SPEED, down=True)
        if self.world.encounter:
            # an encounter has been generated!
            self.screen_manager.push(BattleScreen(self.screen_manager, self.world))

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
        self.draw_terrain(surface)
        self.draw_player(surface)

    def draw_terrain(self, surface):
        px = self.world.player.x
        py = self.world.player.y
        tile_x = int(px // TILE_SIZE)
        tile_y = int(py // TILE_SIZE)
        tile_x_begin = max(0, tile_x - TILE_VIEW_SPAN)
        tile_x_end = min(tile_x + TILE_VIEW_SPAN, self.tmxdata.width)
        tile_y_begin = max(0, tile_y - TILE_VIEW_SPAN)
        tile_y_end = min(tile_y + TILE_VIEW_SPAN, self.tmxdata.height)
        for layer in [0, 1]:
            for x in range(tile_x_begin, tile_x_end):
                for y in range(tile_y_begin, tile_y_end):
                    image = self.tmxdata.get_tile_image(x, y, layer)
                    if image:
                        surface.blit(
                            image,
                            (
                                WINDOW_SIZE[0] // 2 + x * TILE_SIZE - px,
                                WINDOW_SIZE[1] // 2 + y * TILE_SIZE - py,
                            ),
                        )

    def draw_player(self, surface):
        surface.blit(
            self.player_image,
            (
                WINDOW_SIZE[0] // 2 - self.player_image.get_width() // 2,
                WINDOW_SIZE[1] // 2 - self.player_image.get_height() // 2,
            ),
        )

    def load_player_image(self):
        image = pygame.image.load(
            "data/sprites/overworld/player_standing.png"
        ).convert_alpha()
        size = image.get_size()
        self.player_image = pygame.transform.scale(
            image, (int(size[0] * 2), int(size[1] * 2))
        )
