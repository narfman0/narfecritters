import logging

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.db.models import Area
from narfecritters.ui.area_screen import AreaScreen
from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)
GREETING_TEXT_1 = "Hello and welcome to narfecritters, a critter capturing game!"
GREETING_TEXT_2 = "Please select your critter from the below list to get started."


class StartScreen(Screen):
    def __init__(self, ui_manager: UIManager, screen_manager: ScreenManager):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = World()

        self.to_kill.extend(
            [
                UIButton((0, 0), GREETING_TEXT_1, manager=self.ui_manager),
                UIButton((0, 32), GREETING_TEXT_2, manager=self.ui_manager),
            ]
        )

        self.buttons = []
        y = WINDOW_SIZE[1] // 2
        candidate_starters = [
            self.world.encyclopedia.find_by_id(id) for id in [1, 4, 7, 25, 133]
        ]
        for candidate_starter_critters in candidate_starters:
            self.buttons.append(
                UIButton(
                    (
                        WINDOW_SIZE[0] / 2,
                        y,
                    ),
                    candidate_starter_critters.name,
                    manager=self.ui_manager,
                )
            )
            y += 32
        self.to_kill.extend(self.buttons)

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.buttons:
                critter_name = event.ui_element.text
                LOGGER.info(f"{critter_name} chosen! Congratulations!")
                critters = self.world.encyclopedia.create(
                    self.world.random, critter_name, level=5
                )
                self.world.player.critters.append(critters)
                self.screen_manager.pop()
                self.screen_manager.push(
                    AreaScreen(
                        self.ui_manager,
                        self.screen_manager,
                        self.world,
                        Area.OVERWORLD,
                    )
                )
                self.kill()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))