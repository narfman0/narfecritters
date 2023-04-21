import logging

import pygame
from pygame_gui import UIManager, UI_BUTTON_PRESSED

from pokeclone.logging import initialize_logging
from pokeclone.ui.overworld_screen import OverworldScreen
from pokeclone.ui.settings import WINDOW_SIZE


LOGGER = logging.getLogger(__name__)


def main():
    initialize_logging()
    pygame.init()
    pygame.display.set_caption("pokeclone")
    window_surface = pygame.display.set_mode(WINDOW_SIZE)
    manager = UIManager(WINDOW_SIZE, "data/theme.json")
    background = pygame.Surface(WINDOW_SIZE)
    background.fill((255, 255, 255))

    clock = pygame.time.Clock()
    is_running = True

    screens = []
    screens.append(OverworldScreen(screens))

    while is_running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == UI_BUTTON_PRESSED:
                screens[-1].process_event(event)
            if event.type == pygame.QUIT:
                is_running = False
            manager.process_events(event)

        screens[-1].update(dt)

        manager.update(dt)
        window_surface.blit(background, (0, 0))
        screens[-1].draw(window_surface)
        manager.draw_ui(window_surface)

        pygame.display.update()


if __name__ == "__main__":
    main()
