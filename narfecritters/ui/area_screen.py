import logging

import pygame
import pytmx
from pygame_gui import UIManager

from narfecritters.db.models import Area
from narfecritters.game.world import World
from narfecritters.ui.battle_screen import BattleScreen
from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import TILE_SIZE, WINDOW_SIZE

LOGGER = logging.getLogger(__name__)
TILE_VIEW_SPAN = 16  # how many tiles away shall we paint


class AreaScreen(Screen):
    def __init__(
        self,
        ui_manager: UIManager,
        screen_manager: ScreenManager,
        world: World,
        area: Area,
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.load_player_image()
        self.tmxdata = pytmx.load_pygame(f"data/tiled/{area.name.lower()}.tmx")
        self.world.area = area
        self.world.tmxdata = self.tmxdata

    def update(self, dt: float):
        if not self.world.move_action:
            self.handle_move()
        result = self.world.update(dt)
        if result.encounter:
            self.screen_manager.push(
                BattleScreen(self.ui_manager, self.screen_manager, self.world)
            )
        if result.area_change:
            self.screen_manager.pop()
            screen = AreaScreen(
                self.ui_manager,
                self.screen_manager,
                self.world,
                result.area_change,
            )
            self.screen_manager.push(screen)
            self.kill()

    def handle_move(self):
        move_kwargs = {}
        if (
            pygame.key.get_pressed()[pygame.K_LEFT]
            or pygame.key.get_pressed()[pygame.K_a]
        ):
            move_kwargs["left"] = True
        elif (
            pygame.key.get_pressed()[pygame.K_RIGHT]
            or pygame.key.get_pressed()[pygame.K_d]
        ):
            move_kwargs["right"] = True
        if (
            pygame.key.get_pressed()[pygame.K_UP]
            or pygame.key.get_pressed()[pygame.K_w]
        ):
            move_kwargs["up"] = True
        elif (
            pygame.key.get_pressed()[pygame.K_DOWN]
            or pygame.key.get_pressed()[pygame.K_s]
        ):
            move_kwargs["down"] = True
        if move_kwargs:
            running = (
                pygame.key.get_pressed()[pygame.K_LSHIFT]
                or pygame.key.get_pressed()[pygame.K_RSHIFT]
            )
            self.world.move(running=running, **move_kwargs)

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
