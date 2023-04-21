from pygame.event import Event
from pygame.surface import Surface

from pokeclone.ui.settings import WINDOW_SIZE


class Screen:
    def __init__(self):
        self.background = Surface(WINDOW_SIZE)
        self.background.fill("gray")

    def process_event(self, event: Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface: Surface):
        pass


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
