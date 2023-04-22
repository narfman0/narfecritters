import logging

import pygame
from pygame_gui import UIManager, UI_BUTTON_PRESSED

from pokeclone.logging import initialize_logging
from pokeclone.ui.start_screen import StartScreen
from pokeclone.ui.screen import ScreenManager
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

    screen_manager = ScreenManager()
    screen_manager.push(StartScreen(screen_manager))

    while is_running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            else:
                screen_manager.current.process_event(event)
            manager.process_events(event)

        screen_manager.current.update(dt)

        manager.update(dt)
        window_surface.blit(background, (0, 0))
        screen_manager.current.draw(window_surface)
        manager.draw_ui(window_surface)

        pygame.display.update()


if __name__ == "__main__":
    main()
