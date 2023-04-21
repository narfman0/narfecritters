import logging

from pokeclone import settings
from pokeclone.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


"""
* fight pokemon
* final boss
"""
import random

import pygame
from pygame_gui import UIManager, UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton


from pokeclone.world import MOVE_SPEED, World

WINDOW_SIZE = (800, 600)
TILE_SIZE = 16
ENCOUNTER_CHANCE = 0.01


class OverworldScreen:
    def __init__(self):
        self.world = World()
        self.npc_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.npc_surface.fill((255, 0, 0))

    def process_event(self, event):
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self.attack_button:
                print("Hello World!")

    def update(self, dt: float, manager: UIManager):
        if not self.world.in_encounter:
            self.update_overworld_movement()
        self.world.update(dt)

    def draw(self, surface):
        surface.blit(
            self.npc_surface,
            (
                self.world.player.x - TILE_SIZE / 2,
                WINDOW_SIZE[1] - self.world.player.y - TILE_SIZE / 2,
            ),
        )

    def update_overworld_movement(self):
        if (
            pygame.key.get_pressed()[pygame.K_LEFT]
            or pygame.key.get_pressed()[pygame.K_a]
        ) and self.world.player.x > 0:
            self.world.player.x -= MOVE_SPEED
            self.maybe_create_encounter()
        elif (
            pygame.key.get_pressed()[pygame.K_RIGHT]
            or pygame.key.get_pressed()[pygame.K_d]
        ) and self.world.player.x < WINDOW_SIZE[0]:
            self.world.player.x += MOVE_SPEED
            self.maybe_create_encounter()
        if (
            pygame.key.get_pressed()[pygame.K_UP]
            or pygame.key.get_pressed()[pygame.K_w]
        ) and self.world.player.y < WINDOW_SIZE[1]:
            self.world.player.y += MOVE_SPEED
            self.maybe_create_encounter()
        elif (
            pygame.key.get_pressed()[pygame.K_DOWN]
            or pygame.key.get_pressed()[pygame.K_s]
        ) and self.world.player.y > 0:
            self.world.player.y -= MOVE_SPEED
            self.maybe_create_encounter()

    def maybe_create_encounter(self):
        if random.random() > ENCOUNTER_CHANCE or self.world.in_encounter:
            return
        self.world.create_encounter()
        self.attack_button = UIButton(
            (350, 280), f"You are fighting a {self.world.enemy.name}"
        )


def main():
    initialize_logging()
    pygame.init()
    pygame.display.set_caption("pokeclone")
    window_surface = pygame.display.set_mode(WINDOW_SIZE)
    manager = UIManager(WINDOW_SIZE, "data/theme.json")
    background = pygame.Surface(WINDOW_SIZE)
    background.fill((0, 255, 0))

    clock = pygame.time.Clock()
    is_running = True

    screens = [OverworldScreen()]

    while is_running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == UI_BUTTON_PRESSED:
                screens[-1].process_event(event)
            if event.type == pygame.QUIT:
                is_running = False
            manager.process_events(event)

        screens[-1].update(dt, manager)

        manager.update(dt)
        window_surface.blit(background, (0, 0))
        screens[-1].draw(window_surface)
        manager.draw_ui(window_surface)

        pygame.display.update()


if __name__ == "__main__":
    main()
