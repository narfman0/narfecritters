from narfecritters.models.critters import Critter


def text_for_critter(critter: Critter):
    return f"{critter.name} lvl {critter.level} {critter.current_hp}/{critter.max_hp}"
