import logging
from enum import Enum

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements import UIButton

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


class MenuOptions(Enum):
    FIGHT = 1
    CATCH = 2
    CRITTERS = 3
    RUN = 4


class BattleScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.menu_buttons: list[UIButton] = []
        self.information_elements: list[UIElement] = []
        self.information_queue: list[str] = [
            f"You are fighting a level {self.world.enemy.level} {self.world.enemy.name}"
        ]
        self.fight_buttons: list[UIButton] = []
        self.critter_buttons: list[UIButton] = []
        self.enemy_critters_image = self.load_scaled_critters_image(world.enemy.id, 4)
        self.reload_self_critter_image()
        self.initialize_information_elements()

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.menu_buttons:
                self.kill_menu_buttons()
                if event.ui_element.text == MenuOptions.FIGHT.name:
                    self.initialize_fight_buttons()
                if event.ui_element.text == MenuOptions.RUN.name:
                    self.information_queue.extend(self.world.run().information)
                    self.initialize_information_elements()
                if event.ui_element.text == MenuOptions.CRITTERS.name:
                    self.initialize_critter_buttons()
                if event.ui_element.text == MenuOptions.CATCH.name:
                    self.information_queue.extend(self.world.catch().information)
                    self.initialize_information_elements()
            elif event.ui_element in self.fight_buttons:
                self.kill_fight_buttons()
                move_name = event.ui_element.move_name
                result = self.world.turn(move_name)
                self.information_queue.extend(result.information)
                if result.fainted:
                    self.reload_self_critter_image()
                self.initialize_information_elements()
            elif event.ui_element in self.critter_buttons:
                self.kill_critter_buttons()
                critter_idx = event.ui_element.critter_index
                self.world.encounter.active_critter_index = critter_idx
                self.reload_self_critter_image()
                information: list[str] = []
                fainted = self.world.turn_enemy(information)
                if fainted:
                    # TODO itd be nice to do this after the information elements catch up
                    self.reload_self_critter_image()
                self.information_queue.extend(information)
                self.initialize_information_elements()
            elif event.ui_element in self.information_elements:
                self.information_queue.pop(0)
                self.kill_information_elements()
                if self.information_queue:
                    self.initialize_information_elements()
                elif self.world.encounter is None:
                    self.screen_manager.pop()
                else:
                    self.initialize_menu_buttons()

    def initialize_information_elements(self):
        y = WINDOW_SIZE[1] - 156

        self.information_elements.append(
            UIButton(
                (32, y),
                self.information_queue[0],
                self.ui_manager,
            )
        )
        self.information_elements.append(
            UIButton(
                (WINDOW_SIZE[0] - 128, y),
                "OK",
                self.ui_manager,
            )
        )

    def initialize_menu_buttons(self):
        y = WINDOW_SIZE[1] - 156
        for menu_option in MenuOptions:
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), menu_option.name, manager=self.ui_manager
            )
            self.menu_buttons.append(menu_button)
            y += 32

    def initialize_critter_buttons(self):
        y = WINDOW_SIZE[1] - 220
        for critter_idx in self.world.player.active_critters:
            critter = self.world.player.critters[critter_idx]
            self.critter_buttons.append(
                UIButton(
                    (WINDOW_SIZE[0] - 128, y),
                    critter.name_pretty,
                    manager=self.ui_manager,
                )
            )
            self.critter_buttons[-1].critter_index = critter_idx
            y += 32

    def initialize_fight_buttons(self):
        y = WINDOW_SIZE[1] - 156
        for critters_move in self.world.active_critter.moves:
            if len(self.fight_buttons) >= 4:
                LOGGER.warn(f"Critter has move than 4 moves!")
                continue
            self.fight_buttons.append(
                UIButton(
                    (WINDOW_SIZE[0] - 128, y),
                    critters_move.name_pretty,
                    manager=self.ui_manager,
                )
            )
            self.fight_buttons[-1].move_name = critters_move.name
            y += 32

    def kill(self):
        self.kill_menu_buttons()
        self.kill_fight_buttons()
        self.kill_critter_buttons()
        self.kill_information_elements()

    def kill_menu_buttons(self):
        self.kill_elements(self.menu_buttons)

    def kill_fight_buttons(self):
        self.kill_elements(self.fight_buttons)

    def kill_critter_buttons(self):
        self.kill_elements(self.critter_buttons)

    def kill_information_elements(self):
        self.kill_elements(self.information_elements)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
        surface.blit(
            self.enemy_critters_image,
            (
                WINDOW_SIZE[0] - self.enemy_critters_image.get_width(),
                0,
            ),
        )
        trainer_critters_img_pos = (
            0,
            WINDOW_SIZE[1] - self.self_critters_image.get_height(),
        )
        surface.blit(self.self_critters_image, trainer_critters_img_pos)

    def reload_self_critter_image(self):
        if self.world.active_critter:
            self.self_critters_image = self.load_scaled_critters_image(
                self.world.active_critter.id, 5, back=True
            )

    @classmethod
    def load_scaled_critters_image(cls, id, scale, back=False):
        back_str = "back" if back else "front"
        image = pygame.image.load(
            f"data/sprites/critters/{back_str}/{id}.png"
        ).convert()
        size = image.get_size()
        return pygame.transform.scale(
            image, (int(size[0] * scale), int(size[1] * scale))
        )
