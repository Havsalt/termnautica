from __future__ import annotations

from math import ceil
from typing import MutableMapping

import colex
from charz import Node, Sprite, Label, Vec2, text, clamp

from .item import ItemID


type Count = int


_UI_LEFT_OFFSET: int = -50
_UI_RIGHT_OFFSET: int = 40


class UIElement:
    z_index = 5


class Inventory(UIElement, Sprite):
    position = Vec2(_UI_LEFT_OFFSET, 0)
    # color = colex.from_hex(background="#24ac2d")
    color = colex.BOLD + colex.WHITE

    def __init__(
        self,
        parent: Node,
        inventory_ref: MutableMapping[ItemID, Count],
    ) -> None:
        super().__init__(parent=parent)
        self._inventory_ref = inventory_ref
        self._update_texture()

    def update(self, _delta: float) -> None:
        # Remove items that has a count of 0
        for item, count in tuple(self._inventory_ref.items()):
            if count == 0:
                del self._inventory_ref[item]
            elif count < 0:
                raise ValueError(f"Item {repr(item)} has negative count: {count}")
        # Update every frame because inventory items might be mutated
        self._update_texture()

    def _update_texture(self) -> None:
        # Sort by items count
        name_sorted = sorted(
            self._inventory_ref.items(),
            key=lambda pair: pair[0].name,
        )
        count_sorted = sorted(
            name_sorted,
            key=lambda pair: pair[1],
            reverse=True,
        )
        self.texture = text.fill_lines(
            [
                f"- {item.name.capitalize().replace("_", " ")}: {count}"
                for item, count in count_sorted
            ]
        )
        self.texture.insert(0, "Inventory:")


class HotbarE(UIElement, Label):
    position = Vec2(_UI_RIGHT_OFFSET, -5)
    texture = ["Interact [E".rjust(11)]
    transparency = " "
    color = colex.SALMON


class Hotbar1(UIElement, Label):
    position = Vec2(_UI_RIGHT_OFFSET, -3)
    texture = ["Eat [1".rjust(11)]
    transparency = " "
    color = colex.SANDY_BROWN


class Hotbar2(UIElement, Label):
    position = Vec2(_UI_RIGHT_OFFSET, -2)
    texture = ["Drink [2".rjust(11)]
    transparency = " "
    color = colex.AQUA


class Hotbar3(UIElement, Label):
    position = Vec2(_UI_RIGHT_OFFSET, -1)
    texture = ["Heal [3".rjust(11)]
    transparency = " "
    color = colex.PINK


# TODO: Move sounds to `InfoBar` (and subclasses) using hooks
class InfoBar(UIElement, Label):
    MAX_VALUE: float = 100
    MAX_CELL_COUNT: int = 10
    label: str = "<Unset>"
    cell_char: str = "#"
    cell_fill: str = " "
    color = colex.ITALIC + colex.WHITE
    _value: float = 0

    def __init__(self, parent: Node) -> None:
        super().__init__(parent=parent)
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
    position = Vec2(_UI_LEFT_OFFSET, -5)
    label = "Health"
    color = colex.PALE_VIOLET_RED


class OxygenBar(InfoBar):
    MAX_VALUE = 30
    position = Vec2(_UI_LEFT_OFFSET, -4)
    label = "O2"
    color = colex.AQUAMARINE


class HungerBar(InfoBar):
    MAX_VALUE = 120
    position = Vec2(_UI_LEFT_OFFSET, -3)
    label = "Food"
    color = colex.SANDY_BROWN


class ThirstBar(InfoBar):
    MAX_VALUE = 90
    position = Vec2(_UI_LEFT_OFFSET, -2)
    label = "Thirst"
    color = colex.AQUA
