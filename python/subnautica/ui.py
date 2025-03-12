from __future__ import annotations

from _collections_abc import dict_items, dict_keys, dict_values
from collections.abc import Iterator
from dataclasses import dataclass, field
from math import ceil

import colex
from charz import Sprite, Label, Vec2, text


_UI_Z_INDEX: int = 5
_UI_OFFSET: int = -50


@dataclass
class Item:
    name: str
    count: int
    tags: list[type] = field(default_factory=list)


class Inventory(Sprite):
    z_index = _UI_Z_INDEX
    position = Vec2(_UI_OFFSET, 0)
    # color = colex.from_hex(background="#24ac2d")
    color = colex.BOLD + colex.WHITE

    def __init__(self, content: dict[str, int]) -> None:
        self._inner = {
            item_name: Item(item_name, count) for item_name, count in content.items()
        }
        self._update_texture()

    def update(self, _delta: float) -> None:
        # Update every frame because inventory items might be mutated
        self._update_texture()

    def __getitem__(self, key: str) -> Item:
        # if key not in self._inner:
        #     self._inner[key] = Item(key, 0)
        return self._inner[key]

    def __setitem__(self, key: str, value: Item) -> None:
        self._inner[key] = value

    def __contains__(self, key: object) -> bool:
        return key in self._inner

    def __iter__(self) -> Iterator[str]:
        return self._inner.__iter__()

    def keys(self) -> dict_keys[str, Item]:
        return self._inner.keys()

    def values(self) -> dict_values[str, Item]:
        return self._inner.values()

    def items(self) -> dict_items[str, Item]:
        return self._inner.items()

    def _update_texture(self) -> None:
        self.texture = text.fill_lines(
            [
                f"- {item_name.capitalize().replace("_", " ")}: {item.count}"
                for item_name, item in self._inner.items()
            ]
        )
        self.texture.insert(0, "Inventory:")


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
        self._value = max(0, value)  # Min value of 0
        percent = value / self.MAX_VALUE
        count = ceil(self.MAX_CELL_COUNT * percent)
        progress = (self.cell_char * count).ljust(self.MAX_CELL_COUNT, self.cell_fill)
        self.text = f"[{progress}]> {self.label}"

    def fill(self) -> None:
        self.value = self.MAX_VALUE


class HealthBar(InfoBar):
    position = Vec2(_UI_OFFSET, -5)
    label = "Health"
    color = colex.PALE_VIOLET_RED


class OxygenBar(InfoBar):
    MAX_VALUE = 30 * 16  # X seconds
    position = Vec2(_UI_OFFSET, -4)
    label = "O2"
    color = colex.AQUAMARINE


class HungerBar(InfoBar):
    MAX_VALUE = 120 * 16  # X seconds
    position = Vec2(_UI_OFFSET, -3)
    label = "Food"
    color = colex.SANDY_BROWN


class ThirstBar(InfoBar):
    MAX_VALUE = 90 * 16  # X seconds
    position = Vec2(_UI_OFFSET, -2)
    label = "Thirst"
    color = colex.AQUA
