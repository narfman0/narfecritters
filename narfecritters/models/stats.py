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
    """See https://bulbapedia.bulbagarden.net/wiki/Stat_modifier#Stage_multipliers for details"""

    evasion: int = 0
    accuracy: int = 0
    sleep_turns: int = 0
    confusion_turns: int = 0

    @property
    def attack_multipler(self):
        return self.calculate_stat_multiplier(self.attack)

    @property
    def defense_multipler(self):
        return self.calculate_stat_multiplier(self.defense)

    @property
    def spattack_multipler(self):
        return self.calculate_stat_multiplier(self.spattack)

    @property
    def spdefense_multipler(self):
        return self.calculate_stat_multiplier(self.spdefense)

    @property
    def speed_multipler(self):
        return self.calculate_stat_multiplier(self.speed)

    @property
    def accuracy_multipler(self):
        return self.calculate_evasion_or_accuracy_multiplier(self.accuracy)

    @property
    def evasion_multipler(self):
        return self.calculate_evasion_or_accuracy_multiplier(self.evasion)

    @classmethod
    def calculate_stat_multiplier(cls, stage: int):
        if stage < 0:
            return 2 / (2 - stage)
        else:
            return (2 + stage) / 2

    @classmethod
    def calculate_evasion_or_accuracy_multiplier(cls, stage: int):
        if stage < 0:
            return 3 / (3 - stage)
        else:
            return (3 + stage) / 3
