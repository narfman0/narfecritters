import logging
from enum import Enum

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    BACK = 1


class CrittersScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.menu_buttons: list[UIButton] = []
        self.active_critter_buttons: list[UIButton] = []
        self.critter_buttons: list[UIButton] = []
        self.initialize_menu_buttons()
        self.initialize_active_critter_buttons()
        self.initialize_critter_buttons()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.text == MenuOptions.BACK.name:
                    self.kill_menu_buttons()
                    self.kill_active_critter_buttons()
                    self.kill_critter_buttons()
                    self.screen_manager.pop()
                    # TODO this is messy, but should always be the pause screen.
                    # screen manager should autorun an init function of some sort?
                    self.screen_manager.current.initialize_menu_buttons()

    def initialize_active_critter_buttons(self):
        y = 64
        for active_critter_idx in range(6):
            text = None
            if active_critter_idx >= len(self.world.player.active_critters):
                text = "-"
            else:
                critter = self.world.player.critters[active_critter_idx]
                text = self.text_for_critter(critter)
            button = UIButton((64, y), text, manager=self.ui_manager)
            self.active_critter_buttons.append(button)
            y += 32

    def initialize_critter_buttons(self):
        y = 64
        for idx, critter in enumerate(self.world.player.critters):
            if idx in self.world.player.active_critters:
                continue
            text = self.text_for_critter(critter)
            button = UIButton((WINDOW_SIZE[0] // 2, y), text, manager=self.ui_manager)
            self.critter_buttons.append(button)
            y += 32

    def initialize_menu_buttons(self):
        y = WINDOW_SIZE[1] - 156
        for menu_option in MenuOptions:
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), menu_option.name, manager=self.ui_manager
            )
            self.menu_buttons.append(menu_button)
            y += 32

    def kill_active_critter_buttons(self):
        for button in self.active_critter_buttons:
            button.kill()
        self.active_critter_buttons = []

    def kill_critter_buttons(self):
        for button in self.critter_buttons:
            button.kill()
        self.critter_buttons = []

    def kill_menu_buttons(self):
        for button in self.menu_buttons:
            button.kill()
        self.menu_buttons = []

    @classmethod
    def text_for_critter(self, critter):
        return (
            f"{critter.name} lvl {critter.level} {critter.current_hp}/{critter.max_hp}"
        )

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
