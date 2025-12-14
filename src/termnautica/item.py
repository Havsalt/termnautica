"""This file contains an enum with all items.

Some items has extra data associated with them, which is defined using multiple dicts.
These lookups includes which slot they go in, how much food, thirst and healing they restore.

This is basically the item DB of the game.
- Would be cool to use TOML for this...
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, StrEnum, auto, unique
from typing import NewType, Protocol


type Count = int  # Positive
type Change = float
type NonNegative = int
"""Positive `Integer`, including `0`; `[0, INF>`"""


@dataclass(kw_only=True, frozen=True, slots=True)
class Recipe:
    products: dict[ItemID, Count]
    ingredients: dict[ItemID, Count]


@unique
class ItemID(StrEnum):
    def __hash__(self) -> int:
        return id(self)

    # Plain items
    GOLD_ORE = auto()
    GOLD_BAR = auto()
    TITANIUM_ORE = auto()
    TITANIUM_BAR = auto()
    COPPER_ORE = auto()
    COPPER_BAR = auto()
    IRON_ORE = auto()
    IRON_BAR = auto()
    IRON_PLATE = auto()
    COAL_ORE = auto()
    STEEL_BAR = auto()
    KELP = auto()
    FABRIC = auto()
    STRING = auto()
    CRYSTAL = auto()
    DIAMOND = auto()
    STEEL_THREAD = auto()
    # Foods, drinks and healing items
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
    CHOCOLATE = auto()
    # Items that go into slots
    SHARP_ROCK = auto()  # Knife model
    BASIC_KNIFE = auto()
    STEEL_KNIFE = auto()
    O2_TANK = auto()
    HIGH_CAPACITY_O2_TANK = auto()
    BASIC_DIVING_MASK = auto()
    IMPROVED_DIVING_MASK = auto()
    BASIC_SUITE = auto()
    ADVANCED_SUITE = auto()
    MAKESHIFT_HARPOON = auto()
    STEEL_HARPOON = auto()


@unique
class Slot(Enum):
    MASK = auto()
    SUITE = auto()
    TANK = auto()
    MELEE = auto()
    RANGED = auto()


# NOTE: Implement these manually - And add them to type alias
Damage = NewType("Damage", float)
BreathReduction = NewType("BreathReduction", float)
PressureReduction = NewType("PressureReduction", float)
CriticalDepth = NewType("CriticalDepth", float)

type GearStat = Damage | BreathReduction | PressureReduction | CriticalDepth

# Only 1 gear item can be equipped in a slot, and gear can only provide 1 stat
# The associated value is therefore wrapped in a `NewType` based on what it represents
gear: dict[ItemID, tuple[Slot, GearStat]] = {
    ItemID.SHARP_ROCK: (
        Slot.MELEE,
        Damage(2),
    ),
    ItemID.BASIC_KNIFE: (
        Slot.MELEE,
        Damage(3),
    ),
    ItemID.STEEL_KNIFE: (
        Slot.MELEE,
        Damage(4),
    ),
    ItemID.BASIC_DIVING_MASK: (
        Slot.MASK,
        BreathReduction(0.7),
    ),
    ItemID.IMPROVED_DIVING_MASK: (
        Slot.MASK,
        BreathReduction(0.5),
    ),
    ItemID.BASIC_SUITE: (
        Slot.SUITE,
        CriticalDepth(40),  # Second depth layer
    ),
    ItemID.ADVANCED_SUITE: (
        Slot.SUITE,
        CriticalDepth(60),  # Third depth layer
    ),
    ItemID.O2_TANK: (
        Slot.TANK,
        PressureReduction(0.7),
    ),
    ItemID.HIGH_CAPACITY_O2_TANK: (
        Slot.TANK,
        PressureReduction(0.5),
    ),
    ItemID.MAKESHIFT_HARPOON: (Slot.RANGED, Damage(3)),
}


@unique
class ConsumableStat(Enum):
    HUNGER = auto()
    THIRST = auto()
    HEALING = auto()


# Consumable items and what they influence
consumables: dict[ItemID, dict[ConsumableStat, Change]] = {
    ItemID.BLADDER_FISH: {
        ConsumableStat.HUNGER: 16,
        ConsumableStat.THIRST: 20,
    },
    ItemID.GOLD_FISH: {
        ConsumableStat.HUNGER: 14,
    },
    ItemID.FRIED_FISH_NUGGET: {
        ConsumableStat.HUNGER: 27,
    },
    ItemID.COD: {
        ConsumableStat.HUNGER: 18,
    },
    ItemID.COD_SOUP: {
        ConsumableStat.HUNGER: 24,
        ConsumableStat.THIRST: 41,
    },
    ItemID.SALMON: {
        ConsumableStat.HUNGER: 17,
    },
    ItemID.GRILLED_SALMON: {
        ConsumableStat.HUNGER: 60,
    },
    ItemID.NEMO: {
        ConsumableStat.HUNGER: 999,
    },
    ItemID.WATER_BOTTLE: {
        ConsumableStat.THIRST: 45,
    },
    ItemID.BANDAGE: {
        ConsumableStat.HEALING: 30,
    },
    ItemID.MEDKIT: {
        ConsumableStat.HEALING: 70,
    },
    ItemID.CHOCOLATE: {
        ConsumableStat.HEALING: 18,
        ConsumableStat.HUNGER: 23,
    },
}


class Container(Protocol):
    def ids(self) -> tuple[ItemID, ...]: ...
    def slot_count(self) -> Count: ...
    def has(self, item: ItemID) -> bool: ...
    def count(self, item: ItemID) -> Count: ...
    def set(self, item: ItemID, count: Count) -> None:
        """Has to remove items with count `<= 0`"""

    def take(self, item: ItemID, count: Count) -> None:
        """Has to remove items with count `<= 0`"""

    def give(self, item: ItemID, count: Count) -> None:
        """Has to create item if not exists"""


class SizedInventory:
    def __init__(self, slot_limit: NonNegative | None = None) -> None:
        self._default_dict = defaultdict[ItemID, Count](int)
        self.slot_limit = slot_limit

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.slot_limit=}, content={self._default_dict})"

    def ids(self) -> tuple[ItemID, ...]:
        return tuple(self._default_dict.keys())

    def slot_count(self) -> Count:
        return len(self._default_dict)

    def has(self, item: ItemID) -> bool:
        return item in self._default_dict

    def count(self, item: ItemID) -> Count:
        return self._default_dict[item]

    def set(self, item: ItemID, count: Count) -> None:
        if count == 0:
            del self._default_dict[item]
        else:
            self._default_dict[item] = count

    def take(self, item: ItemID, count: Count) -> None:
        self._default_dict[item] -= count
        if self._default_dict[item] == 0:
            del self._default_dict[item]
        elif self._default_dict[item] < 0:
            raise ValueError(
                f"Item count for `{item}` is less than `0`, got {self._default_dict[item]}"
            )

    def clear(self) -> None:
        self._default_dict.clear()

    def give(self, item: ItemID, count: Count) -> None:
        self._default_dict[item] += count
        if self.slot_limit is not None:
            if len(self._default_dict) > self.slot_limit:
                raise ValueError(
                    f"Slot size exceeded: {len(self._default_dict)} > {self.slot_limit}"
                )
