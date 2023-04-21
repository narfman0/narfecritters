import copy
from enum import Enum

from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


class Type(Enum):
    NORMAL = 1
    FIRE = 2
    GRASS = 5
    POISON = 8


@dataclass
class NPC:
    x: int
    y: int
    pokemon: list


@dataclass
class Move:
    name: str
    power: int


@dataclass
class Pokemon:
    name: str
    max_hp: int
    current_hp: int
    attack: int
    defense: int
    spattack: int
    spdefense: int
    speed: int
    types: list[Type]
    level: int = field(default=False, init=False)


def attack(attacker: Pokemon, defender: Pokemon, move: Move):
    return (
        round(
            (
                (round((2 * attacker.level) / 5) + 2)
                * move.power
                * round(attacker.attack / defender.defense)
            )
            / 50
        )
        + 2
    )


@dataclass
class Pokedex(YAMLWizard):
    pokemon: list[Pokemon]

    @classmethod
    def load(cls):
        return Pokedex.from_yaml_file(f"data/pokemon.yml")

    def find(self, name):
        for pokemon in self.pokemon:
            if pokemon.name == name:
                return pokemon

    def create(self, name, level) -> Pokemon:
        instance = copy.copy(self.find(name))
        instance.level = level
        return instance
