import logging
from enum import Enum, auto

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton
from pygame_gui.core import UIElement

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World
from narfecritters.models.items import ItemType, item_cost

LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    CASH = auto()
    BACK = auto()


class BuyScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.menu_buttons: list[UIButton] = []
        self.inventory_elements: list[UIElement] = []
        self.init()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                if event.ui_element.text == MenuOptions.BACK.name:
                    self.screen_manager.pop()
            if event.ui_element in self.inventory_elements:
                item_type = event.ui_element.item_type
                cost = item_cost(item_type)
                if self.world.player.money >= cost:
                    self.world.player.money -= cost
                    self.world.player.add_item(item_type)
                    LOGGER.info(f"Purchased a {item_type} for ${cost}!")
                    self.reinit()

    def init(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        for menu_option in MenuOptions:
            text = menu_option.name
            if menu_option is MenuOptions.CASH:
                text = f"${self.world.player.money}"
            pos = (WINDOW_SIZE[0] - 128, y)
            menu_button = UIButton(pos, text, self.ui_manager)
            self.menu_buttons.append(menu_button)
            y += 32
        self.initialize_inventory_elements()

    def initialize_inventory_elements(self):
        y = 32
        for item_type in ItemType:
            quantity = self.world.player.inventory.get(item_type, 0)
            cost = item_cost(item_type)
            text = f"{item_type.name.capitalize()}: ({quantity}) ${cost}"
            button = UIButton(
                relative_rect=pygame.Rect(32, y, WINDOW_SIZE[0] // 3, 32),
                text=text,
                manager=self.ui_manager,
            )
            button.item_type = item_type
            self.inventory_elements.append(button)
            y += 32

    def kill(self):
        self.kill_elements(self.menu_buttons)
        self.kill_elements(self.inventory_elements)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
