from pygame.event import Event
from pygame.surface import Surface
from pygame_gui import UIManager

from narfecritters.ui.settings import WINDOW_SIZE


class Screen:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.background = Surface(WINDOW_SIZE)
        self.background.fill("gray")
        self.to_kill = []

    def process_event(self, event: Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface: Surface):
        pass

    def kill(self):
        for element_to_kill in self.to_kill:
            element_to_kill.kill()


class ScreenManager:
    def __init__(self):
        self.screens = []

    def push(self, screen: Screen):
        self.screens.append(screen)

    def pop(self):
        self.screens.pop()

    @property
    def current(self) -> Screen:
        return self.screens[-1]
