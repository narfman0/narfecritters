import logging

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UIManager
from pygame_gui.elements import UIButton

from narfecritters.ui.screen import Screen, ScreenManager
from narfecritters.ui.settings import WINDOW_SIZE
from narfecritters.game.world import World


LOGGER = logging.getLogger(__name__)


class BattleScreen(Screen):
    def __init__(
        self, ui_manager: UIManager, screen_manager: ScreenManager, world: World
    ):
        super().__init__(ui_manager)
        self.screen_manager = screen_manager
        self.world = world
        self.fight_buttons = []
        y = WINDOW_SIZE[1] - 156
        for pokemon_move in self.world.active_pokemon.moves:
            if len(self.fight_buttons) >= 4:
                LOGGER.warn(f"Pokemon has move than 4 moves!")
                continue
            self.fight_buttons.append(
                UIButton(
                    (WINDOW_SIZE[0] - 128, y),
                    pokemon_move.name,
                    manager=self.ui_manager,
                )
            )
            y += 32
        self.to_kill.extend(self.fight_buttons)
        self.enemy_pokemon_image = self.load_scaled_pokemon_image(world.enemy.id, 4)
        self.self_pokemon_image = self.load_scaled_pokemon_image(
            world.active_pokemon.id, 5, back=True
        )
        LOGGER.info(
            f"You are fighting a level {self.world.enemy.level} {self.world.enemy.name}"
        )

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element in self.fight_buttons:
                move_name = event.ui_element.text
                self.world.turn(move_name)
                if self.world.encounter is None:
                    self.screen_manager.pop()
                    self.kill()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
        surface.blit(
            self.enemy_pokemon_image,
            (
                WINDOW_SIZE[0] - self.enemy_pokemon_image.get_width(),
                0,
            ),
        )
        trainer_pokemon_img_pos = (
            0,
            WINDOW_SIZE[1] - self.self_pokemon_image.get_height(),
        )
        surface.blit(self.self_pokemon_image, trainer_pokemon_img_pos)

    @classmethod
    def load_scaled_pokemon_image(cls, id, scale, back=False):
        back_str = "back" if back else "front"
        image = pygame.image.load(f"data/sprites/pokemon/{back_str}/{id}.png").convert()
        size = image.get_size()
        return pygame.transform.scale(
            image, (int(size[0] * scale), int(size[1] * scale))
        )
