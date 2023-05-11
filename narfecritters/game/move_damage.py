from dataclasses import dataclass
from narfecritters.models import *

TYPES = Types.load()  # this is a trick for performance and usability in tests, refactor
APPLICABILITY = [
    MoveCategory.DAMAGE,
    MoveCategory.DAMAGE_AILMENT,
    MoveCategory.DAMAGE_HEAL,
    MoveCategory.DAMAGE_LOWER,
    MoveCategory.DAMAGE_RAISE,
]


@dataclass
class MoveDamageResult:
    damage: Optional[int] = None
    type_factor: Optional[float] = None


def calculate_base_damage(
    attacker: Critter,
    defender: Critter,
    attacker_encounter_stages: EncounterStages,
    defender_encounter_stages: EncounterStages,
    move: Move,
):
    return (
        round(
            (
                (round((2 * attacker.level) / 5) + 2)
                * move.power
                * round(
                    (attacker.attack * attacker_encounter_stages.attack_multipler)
                    / (defender.defense * defender_encounter_stages.defense_multipler)
                )
            )
            / 50
        )
        + 2
    )


def calculate_type_factor(defender: Critter, move: Move):
    type_factor = 1
    for type_id in defender.type_ids:
        if move.type_id in TYPES.find_by_id(type_id).double_damage_from:
            type_factor *= 2
        if move.type_id in TYPES.find_by_id(type_id).half_damage_from:
            type_factor /= 2
        if move.type_id in TYPES.find_by_id(type_id).no_damage_from:
            type_factor *= 0
    return type_factor


def calculate_move_damage(
    attacker: Critter,
    defender: Critter,
    attacker_encounter_stages: EncounterStages,
    defender_encounter_stages: EncounterStages,
    move: Move,
    random: Random,
) -> Optional[MoveDamageResult]:
    """Follows gen5 dmg formula as defined: https://bulbapedia.bulbagarden.net/wiki/Damage#Generation_V_onward"""
    if move.category not in APPLICABILITY:
        return
    if move.power is None:
        print(
            f"Move {move.name} is trying to calculate damage, but the move has no power!"
        )
        return
    base_damage = calculate_base_damage(
        attacker, defender, attacker_encounter_stages, defender_encounter_stages, move
    )
    # TODO critical hits in gen5 use interesting stages, leaving at stage +0 for now
    # see https://bulbapedia.bulbagarden.net/wiki/Critical_hit for implementation details
    critical_hit_scalar = 1 if random.random() > 0.0625 else 2
    random_factor = random.random() * 0.15 + 0.85
    stab = 1.5 if move.type_id in attacker.type_ids else 1
    type_factor = calculate_type_factor(defender, move)
    dmg = round(base_damage * critical_hit_scalar * random_factor * stab * type_factor)
    return MoveDamageResult(damage=dmg, type_factor=type_factor)
