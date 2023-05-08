import logging
from enum import Enum

from pygame_gui import UI_BUTTON_PRESSED

from narfecritters.ui.pause.save_screen import SaveScreen


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
