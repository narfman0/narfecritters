import logging
from enum import Enum

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton, UIScrollingContainer

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.models import ACTIVE_CRITTERS_MAX
from narfecritters.models.critters import Critter
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


def text_for_critter(critter: Critter):
    return f"{critter.name} lvl {critter.level} {critter.current_hp}/{critter.max_hp}"


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
        self.init()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.text == MenuOptions.BACK.name:
                    self.screen_manager.pop()
            if event.ui_element in self.active_critter_buttons:
                critter_slot_idx = event.ui_element.critter_slot_idx
                if len(self.world.player.active_critters) <= critter_slot_idx:
                    return
                del self.world.player.active_critters[critter_slot_idx]
                self.reinit()
            if event.ui_element in self.critter_buttons:
                if len(self.world.player.active_critters) >= ACTIVE_CRITTERS_MAX:
                    return
                critter_index = event.ui_element.critter_index
                self.world.player.active_critters.append(critter_index)
                self.reinit()

    def initialize_active_critter_buttons(self):
        y = 32
        for critter_slot_idx in range(ACTIVE_CRITTERS_MAX):
            text = None
            if critter_slot_idx >= len(self.world.player.active_critters):
                text = "-"
            else:
                critter = self.world.player.critters[
                    self.world.player.active_critters[critter_slot_idx]
                ]
                text = text_for_critter(critter)
            button = UIButton(
                relative_rect=pygame.Rect(32, y, WINDOW_SIZE[0] // 3, 32),
                text=text,
                manager=self.ui_manager,
            )
            button.critter_slot_idx = critter_slot_idx
            self.active_critter_buttons.append(button)
            y += 32

    def initialize_critter_buttons(self):
        y = 0
        for idx, critter in enumerate(self.world.player.critters):
            if idx in self.world.player.active_critters:
                continue
            text = self.text_for_critter(critter)
            button = UIButton(
                relative_rect=pygame.Rect(0, y, WINDOW_SIZE[0] // 3 - 16, 32),
                text=text,
                container=self.scrolling_container,
                manager=self.ui_manager,
            )
            button.critter_index = idx
            self.critter_buttons.append(button)
            y += 32

    def initialize_menu_buttons(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        for menu_option in MenuOptions:
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), menu_option.name, manager=self.ui_manager
            )
            self.menu_buttons.append(menu_button)
            y += 32

    def init_scrolling_container(self):
        scrolling_height = (
            len(self.world.player.critters) - len(self.world.player.active_critters)
        ) * 32
        self.scrolling_container = UIScrollingContainer(
            pygame.Rect(
                WINDOW_SIZE[0] // 3 + 32,
                32,
                WINDOW_SIZE[0] // 3,
                WINDOW_SIZE[1] - 64,
            ),
            manager=self.ui_manager,
        )
        self.scrolling_container.set_scrollable_area_dimensions(
            (
                WINDOW_SIZE[0] // 2,
                scrolling_height,
            )
        )

    def init(self):
        self.init_scrolling_container()
        self.initialize_menu_buttons()
        self.initialize_active_critter_buttons()
        self.initialize_critter_buttons()

    def kill(self):
        self.scrolling_container.kill()
        self.kill_active_critter_buttons()
        self.kill_critter_buttons()
        self.kill_menu_buttons()

    def kill_active_critter_buttons(self):
        self.kill_elements(self.active_critter_buttons)

    def kill_critter_buttons(self):
        self.kill_elements(self.critter_buttons)

    def kill_menu_buttons(self):
        self.kill_elements(self.menu_buttons)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
