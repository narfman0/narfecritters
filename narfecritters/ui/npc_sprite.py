from enum import Enum

import pygame


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class NPCSprite(pygame.sprite.Sprite):
    SUBFRAMES_PER_FRAME = 8

    def __init__(self, sprite_name, scale=1, offset=(0, 0)):
        super(NPCSprite, self).__init__()
        self.sprite_name = sprite_name
        self.offset = offset

        self.images: dict[list[pygame.Surface]] = {}
        for direction in Direction:
            self.images[direction] = []
            for i in range(4):
                filename = f"{direction.name.lower()}{i}.png"
                path = f"data/sprites/npcs/{sprite_name}/{filename}"
                image = pygame.image.load(path).convert_alpha()
                if scale != 1:
                    width, height = image.get_size()
                    image = pygame.transform.scale(
                        image, (int(width * scale), int(height * scale))
                    )
                self.images[direction].append(image)

        self.index = 0
        self.moving = False
        self.subframe = 0

        self.active_images = self.images[Direction.DOWN]
        self.image = self.active_images[self.index]
        width, height = self.image.get_size()
        self.rect = pygame.Rect(0, 0, width, height)

    def move(self, up=False, down=False, left=False, right=False):
        self.moving = True
        if left:
            self.change_direction(Direction.LEFT)
        elif right:
            self.change_direction(Direction.RIGHT)
        elif up:
            self.change_direction(Direction.UP)
        elif down:
            self.change_direction(Direction.DOWN)

    def stop(self):
        self.moving = False
        self.index = 0

    def change_direction(self, direction):
        self.active_images = self.images[direction]
        self.index = 0

    def update(self):
        if self.moving:
            if self.subframe == NPCSprite.SUBFRAMES_PER_FRAME:
                self.index += 1
                self.subframe = 0
            else:
                self.subframe += 1

        if self.index >= len(self.active_images):
            self.index = 0

        self.image = self.active_images[self.index]

    def set_position(self, x, y):
        width, height = self.image.get_size()
        self.rect.left = x + self.offset[0] - width // 2
        self.rect.top = y + self.offset[1] - height // 2
