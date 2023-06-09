import logging
from enum import Enum

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements import UIButton

from narfecritters.game.world import World
from narfecritters.models.items import ItemType
from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.move_select_screen import MoveSelectScreen
from narfecritters.ui.settings import WINDOW_SIZE


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
        self.initialize_background()
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
                    if self.world.player.has_item(ItemType.BALL):
                        self.information_queue.extend(
                            self.world.catch(ItemType.BALL).information
                        )
                    else:
                        self.information_queue.append("Not enough balls to catch!")
                    self.initialize_information_elements()
            elif event.ui_element in self.fight_buttons:
                self.kill_fight_buttons()
                result = self.world.turn(event.ui_element.move)
                self.information_queue.extend(result.information)
                if result.fainted:
                    self.reload_self_critter_image()
                self.initialize_information_elements()
            elif event.ui_element in self.critter_buttons:
                self.kill_critter_buttons()
                critter = event.ui_element.critter
                self.world.encounter.active_player_critter = critter
                self.reload_self_critter_image()
                information: list[str] = []
                active_critter = self.world.active_critter
                self.world.turn_step(  # TODO need to call turn to calculate poison+burn etc here
                    defender=active_critter,
                    attacker=self.world.enemy,
                    attacker_encounter_stages=self.world.encounter.enemy_stat_stages,
                    defender_encounter_stages=self.world.encounter.player_stat_stages,
                    information=information,
                )
                if active_critter.fainted:
                    # TODO itd be nice to do this after the information elements catch up
                    self.reload_self_critter_image()
                self.information_queue.extend(information)
                self.initialize_information_elements()
            elif event.ui_element in self.information_elements:
                last_information = self.information_queue.pop(0)
                self.kill_information_elements()
                if self.information_queue:
                    self.initialize_information_elements()
                elif self.world.encounter is None:
                    self.screen_manager.pop()
                else:
                    self.initialize_menu_buttons()
                if "leveled up to" in last_information:
                    # TODO hack: Need to enrich information queue with a struct that describes a trigger
                    # for other screen or things. It doesn't exist right now though, and while useful in general,
                    # this is the only specific thing I need this for right now. Consider refactoring.
                    if len(self.world.active_critter.moves) > 4:
                        self.screen_manager.push(
                            MoveSelectScreen(
                                screen_manager=self.screen_manager,
                                ui_manager=self.ui_manager,
                                world=self.world,
                            )
                        )

    def init(self):
        if self.information_queue:
            self.initialize_information_elements()
        elif self.world.encounter is None:
            self.screen_manager.pop()
        else:
            self.initialize_menu_buttons()

    def initialize_background(self):
        self.background_image = pygame.image.load(
            "data/images/battles/grass.png"
        ).convert()
        width, height = self.background_image.get_size()
        background_x = WINDOW_SIZE[0] // 2 - width // 2
        background_y = WINDOW_SIZE[1] // 2 - height // 2
        self.background_xy = (background_x, background_y)

    def initialize_information_elements(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        information_text = self.information_queue[0]
        LOGGER.info(information_text)
        self.information_elements.append(
            UIButton(
                (32, y),
                information_text,
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
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
        for menu_option in MenuOptions:
            menu_button = UIButton(
                (WINDOW_SIZE[0] - 128, y), menu_option.name, manager=self.ui_manager
            )
            self.menu_buttons.append(menu_button)
            y += 32

    def initialize_critter_buttons(self):
        y = WINDOW_SIZE[1] - 220
        for critter_uuid in self.world.player.active_critters:
            critter = self.world.player.find_critter_by_uuid(critter_uuid)
            self.critter_buttons.append(
                UIButton(
                    (WINDOW_SIZE[0] - 128, y),
                    critter.name,
                    manager=self.ui_manager,
                )
            )
            self.critter_buttons[-1].critter = critter
            y += 32

    def initialize_fight_buttons(self):
        y = WINDOW_SIZE[1] - (len(MenuOptions) + 1) * 32
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
            self.fight_buttons[-1].move = critters_move
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
        surface.blit(self.background_image, self.background_xy)
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
