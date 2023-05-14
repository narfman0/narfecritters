import logging

import pygame
from pygame_gui import UIManager

from narfecritters.util.logging import initialize_logging
from narfecritters.ui.start_screen import StartScreen
from narfecritters.ui.screen import ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE


LOGGER = logging.getLogger(__name__)


def main():
    initialize_logging()
    pygame.init()
    pygame.display.set_caption("narfecritters")
    window_surface = pygame.display.set_mode(WINDOW_SIZE)
    manager = UIManager(WINDOW_SIZE, "data/theme.json")
    background = pygame.Surface(WINDOW_SIZE)
    background.fill((255, 255, 255))

    clock = pygame.time.Clock()
    is_running = True

    screen_manager = ScreenManager()
    screen_manager.push(StartScreen(manager, screen_manager))

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
