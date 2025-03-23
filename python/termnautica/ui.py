from __future__ import annotations

from math import ceil
from typing import MutableMapping

import pygame
import colex
from colex import ColorValue
from charz import Node, Sprite, Label, Vec2, text, clamp

from .item import ItemID, Recipe


type Count = int
type Craftable = bool
type IdgredientCount = int


_UI_LEFT_OFFSET: int = -50
_UI_RIGHT_OFFSET: int = 40
_UI_CHANNEL = pygame.mixer.Channel(0)


# TODO: Render `UIElement` on top of screen buffer (Would be nice with `FrameTask`)
class UIElement:  # NOTE: Have this be the first mixin in mro
    z_index = 5  # Global UI z-index


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
    _LABEL: str = "<Unset>"
    _CELL_CHAR: str = "#"
    _CELL_FILL: str = " "
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
        last_value = self.value
        last_cell_count = self.cell_count

        self._value = clamp(value, 0, self.MAX_VALUE)
        percent = self._value / self.MAX_VALUE

        cell_count = ceil(self.MAX_CELL_COUNT * percent)
        cells = self._CELL_CHAR * cell_count
        progress = cells.ljust(self.MAX_CELL_COUNT, self._CELL_FILL)
        self.text = f"[{progress}]> {self._LABEL}"

        change = self.value - last_value
        cells_changed = cell_count - last_cell_count
        self.on_change(change, cells_changed)

    @property
    def cell_count(self) -> int:
        percent = self.value / self.MAX_VALUE
        return ceil(self.MAX_CELL_COUNT * percent)

    def fill(self) -> None:
        last_value = self.value
        last_cell_count = self.cell_count
        self.value = self.MAX_VALUE
        change = self.value - last_value
        cells_changed = self.cell_count - last_cell_count
        self.on_change(change, cells_changed)

    def on_change(self, change: float, cells_changed: int, /) -> None: ...


class HealthBar(InfoBar):
    MAX_VALUE = 100
    _SOUND_HEAL = pygame.mixer.Sound("assets/sounds/ui/health/heal.wav")
    _SOUND_HURT = pygame.mixer.Sound("assets/sounds/ui/health/hurt.wav")
    _CHANNEL_HURT = pygame.mixer.Channel(1)
    _LABEL = "Health"
    position = Vec2(_UI_LEFT_OFFSET, -5)
    color = colex.PALE_VIOLET_RED

    def on_change(self, change: float, _cells_changed: int) -> None:
        if change > 0:
            _UI_CHANNEL.play(self._SOUND_HEAL)
        elif change < 0 and not self._CHANNEL_HURT.get_busy():
            self._CHANNEL_HURT.play(self._SOUND_HURT)


class OxygenBar(InfoBar):
    MAX_VALUE = 30
    _SOUND_BREATHE = pygame.mixer.Sound("assets/sounds/ui/oxygen/breathe.wav")
    _SOUND_BUBBLE = pygame.mixer.Sound("assets/sounds/ui/oxygen/bubble.wav")
    _CHANNEL_BREATH = pygame.mixer.Channel(2)
    _CHANNEL_BUBBLE = pygame.mixer.Channel(3)
    _LABEL = "O2"
    position = Vec2(_UI_LEFT_OFFSET, -4)
    color = colex.AQUAMARINE

    def on_change(self, change: float, cells_changed: int) -> None:
        if change > 0 and not self._CHANNEL_BREATH.get_busy():
            self._CHANNEL_BREATH.play(self._SOUND_BREATHE)
        if cells_changed and not self._CHANNEL_BUBBLE.get_busy():
            self._CHANNEL_BUBBLE.play(self._SOUND_BUBBLE)


class HungerBar(InfoBar):
    MAX_VALUE = 120
    _LABEL = "Food"
    position = Vec2(_UI_LEFT_OFFSET, -3)
    color = colex.SANDY_BROWN


class ThirstBar(InfoBar):
    MAX_VALUE = 90
    _LABEL = "Thirst"
    position = Vec2(_UI_LEFT_OFFSET, -2)
    color = colex.AQUA


