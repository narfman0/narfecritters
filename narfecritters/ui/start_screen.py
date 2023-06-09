import logging

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.area_screen import AreaScreen
from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE, SETTINGS
from narfecritters.game.world import DEFAULT_AREA, World


LOGGER = logging.getLogger(__name__)
GREETING_TEXT_1 = "Hello and welcome to narfecritters, a critter capturing game!"
GREETING_TEXT_2 = "Please select your critter from the below list to get started."


class StartScreen(Screen):
    def __init__(self, ui_manager: UIManager, screen_manager: ScreenManager):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = World()

        self.greeting_elements = [
            UIButton((0, 0), GREETING_TEXT_1, manager=self.ui_manager),
            UIButton((0, 32), GREETING_TEXT_2, manager=self.ui_manager),
        ]

        self.buttons: list[UIButton] = []
        y = WINDOW_SIZE[1] // 2
        candidate_starters = [
            self.world.encyclopedia.find_by_id(id)
            for id in SETTINGS.candidate_starter_species
        ]
        for candidate_starter_species in candidate_starters:
            button = UIButton(
                (
                    WINDOW_SIZE[0] / 2,
                    y,
                ),
                candidate_starter_species.name_pretty,
                manager=self.ui_manager,
            )
            button.species = candidate_starter_species
            self.buttons.append(button)
            y += 32

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.buttons:
                species = event.ui_element.species
                critter = self.world.encyclopedia.create(
                    self.world.random,
                    self.world.moves,
                    id=species.id,
                    level=5,
                )
                LOGGER.info(f"{critter.name} chosen! Congratulations!")
                self.world.player.add_critter(critter)
                self.screen_manager.pop()
                self.screen_manager.push(
                    AreaScreen(
                        self.ui_manager,
                        self.screen_manager,
                        self.world,
                        DEFAULT_AREA,
                    )
                )

    def kill(self):
        self.kill_elements(self.buttons + self.greeting_elements)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
