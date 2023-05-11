import logging

import pygame
from pygame_gui import UIManager

from narfecritters.game.world import World
from narfecritters.ui.battle_screen import BattleScreen
from narfecritters.ui.merchant.merchant_screen import MerchantScreen
from narfecritters.ui.npc_sprite import NPCSprite
from narfecritters.ui.pause.pause_screen import PauseScreen
from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import TILE_SIZE, WINDOW_SIZE

LOGGER = logging.getLogger(__name__)
TILE_VIEW_SPAN = (
    WINDOW_SIZE[0] // 2 // TILE_SIZE + 2
)  # how many tiles away shall we paint


class AreaScreen(Screen):
    def __init__(
        self,
        ui_manager: UIManager,
        screen_manager: ScreenManager,
        world: World,
        area: str,
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.player_sprite = NPCSprite("player", 0.8, offset=(0, -4))
        self.sprites = pygame.sprite.Group(self.player_sprite)
        self.world.set_area(area)
        self.merchant_sprite = None

    def update(self, dt: float):
        if (
            pygame.key.get_pressed()[pygame.K_ESCAPE]
            or pygame.key.get_pressed()[pygame.K_TAB]
        ):
            self.screen_manager.push(
                PauseScreen(self.ui_manager, self.screen_manager, self.world)
            )
        if (
            pygame.key.get_pressed()[pygame.K_RETURN]
            or pygame.key.get_pressed()[pygame.K_EQUALS]
        ):
            if self.world.detect_merchant():
                self.screen_manager.push(
                    MerchantScreen(self.ui_manager, self.screen_manager, self.world)
                )
        if not self.world.move_action:
            self.player_sprite.stop()
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

        self.update_merchant_sprite()

        self.player_sprite.set_position(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
        self.sprites.update()

    def update_merchant_sprite(self):
        if self.world.merchant:
            if not self.merchant_sprite:
                self.merchant_sprite = NPCSprite("npc06", 1, offset=(0, -4))
            self.merchant_sprite.set_position(
                WINDOW_SIZE[0] // 2 + self.world.merchant.x - self.world.player.x,
                WINDOW_SIZE[1] // 2 + self.world.merchant.y - self.world.player.y,
            )
            if not self.sprites.has(self.merchant_sprite):
                self.sprites.add(self.merchant_sprite)
        elif self.world.merchant is None and self.merchant_sprite:
            self.merchant_sprite.kill()

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
        elif (
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
            self.player_sprite.move(**move_kwargs)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
        self.draw_terrain(surface)
        self.sprites.draw(surface)

    def draw_terrain(self, surface):
        px = self.world.player.x
        py = self.world.player.y
        tile_x = int(px // TILE_SIZE)
        tile_y = int(py // TILE_SIZE)
        tile_x_begin = max(0, tile_x - TILE_VIEW_SPAN)
        tile_x_end = min(tile_x + TILE_VIEW_SPAN, self.world.map.width)
        tile_y_begin = max(0, tile_y - TILE_VIEW_SPAN)
        tile_y_end = min(tile_y + TILE_VIEW_SPAN, self.world.map.height)
        for layer in range(self.world.map.get_tile_layer_count()):
            for x in range(tile_x_begin, tile_x_end):
                for y in range(tile_y_begin, tile_y_end):
                    image = self.world.map.get_tile_image(x, y, layer)
                    if image:
                        surface.blit(
                            image,
                            (
                                WINDOW_SIZE[0] // 2 + x * TILE_SIZE - px,
                                WINDOW_SIZE[1] // 2 + y * TILE_SIZE - py,
                            ),
                        )
