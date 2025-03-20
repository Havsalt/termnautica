from __future__ import annotations

from enum import Enum, auto, unique


type Count = int


@unique
class Stat(Enum):
    EATABLE = auto()
    DRINKABLE = auto()
    HEALING = auto()


@unique
class ItemID(Enum):
    def __hash__(self) -> int:
        return id(self)

    GOLD_ORE = auto()
    GOLD_BAR = auto()
    TITANIUM_ORE = auto()
    TITANIUM_BAR = auto()
    COPPER_ORE = auto()
    COPPER_BAR = auto()
    COAL_ORE = auto()
    KELP = auto()
    BLADDER_FISH = auto()
    GOLD_FISH = auto()
    FRIED_FISH_NUGGET = auto()
    COD = auto()
    COD_SOUP = auto()
    SALMON = auto()
    GRILLED_SALMON = auto()
    NEMO = auto()
    WATER_BOTTLE = auto()
    BANDAGE = auto()
    MEDKIT = auto()


stats: dict[ItemID, dict[Stat, int]] = {
    ItemID.BLADDER_FISH: {
        Stat.EATABLE: 16,
        Stat.DRINKABLE: 20,
    },
    ItemID.GOLD_FISH: {
        Stat.EATABLE: 14,
    },
    ItemID.FRIED_FISH_NUGGET: {
        Stat.EATABLE: 27,
    },
    ItemID.COD: {
        Stat.EATABLE: 18,
    },
    ItemID.COD_SOUP: {
        Stat.EATABLE: 24,
        Stat.DRINKABLE: 25,
    },
    ItemID.SALMON: {
        Stat.EATABLE: 17,
    },
    ItemID.GRILLED_SALMON: {
        Stat.EATABLE: 60,
    },
    ItemID.NEMO: {
        Stat.EATABLE: 999,
    },
    ItemID.WATER_BOTTLE: {
        Stat.DRINKABLE: 45,
    },
    ItemID.BANDAGE: {
        Stat.HEALING: 30,
    },
    ItemID.MEDKIT: {
        Stat.HEALING: 70,
    },
}
