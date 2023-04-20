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


def main():
    initialize_logging()
    pygame.init()
    pygame.display.set_caption("pokeclone")
    window_surface = pygame.display.set_mode(WINDOW_SIZE)
    manager = UIManager(WINDOW_SIZE, "data/theme.json")
    background = pygame.Surface(WINDOW_SIZE)
    background.fill((0, 255, 0))
    npc_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    npc_surface.fill((255, 0, 0))
    hello_button = UIButton((350, 280), "Hello")

    clock = pygame.time.Clock()
    is_running = True

    world = World()

    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == hello_button:
                    print("Hello World!")
            manager.process_events(event)

        if pygame.key.get_pressed()[pygame.K_LEFT] and world.player.x > 0:
            world.player.x -= MOVE_SPEED
        elif (
            pygame.key.get_pressed()[pygame.K_RIGHT] and world.player.x < WINDOW_SIZE[0]
        ):
            world.player.x += MOVE_SPEED
        if pygame.key.get_pressed()[pygame.K_UP] and world.player.y < WINDOW_SIZE[1]:
            world.player.y += MOVE_SPEED
        elif pygame.key.get_pressed()[pygame.K_DOWN] and world.player.y > 0:
            world.player.y -= MOVE_SPEED
        world.update(time_delta)
        manager.update(time_delta)
        window_surface.blit(background, (0, 0))
        window_surface.blit(
            npc_surface,
            (
                world.player.x - TILE_SIZE / 2,
                WINDOW_SIZE[1] - world.player.y - TILE_SIZE / 2,
            ),
        )
        manager.draw_ui(window_surface)

        pygame.display.update()


if __name__ == "__main__":
    main()
