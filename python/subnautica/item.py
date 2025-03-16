from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto, unique


@dataclass
class Item:
    id: ItemID
    count: int
    tags: list[type] = field(default_factory=list)


@unique
class ItemID(Enum):
    def __hash__(self) -> int:
        return hash(self.name)

    NONE = auto()
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
    COD = auto()
    SALMON = auto()
    WATER_BOTTLE = auto()
