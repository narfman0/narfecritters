from dataclasses import dataclass


@dataclass
class NPC:
    x: int
    y: int


@dataclass
class Pokemon:
    hp: int
    attack: int
    defense: int
    spattack: int
    spdefense: int
    speed: int
