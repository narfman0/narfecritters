import logging
from enum import Enum

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.pause.save_screen import SaveScreen
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.db.models import Save
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    BACK = 1


class LoadScreen(SaveScreen):
    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.text == MenuOptions.BACK.name:
                    self.screen_manager.pop()
            if event.ui_element in self.slot_buttons:
                slot_index = event.ui_element.slot_index
                self.world.player = self.save.players[slot_index]
                self.screen_manager.pop()
                self.screen_manager.pop()
