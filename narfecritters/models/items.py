from enum import Enum

POTION_HEAL_AMOUNT = 20


class ItemType(Enum):
    POTION = 1
    BALL = 10


def item_cost(item_type: ItemType):
    return {ItemType.POTION: 200, ItemType.BALL: 200}[item_type]
