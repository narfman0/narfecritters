from random import Random

from dataclasses import dataclass


@dataclass
class Stats:
    hp: int = 0
    attack: int = 0
    defense: int = 0
    spattack: int = 0
    spdefense: int = 0
    speed: int = 0

    @classmethod
    def create_random_ivs(cls, random: Random):
        return Stats(
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
        )


@dataclass
class EncounterStages(Stats):
    evasion: int = 0
    accuracy: int = 0
