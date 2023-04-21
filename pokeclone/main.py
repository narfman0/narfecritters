import logging

from pokeclone import settings
from pokeclone.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


"""
* randomly pick first pokemon
* fight pokemon
* final boss
"""


import pygame
from pygame_gui import UIManager, UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton


from pokeclone.world import MOVE_SPEED, World

WINDOW_SIZE = (800, 600)
TILE_SIZE = 16


class OverworldScreen:
    def __init__(self):
        self.world = World()
        self.npc_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.npc_surface.fill((255, 0, 0))

    def update(self, dt: float):
        if (
            pygame.key.get_pressed()[pygame.K_LEFT]
            or pygame.key.get_pressed()[pygame.K_a]
        ) and self.world.player.x > 0:
            self.world.player.x -= MOVE_SPEED
        elif (
            pygame.key.get_pressed()[pygame.K_RIGHT]
            or pygame.key.get_pressed()[pygame.K_d]
        ) and self.world.player.x < WINDOW_SIZE[0]:
            self.world.player.x += MOVE_SPEED
        if (
            pygame.key.get_pressed()[pygame.K_UP]
            or pygame.key.get_pressed()[pygame.K_w]
        ) and self.world.player.y < WINDOW_SIZE[1]:
            self.world.player.y += MOVE_SPEED
        elif (
            pygame.key.get_pressed()[pygame.K_DOWN]
            or pygame.key.get_pressed()[pygame.K_s]
        ) and self.world.player.y > 0:
            self.world.player.y -= MOVE_SPEED
        self.world.update(dt)

    def draw(self, surface):
        surface.blit(
            self.npc_surface,
            (
                self.world.player.x - TILE_SIZE / 2,
                WINDOW_SIZE[1] - self.world.player.y - TILE_SIZE / 2,
            ),
        )


def main():
    initialize_logging()
    pygame.init()
    pygame.display.set_caption("pokeclone")
    window_surface = pygame.display.set_mode(WINDOW_SIZE)
    manager = UIManager(WINDOW_SIZE, "data/theme.json")
    background = pygame.Surface(WINDOW_SIZE)
    background.fill((0, 255, 0))
    hello_button = UIButton((350, 280), "Hello")

    clock = pygame.time.Clock()
    is_running = True

    overworld_screen = OverworldScreen()

    while is_running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == hello_button:
                    print("Hello World!")
            manager.process_events(event)

        overworld_screen.update(dt)

        manager.update(dt)
        window_surface.blit(background, (0, 0))
        overworld_screen.draw(window_surface)
        manager.draw_ui(window_surface)

        pygame.display.update()


if __name__ == "__main__":
    main()
