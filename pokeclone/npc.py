from dataclasses import dataclass


class NPC:
    x: int = 0
    y: int = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
