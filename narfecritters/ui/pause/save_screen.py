import logging
from enum import Enum

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.models import Save
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    BACK = 1


class SaveScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.save = Save.load()
        self.menu_buttons: list[UIButton] = []
        self.slot_buttons: list[UIButton] = []
        self.init()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.text == MenuOptions.BACK.name:
                    self.screen_manager.pop()
            if event.ui_element in self.slot_buttons:
                slot_index = event.ui_element.slot_index
                self.save.players[slot_index] = self.world.player
                self.save.save()
                self.reinit()

    def initialize_slot_buttons(self):
        y = 32
        idx = 0
        for player in self.save.players:
            text = "-"
            if player:
                text = f"{len(player.critters)}, {player.x}/{player.y}"
            button = UIButton(
                (32, y),
                text=text,
                manager=self.ui_manager,
            )
            button.slot_index = idx
            self.slot_buttons.append(button)
            y += 32
            idx += 1

    def initialize_menu_buttons(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        for menu_option in MenuOptions:
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), menu_option.name, manager=self.ui_manager
            )
            self.menu_buttons.append(menu_button)
            y += 32

    def init(self):
        self.initialize_menu_buttons()
        self.initialize_slot_buttons()

    def kill(self):
        self.kill_elements(self.slot_buttons)
        self.kill_elements(self.menu_buttons)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
