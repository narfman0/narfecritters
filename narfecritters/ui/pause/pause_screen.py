import logging
from enum import Enum
from sys import exit

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.pause.critters_screen import CrittersScreen
from narfecritters.ui.pause.item_screen import ItemScreen
from narfecritters.ui.pause.load_screen import LoadScreen
from narfecritters.ui.pause.save_screen import SaveScreen
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    CRITTERS = 1
    ITEMS = 2
    BACK = 3
    LOAD = 4
    SAVE = 5
    QUIT = 6


class PauseScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.menu_buttons: list[UIButton] = []
        self.init()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.text == MenuOptions.BACK.name:
                    self.screen_manager.pop()
                if event.ui_element.text == MenuOptions.CRITTERS.name:
                    self.screen_manager.push(
                        CrittersScreen(self.ui_manager, self.screen_manager, self.world)
                    )
                if event.ui_element.text == MenuOptions.ITEMS.name:
                    self.screen_manager.push(
                        ItemScreen(self.ui_manager, self.screen_manager, self.world)
                    )
                if event.ui_element.text == MenuOptions.SAVE.name:
                    self.screen_manager.push(
                        SaveScreen(self.ui_manager, self.screen_manager, self.world)
                    )
                if event.ui_element.text == MenuOptions.LOAD.name:
                    self.screen_manager.push(
                        LoadScreen(self.ui_manager, self.screen_manager, self.world)
                    )
                if event.ui_element.text == MenuOptions.QUIT.name:
                    exit()

    def init(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        for menu_option in MenuOptions:
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), menu_option.name, manager=self.ui_manager
            )
            self.menu_buttons.append(menu_button)
            y += 32

    def kill(self):
        self.kill_elements(self.menu_buttons)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
