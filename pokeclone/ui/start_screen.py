import logging

import pygame
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton

from pokeclone.ui.overworld_screen import OverworldScreen
from pokeclone.ui.screen import Screen, ScreenManager
from pokeclone.ui.settings import WINDOW_SIZE
from pokeclone.world import World


LOGGER = logging.getLogger(__name__)
GREETING_TEXT_1 = "Hello and welcome to pokeclone, a fan-made version of pokemon!"
GREETING_TEXT_2 = "Please select your pokemon from the below list to get started."


class StartScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        self.screen_manager = screen_manager
        self.world = World()

        self.to_kill.extend(
            [
                UIButton((0, 0), GREETING_TEXT_1),
                UIButton((0, 32), GREETING_TEXT_2),
            ]
        )

        self.buttons = []
        y = WINDOW_SIZE[1] // 2
        candidate_starters = [
            self.world.pokedex.find_by_id(id) for id in [1, 4, 7, 25, 133]
        ]
        for candidate_starter_pokemon in candidate_starters:
            self.buttons.append(
                UIButton(
                    (
                        WINDOW_SIZE[0] / 2,
                        y,
                    ),
                    candidate_starter_pokemon.name,
                )
            )
            y += 32
        self.to_kill.extend(self.buttons)

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.buttons:
                pokemon_name = event.ui_element.text
                LOGGER.info(f"{pokemon_name} chosen! Congratulations!")
                pokemon = self.world.pokedex.create(
                    self.world.random, pokemon_name, level=4
                )
                self.world.player.pokemon.append(pokemon)
                self.screen_manager.pop()
                self.screen_manager.push(
                    OverworldScreen(self.screen_manager, self.world)
                )
                self.kill()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