class Panel(Sprite):
    _width: int = 12
    _height: int = 6
    fill_char: str = " "

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        self._width = value
        self._resize()

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        self._height = value
        self._resize()

    def _resize(self) -> None:
        assert self._width >= 2, f"Minimum width of 2, got: {self._width}"
        assert self._height >= 2, f"Minimum height of 2, got: {self._height}"
        self.texture = [
            "┌" + "-" * (self._width - 2) + "┐",
            *[
                "┊" + self.fill_char * (self._width - 2) + "┊"
                for _ in range(self._height - 2)
            ],
            "└" + "-" * (self._width - 2) + "┘",
        ]


class Crafting(UIElement, Panel):  # GUI
    _DEFAULT_PRODUCT_COLOR: ColorValue = colex.GRAY
    _CRAFTABLE_PRODUCT_COLOR: ColorValue = colex.GOLDENROD
    _SELECTED_PRODUCT_COLOR: ColorValue = colex.BOLD + colex.REVERSE + colex.WHITE
    _SELECTED_CRAFTABLE_PRODUCT_COLOR: ColorValue = (
        colex.BOLD + colex.REVERSE + colex.AQUA
    )
    _MISSING_IDGREDIENT_COLOR: ColorValue = (
        colex.BOLD + colex.REVERSE + colex.LIGHT_GRAY
    )
    _CRAFTABLE_IDGREDIENT_COLOR: ColorValue = (
        colex.BOLD + colex.REVERSE + colex.PALE_GREEN
    )
    position = Vec2(2, -10)
    centered = True
    color = colex.BOLD + colex.WHITE
    visible = False

    def __init__(self, parent: Node) -> None:
        super().__init__(parent=parent)
        self.width = 50
        self.height = 8
        self._info_labels: list[Label] = []

    # I did not want to pass inventory of the one interacting with the `Fabrication`,
    # therefore, states regarding craftable and count of idgredients are passed
    # using a tuple of 3 elements
    def update_from_recipe(
        self,
        current_recipe: Recipe,
        selected_idgredient_counts: tuple[IdgredientCount, ...],
        all_recipe_states: list[tuple[Recipe, Craftable]],
    ) -> None:
        self.height = len(all_recipe_states) + len(current_recipe.idgredients) + 2

        for products_label in self._info_labels:
            products_label.queue_free()
        self._info_labels.clear()

        lino = 1  # Manual lino, because current recipe needs more place
        for recipe, craftable in all_recipe_states:
            products_text = " + ".join(
                f"{product_count}x{product.name.replace("_", " ").capitalize()}"
                for product, product_count in recipe.products.items()
            )
            products_color = (  # This might not be the prettiest, but should be ok
                (
                    self._SELECTED_CRAFTABLE_PRODUCT_COLOR
                    if recipe is current_recipe
                    else self._CRAFTABLE_PRODUCT_COLOR
                )
                if craftable
                else (
                    self._SELECTED_PRODUCT_COLOR
                    if recipe is current_recipe
                    else self._DEFAULT_PRODUCT_COLOR
                )
            )
            products_label = Label(
                self,
                text=products_text,
                z_index=self.z_index + 1,
                color=products_color,
                position=Vec2(
                    -self.texture_size.x // 2,
                    -self.texture_size.y // 2 + lino,
                ),
            )
            lino += 1
            self._info_labels.append(products_label)

            if recipe is current_recipe:
                for index, (idgredient, idgredient_cost) in enumerate(
                    recipe.idgredients.items()
                ):
                    idgredient_name = idgredient.name.replace("_", " ").capitalize()
                    idgredient_count = selected_idgredient_counts[index]
                    idgredient_text = (
                        f"{idgredient_cost}x{idgredient_name} ({idgredient_count})"
                    )
                    idgredient_color = (
                        self._CRAFTABLE_IDGREDIENT_COLOR
                        if idgredient_count >= idgredient_cost
                        else self._MISSING_IDGREDIENT_COLOR
                    )
                    idgredient_label = Label(
                        self,
                        text="- " + idgredient_text,
                        z_index=self.z_index + 1,
                        color=idgredient_color,
                        position=Vec2(
                            -self.texture_size.x // 2,
                            -self.texture_size.y // 2 + lino,
                        ),
                    )
                    self._info_labels.append(idgredient_label)
                    lino += 1
