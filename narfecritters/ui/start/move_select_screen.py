import logging

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton, UIScrollingContainer

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


class MoveSelectScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.information_elements = [
            UIButton(
                (0, 0), "Click the moves you'd like to forget", manager=self.ui_manager
            ),
        ]
        self.init_scrolling_container()
        self.init_buttons()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.buttons:
                species_move = event.ui_element.species_move
                self.world.player.active_critter.moves.remove(species_move)
                if len(self.world.player.active_critter.moves) <= 4:
                    self.screen_manager.pop()
                else:
                    self.reinit()

    def init(self):
        self.init_scrolling_container()
        self.init_buttons()

    def init_buttons(self):
        self.buttons: list[UIButton] = []
        y = 0
        for species_move in self.world.player.active_critter.moves:
            button = UIButton(
                relative_rect=pygame.Rect(0, y, WINDOW_SIZE[0] // 3, 32),
                text=species_move.name_pretty,
                container=self.scrolling_container,
                manager=self.ui_manager,
            )
            button.species_move = species_move
            self.buttons.append(button)
            y += 32

    def init_scrolling_container(self):
        scrolling_height = len(self.world.player.active_critter.moves) * 32
        self.scrolling_container = UIScrollingContainer(
            pygame.Rect(
                WINDOW_SIZE[0] // 3,
                32,
                WINDOW_SIZE[0] // 3,
                WINDOW_SIZE[1] - 64,
            ),
            manager=self.ui_manager,
        )
        self.scrolling_container.set_scrollable_area_dimensions(
            (
                WINDOW_SIZE[0] // 3,
                scrolling_height,
            )
        )

    def kill(self):
        self.kill_elements(self.buttons + self.information_elements)
        self.scrolling_container.kill()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
