import logging
from enum import Enum, auto

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.pause.critters_screen import text_for_critter
from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World
from narfecritters.models import ACTIVE_CRITTERS_MAX

LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    CRITTER = auto()
    BACK = auto()


class SellScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.menu_buttons: list[UIButton] = []
        self.active_critter_buttons: list[UIButton] = []
        self.init()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.text == MenuOptions.CRITTER.name:
                    if len(self.world.player.critters) <= 1:
                        LOGGER.warn("Can't sell all your critters!")
                    else:
                        self.initialize_active_critter_buttons()
                if event.ui_element.text == MenuOptions.BACK.name:
                    self.screen_manager.pop()
            if event.ui_element in self.active_critter_buttons:
                critter_uuid = event.ui_element.critter_uuid
                critter = self.world.player.find_critter_by_uuid(critter_uuid)
                if not critter:
                    return
                critter_worth = event.ui_element.critter_worth
                self.world.player.money += critter_worth
                LOGGER.info(f"Sold critter for ${critter_worth}")
                self.reinit()

    def init(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        for menu_option in MenuOptions:
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), menu_option.name, manager=self.ui_manager
            )
            self.menu_buttons.append(menu_button)
            y += 32

    def initialize_active_critter_buttons(self):
        y = 32
        for critter_slot_idx in range(ACTIVE_CRITTERS_MAX):
            text = None
            critter_worth = 0
            if critter_slot_idx >= len(self.world.player.active_critters):
                text = "-"
            else:
                critter = self.world.player.find_critter_by_uuid(
                    self.world.player.active_critters[critter_slot_idx]
                )
                critter_worth = 50 * critter.level  # TODO tweak algorithm
                text = f"{text_for_critter(critter)} - {critter_worth}"
            button = UIButton(
                relative_rect=pygame.Rect(32, y, WINDOW_SIZE[0] // 3, 32),
                text=text,
                manager=self.ui_manager,
            )
            if critter:
                button.critter_uuid = critter.uuid
                button.critter_worth = critter_worth
            self.active_critter_buttons.append(button)
            y += 32

    def kill(self):
        self.kill_elements(self.active_critter_buttons)
        self.kill_elements(self.menu_buttons)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
