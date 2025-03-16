from __future__ import annotations

from _collections_abc import dict_items, dict_keys, dict_values
from collections.abc import Iterator
from math import ceil

import colex
from charz import Sprite, Label, Vec2, text, clamp

from .item import Item, ItemID


type Count = int
type Tags = list[type | object]


_UI_Z_INDEX: int = 5
_UI_OFFSET: int = -50


class Inventory(Sprite):
    z_index = _UI_Z_INDEX
    position = Vec2(_UI_OFFSET, 0)
    # color = colex.from_hex(background="#24ac2d")
    color = colex.BOLD + colex.WHITE

    def __init__(self, content: dict[ItemID, tuple[Count, Tags]]) -> None:
        self.inner = {
            item_id: Item(item_id, count, tags)
            for item_id, (count, tags) in content.items()
        }
        self._update_texture()

    def update(self, _delta: float) -> None:
        # Remove items that has a count of 0
        for item_name, item in tuple(self.inner.items()):
            if item.count == 0:
                del self.inner[item_name]
            elif item.count < 0:
                raise ValueError(f"Item {repr(item)} has negative count: {item.count}")
        # Update every frame because inventory items might be mutated
        self._update_texture()

    def _update_texture(self) -> None:
        # Sort by items count
        name_sorted = sorted(
            tuple(self.inner.items()),
            key=lambda pair: pair[0].name,
        )
        count_sorted = sorted(
            name_sorted,
            key=lambda pair: pair[1].count,
            reverse=True,
        )
        self.texture = text.fill_lines(
            [
                f"- {item_id.name.capitalize().replace("_", " ")}: {item.count}"
                for item_id, item in count_sorted
            ]
        )
        self.texture.insert(0, "Inventory:")

    def __getitem__(self, key: ItemID) -> Item:
        return self.inner[key]

    def __setitem__(self, key: ItemID, value: Item) -> None:
        self.inner[key] = value

    def __contains__(self, key: ItemID) -> bool:
        return key in self.inner

    def __iter__(self) -> Iterator[ItemID]:
        return self.inner.__iter__()

    def get[T](self, key: ItemID, *, default: T) -> Item | T:
        return self.inner.get(key, default)

    def keys(self) -> dict_keys[ItemID, Item]:
        return self.inner.keys()

    def values(self) -> dict_values[ItemID, Item]:
        return self.inner.values()

    def items(self) -> dict_items[ItemID, Item]:
        return self.inner.items()


# TODO: Move sounds to `InfoBar` (and subclasses) using hooks
class InfoBar(Label):
    MAX_VALUE: float = 100
    MAX_CELL_COUNT: int = 10
    z_index = _UI_Z_INDEX
    label: str = "<Unset>"
    cell_char: str = "#"
    cell_fill: str = " "
    color = colex.ITALIC + colex.WHITE
    _value: float = 0

    def __init__(self) -> None:
        self.value = self.MAX_VALUE

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = clamp(value, 0, self.MAX_VALUE)
        percent = self._value / self.MAX_VALUE
        count = ceil(self.MAX_CELL_COUNT * percent)
        progress = (self.cell_char * count).ljust(self.MAX_CELL_COUNT, self.cell_fill)
        self.text = f"[{progress}]> {self.label}"

    def fill(self) -> None:
        self.value = self.MAX_VALUE


class HealthBar(InfoBar):
    MAX_VALUE = 100
    position = Vec2(_UI_OFFSET, -5)
    label = "Health"
    color = colex.PALE_VIOLET_RED


class OxygenBar(InfoBar):
    MAX_VALUE = 30
    position = Vec2(_UI_OFFSET, -4)
    label = "O2"
    color = colex.AQUAMARINE


class HungerBar(InfoBar):
    MAX_VALUE = 120
    position = Vec2(_UI_OFFSET, -3)
    label = "Food"
    color = colex.SANDY_BROWN


class ThirstBar(InfoBar):
    MAX_VALUE = 90
    position = Vec2(_UI_OFFSET, -2)
    label = "Thirst"
    color = colex.AQUA
