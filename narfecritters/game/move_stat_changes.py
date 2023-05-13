from narfecritters.models import *


def calculate_move_stat_changes(
    attacker: Critter,
    defender: Critter,
    attacker_encounter_stages: EncounterStages,
    defender_encounter_stages: EncounterStages,
    move: Move,
    information: list[str],
):
    if not move.stat_changes:
        return
    for stat_change in move.stat_changes:
        if move.target in [
            MoveTarget.ALL_CRITTERS,
            MoveTarget.ENTIRE_FIELD,
            MoveTarget.ALL_OPPONENTS,
            MoveTarget.OPPONENTS_FIELD,
            MoveTarget.RANDOM_OPPONENT,
            MoveTarget.ALL_OTHER_CRITTERS,
        ]:
            current_stat = getattr(defender_encounter_stages, stat_change.name)
            setattr(
                defender_encounter_stages,
                stat_change.name,
                current_stat + stat_change.amount,
            )
            information.append(
                f"{stat_change.name.capitalize()} changed for {defender.name}"
            )
        if move.target in [
            MoveTarget.ALL_CRITTERS,
            MoveTarget.ENTIRE_FIELD,
            MoveTarget.ALL_ALLIES,
            MoveTarget.USER_AND_ALLIES,
            MoveTarget.USER,
            MoveTarget.USER_OR_ALLY,
            MoveTarget.SELECTED_CRITTERS_ME_FIRST,
            MoveTarget.ALLY,
        ]:
            current_stat = getattr(attacker_encounter_stages, stat_change.name)
            setattr(
                attacker_encounter_stages,
                stat_change.name,
                current_stat + stat_change.amount,
            )
            information.append(
                f"{stat_change.name.capitalize()} changed for {attacker.name}"
            )
