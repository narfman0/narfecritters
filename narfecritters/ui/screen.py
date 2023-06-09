from pygame.event import Event
from pygame.image import load as load_image
from pygame.surface import Surface
from pygame_gui import UIManager
from pygame_gui.core import UIElement

from narfecritters.ui.settings import WINDOW_SIZE


class Screen:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.background = load_image("data/images/background.png").convert_alpha()

    def init(self):
        pass

    def process_event(self, event: Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface: Surface):
        surface.blit(self.background, (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))

    def kill(self):
        pass

    def reinit(self):
        self.kill()
        self.init()

    @classmethod
    def kill_elements(cls, elements: list[UIElement]):
        for button in elements:
            button.kill()
        elements.clear()


class ScreenManager:
    def __init__(self):
        self.screens: list[Screen] = []

    def push(self, screen: Screen):
        if self.current:
            self.current.kill()
        self.screens.append(screen)

    def pop(self):
        if self.current:
            self.current.kill()
        self.screens.pop()
        if self.current:
            self.current.init()

    @property
    def current(self) -> Screen:
        if self.screens:
            return self.screens[-1]
        return None
