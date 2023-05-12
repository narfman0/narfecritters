import logging
from enum import Enum, auto

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.ui.util import text_for_critter
from narfecritters.game.world import World, POTION_HEAL_AMOUNT
from narfecritters.models.items import ItemType
from narfecritters.models import ACTIVE_CRITTERS_MAX

LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    POTION = auto()
    BALL = auto()
    MONEY = auto()
    BACK = auto()


class ItemScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.menu_buttons: list[UIButton] = []
        self.active_critter_buttons: list[UIButton] = []
        self.active_item_type: ItemType = None
        self.init()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.menu_option == MenuOptions.BACK:
                    self.screen_manager.pop()
                if event.ui_element.menu_option == MenuOptions.POTION:
                    self.active_item_type = ItemType.POTION
                    self.initialize_active_critter_buttons()
                if event.ui_element.menu_option == MenuOptions.BALL:
                    self.active_item_type = ItemType.BALL
                    self.kill_active_critter_buttons()
                if event.ui_element.menu_option == MenuOptions.MONEY:
                    self.active_item_type = None
                    self.kill_active_critter_buttons()
            if event.ui_element in self.active_critter_buttons:
                if self.active_item_type is None:
                    LOGGER.warn("No item active to use!")
                    return
                if not self.world.player.has_item(self.active_item_type):
                    LOGGER.warn("Not enough of item for use!")
                    return
                critter_slot_idx = event.ui_element.critter_slot_idx
                if len(self.world.player.active_critters) <= critter_slot_idx:
                    return
                self.world.player.remove_item(self.active_item_type)
                if self.active_item_type == ItemType.POTION:
                    critter = self.world.player.critters[critter_slot_idx]
                    critter.add_current_hp(POTION_HEAL_AMOUNT)
                    LOGGER.warn(f"Healed {critter.name}")
                self.reinit()

    def init(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        for menu_option in MenuOptions:
            text = menu_option.name
            if menu_option is MenuOptions.POTION:
                text += f" ({self.world.player.get_item_count(ItemType.POTION)})"
            elif menu_option is MenuOptions.BALL:
                text += f" ({self.world.player.get_item_count(ItemType.BALL)})"
            elif menu_option is MenuOptions.MONEY:
                text = f"{self.world.player.money}$"
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), text, manager=self.ui_manager
            )
            menu_button.menu_option = menu_option
            self.menu_buttons.append(menu_button)
            y += 32

    def initialize_active_critter_buttons(self):
        y = 32
        for critter_slot_idx in range(ACTIVE_CRITTERS_MAX):
            text = None
            if critter_slot_idx >= len(self.world.player.active_critters):
                text = "-"
            else:
                critter = self.world.player.find_critter_by_uuid(
                    self.world.player.active_critters[critter_slot_idx]
                )
                text = text_for_critter(critter)
            button = UIButton(
                relative_rect=pygame.Rect(32, y, WINDOW_SIZE[0] // 3, 32),
                text=text,
                manager=self.ui_manager,
            )
            button.critter_slot_idx = critter_slot_idx
            self.active_critter_buttons.append(button)
            y += 32

    def kill(self):
        self.kill_elements(self.menu_buttons)
        self.kill_active_critter_buttons()

    def kill_active_critter_buttons(self):
        self.kill_elements(self.active_critter_buttons)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
