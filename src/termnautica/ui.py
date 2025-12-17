from __future__ import annotations

import itertools
from enum import Enum, auto, unique
from math import ceil

import pygame
import keyboard
import colex
from colex import ColorValue
from charz import Node, Sprite, Label, Vec2, clamp, group

from . import settings
from .item import ItemID, Recipe, Container


pygame.mixer.init()


type Count = int
type Craftable = bool
type IdgredientCount = int
type Char = str
"""`String` of length `1`."""


_UI_MIXER_CHANNEL = pygame.mixer.Channel(0)


# TODO: Render `UIElement` on top of screen buffer (Would be nice with `FrameTask`)
class UIElement:  # NOTE: Have this be the first mixin in mro
    z_index = 5  # Global UI z-index


class InventorySlot(UIElement, Label):
    _PREFIX: str = "{}. "
    _EMPTY_PREFIX: str = "   "
    _EMPTY_FILLER: Char = "="
    _CUTOFF_INDICATOR: str = ".."
    _SUFFIX_LENGTH: int = len(":99")
    # FPS * Seconds = Frames
    _TIME_WARMING: float = settings.FPS * 3
    _TIME_BETWEEN_STEP: float = settings.FPS * 0.2
    _TIME_BETWEEN_STEP_BACK: float = settings.FPS * 0.15
    _TIME_COOLING: float = settings.FPS * 2

    @unique
    class DisplayState(float, Enum):
        WARMING = auto()
        SLIDING = auto()
        COOLING = auto()
        BACKTRACKING = auto()

    def __init__(self, id: int, max_length: int) -> None:
        self._max_item_info_length = max_length
        self._id = id
        self._state = InventorySlot.DisplayState.WARMING
        self._frames_waited: int = 0
        self._scroll_frame: int = 0
        self._cutoff_amount: int | None = None

    def set_item(self, item: ItemID, count: Count) -> None:
        self.text = self._PREFIX.format(self._id) + self._fit_item_info(
            item, count, self._max_item_info_length
        )

    def clear_item(self) -> None:
        self.text = (
            self._EMPTY_PREFIX
            + self._EMPTY_FILLER * self._max_item_info_length
            + " " * self._SUFFIX_LENGTH
        )
        self._cutoff_amount = None

    def reset_states(self) -> None:
        self._state = InventorySlot.DisplayState.WARMING
        self._frames_waited = 0
        self._scroll_frame = 0

    def update(self) -> None:
        if self._cutoff_amount is None:
            return  # Return if no need for scroll animation
        self._frames_waited += 1
        match self._state:
            case InventorySlot.DisplayState.WARMING:
                if self._frames_waited >= self._TIME_WARMING:
                    self._state = InventorySlot.DisplayState.SLIDING
                    self._frames_waited = 0
            case InventorySlot.DisplayState.SLIDING:
                if self._scroll_frame >= self._cutoff_amount + len(
                    self._CUTOFF_INDICATOR
                ):
                    self._state = InventorySlot.DisplayState.COOLING
                if self._frames_waited >= self._TIME_BETWEEN_STEP:
                    self._frames_waited = 0
                    self._scroll_frame += 1
            case InventorySlot.DisplayState.COOLING:
                if self._frames_waited >= self._TIME_COOLING:
                    self._state = InventorySlot.DisplayState.BACKTRACKING
                    self._frames_waited = 0
            case InventorySlot.DisplayState.BACKTRACKING:
                if self._scroll_frame <= 0:
                    self._state = InventorySlot.DisplayState.WARMING
                if self._frames_waited >= self._TIME_BETWEEN_STEP_BACK:
                    self._frames_waited = 0
                    self._scroll_frame -= 1

    def _fit_item_info(
        self,
        item: ItemID,
        count: Count,
        width: int,
    ) -> str:
        """Fit item name for custom inventory wheel sprite.

        Uses local scroll info.
        Mutates local `._cutoff_amount`.

        Args:
            item (ItemID): Enum variant.
            count (Count): Item count.
            width (int): Max spaces to shorten, and min spaces to fill spaces.

        Returns:
            str: Item name fitting into `width`.
        """
        # Remove underscore, and capitalize each first letter in words
        pretty_name = " ".join(map(str.capitalize, item.value.split("_")))
        over_reach = len(pretty_name) - width
        if over_reach > 0:
            stop = self._scroll_frame + width - len(self._CUTOFF_INDICATOR)
            name_segment = pretty_name[self._scroll_frame : stop]
            missing_letter_count = width - len(name_segment)
            item_name = name_segment + self._CUTOFF_INDICATOR
            if missing_letter_count > 0:
                self._cutoff_amount = over_reach
        else:
            item_name = pretty_name
        # Ljust with `2`, expecting no stack greater than `99`  NOTE: Not enforced
        return (item_name + ":" + str(count).ljust(2)).ljust(
            width + self._SUFFIX_LENGTH
        )


class InventoryCenterMarker(UIElement, Sprite):
    color = colex.DARK_SALMON
    texture = ["X"]


# This is *not* a `Node2D`, because `Node2D` does not handle `.visible` in a tree
class InventoryWheel(UIElement, Sprite):
    _NAME_LENGTH: int = 6
    _SHOW_SPEED_PERCENT_PER_FRAME: float = 0.23
    _HIDE_SPEED_PERCENT_PER_FRAME: float = 0.27

    @unique
    class DisplayState(Enum):
        IDLE = auto()
        SHOWING = auto()
        HIDING = auto()

    def __init__(
        self, parent: Node, ref: Container, hide_anchor: Vec2 = Vec2.ZERO
    ) -> None:
        super().__init__(parent=parent)
        self.ref = ref
        self.hide_anchor = hide_anchor
        self._state = InventoryWheel.DisplayState.IDLE
        self._elements: list[Sprite] = [
            # Center Piviot
            InventoryCenterMarker().with_parent(self),
            # 1
            InventorySlot(id=1, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=4)
            .with_color(colex.REVERSE + colex.from_hex("#bbe4e9")),
            # 2
            InventorySlot(id=2, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=2, y=2)
            .with_color(colex.REVERSE + colex.from_hex("#79c2d0")),
            # 3
            InventorySlot(id=3, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=-5, y=4)
            .with_color(colex.REVERSE + colex.from_hex("#53a8b6")),
            # 4
            InventorySlot(id=4, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=-13, y=2)
            .with_color(colex.REVERSE + colex.from_hex("#5585b5")),
            # 5
            InventorySlot(id=5, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=-15)
            .with_color(colex.REVERSE + colex.from_hex("#37618b")),
            # 6
            InventorySlot(id=6, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=-13, y=-2)
            .with_color(colex.REVERSE + colex.from_hex("#37618b")),
            # 7
            InventorySlot(id=7, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=-6, y=-4)
            .with_color(colex.REVERSE + colex.from_hex("#5585b5")),
            # 8
            InventorySlot(id=8, max_length=self._NAME_LENGTH)
            .with_parent(self)
            .with_position(x=2, y=-2)
            .with_color(colex.REVERSE + colex.from_hex("#79c2d0")),
        ]
        self._slots: list[InventorySlot] = [
            element for element in self._elements if isinstance(element, InventorySlot)
        ]
        self._slots_resting_positions = [slot.position.copy() for slot in self._slots]
        self._waited_1_frame = False
        self._showing_percent = 0.00
        self.animate_hide()  # NOTE: Will be instant on start, since `self._showing_percent == 0.00`
        self.update()

    def animate_show(self) -> None:
        self._state = InventoryWheel.DisplayState.SHOWING
        self.show()
        for slot in self._slots:
            slot.show()
            slot.reset_states()

    def animate_hide(self) -> None:
        self._waited_1_frame = False
        self._state = InventoryWheel.DisplayState.HIDING

    def is_open(self) -> bool:
        return (
            self.is_globally_visible()
            and self._state is not InventoryWheel.DisplayState.HIDING
        )

    def update(self) -> None:
        if keyboard.is_pressed("6"):
            self.animate_hide()
        elif keyboard.is_pressed("5"):
            self.animate_show()
        match self._state:
            case InventoryWheel.DisplayState.IDLE:
                pass
            case InventoryWheel.DisplayState.SHOWING:
                for slot, rest_position in zip(
                    self._slots, self._slots_resting_positions
                ):
                    slot.position = self.hide_anchor.lerp(
                        rest_position, self._showing_percent
                    )
                if self._showing_percent == 1.00:
                    self._state = InventoryWheel.DisplayState.IDLE
                self._showing_percent = min(
                    self._showing_percent + self._SHOW_SPEED_PERCENT_PER_FRAME, 1.00
                )
            case InventoryWheel.DisplayState.HIDING:
                for slot, rest_position in zip(
                    self._slots, self._slots_resting_positions
                ):
                    slot.position = self.hide_anchor.lerp(
                        rest_position, self._showing_percent
                    )
                if self._showing_percent == 0.00:
                    if not self._waited_1_frame:
                        self._waited_1_frame = True
                        return
                    self._state = InventoryWheel.DisplayState.IDLE
                    for slot in self._slots:
                        slot.hide()
                    self.hide()
                self._showing_percent = max(
                    self._showing_percent - self._HIDE_SPEED_PERCENT_PER_FRAME, 0.00
                )

        for slot, item in itertools.zip_longest(
            self._slots, self.ref.ids(), fillvalue=None
        ):
            # Due to the nature of `itertools.zip_longest`,
            # stop when no more slots are available
            if slot is None:
                break
            if item is None:
                slot.clear_item()
            else:
                slot.set_item(item, self.ref.count(item))


class HotbarE(UIElement, Label):
    position = Vec2(settings.UI_RIGHT_OFFSET, -5)
    texture = ["Interact [E".rjust(11)]
    transparency = " "
    color = colex.SALMON


class Hotbar1(UIElement, Label):
    position = Vec2(settings.UI_RIGHT_OFFSET, -3)
    texture = ["Eat [1".rjust(11)]
    transparency = " "
    color = colex.SANDY_BROWN


class Hotbar2(UIElement, Label):
    position = Vec2(settings.UI_RIGHT_OFFSET, -2)
    texture = ["Drink [2".rjust(11)]
    transparency = " "
    color = colex.AQUA


class Hotbar3(UIElement, Label):
    position = Vec2(settings.UI_RIGHT_OFFSET, -1)
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
    _SOUND_HEAL = pygame.mixer.Sound(
        settings.SOUNDS_FOLDER / "ui" / "health" / "heal.wav"
    )
    _SOUND_HURT = pygame.mixer.Sound(
        settings.SOUNDS_FOLDER / "ui" / "health" / "hurt.wav"
    )
    _CHANNEL_HURT = pygame.mixer.Channel(1)
    _LABEL = "Health"
    position = Vec2(settings.UI_LEFT_OFFSET, -5)
    color = colex.PALE_VIOLET_RED

    def on_change(self, change: float, _cells_changed: int) -> None:
        if change > 0:
            _UI_MIXER_CHANNEL.play(self._SOUND_HEAL)
        elif change < 0 and not self._CHANNEL_HURT.get_busy():
            self._CHANNEL_HURT.play(self._SOUND_HURT)


class OxygenBar(InfoBar):
    MAX_VALUE = 100
    _SOUND_BREATHE = pygame.mixer.Sound(
        settings.SOUNDS_FOLDER / "ui" / "oxygen" / "breathe.wav"
    )
    _SOUND_BREATHE.set_volume(0.08)
    _SOUND_BUBBLE = pygame.mixer.Sound(
        settings.SOUNDS_FOLDER / "ui" / "oxygen" / "bubble.wav"
    )
    _SOUND_BUBBLE.set_volume(0.03)
    _CHANNEL_BREATH = pygame.mixer.Channel(2)
    _CHANNEL_BUBBLE = pygame.mixer.Channel(3)
    _LABEL = "O2"
    position = Vec2(settings.UI_LEFT_OFFSET, -4)
    color = colex.AQUAMARINE

    def on_change(self, change: float, cells_changed: int) -> None:
        if change > 0 and not self._CHANNEL_BREATH.get_busy():
            self._CHANNEL_BREATH.play(self._SOUND_BREATHE)
        if cells_changed and not self._CHANNEL_BUBBLE.get_busy():
            self._CHANNEL_BUBBLE.play(self._SOUND_BUBBLE)


class HungerBar(InfoBar):
    MAX_VALUE = 120
    _LABEL = "Food"
    position = Vec2(settings.UI_LEFT_OFFSET, -3)
    color = colex.SANDY_BROWN


class ThirstBar(InfoBar):
    MAX_VALUE = 90
    _LABEL = "Thirst"
    position = Vec2(settings.UI_LEFT_OFFSET, -2)
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
    # using a tuple of 2 elements
    def update_from_recipe(
        self,
        current_recipe: Recipe,
        selected_idgredient_counts: tuple[IdgredientCount, ...],
        all_recipe_states: list[tuple[Recipe, Craftable]],
    ) -> None:
        self.height = len(all_recipe_states) + len(current_recipe.ingredients) + 2

        for products_label in self._info_labels:
            products_label.queue_free()
        self._info_labels.clear()

        lino = 1  # Manual lino, because current recipe needs more place
        for recipe, craftable in all_recipe_states:
            products_text = " + ".join(
                f" {product_count}x{product.name.replace('_', ' ').capitalize()} "
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
                    -self.get_texture_size().x // 2 - 1,
                    -self.get_texture_size().y // 2 + lino,
                ),
            )
            lino += 1
            self._info_labels.append(products_label)

            if recipe is current_recipe:
                for index, (idgredient, idgredient_cost) in enumerate(
                    recipe.ingredients.items()
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
                        text=f" - {idgredient_text} ",
                        z_index=self.z_index + 1,
                        color=idgredient_color,
                        position=Vec2(
                            -self.get_texture_size().x // 2 - 1,
                            -self.get_texture_size().y // 2 + lino,
                        ),
                    )
                    self._info_labels.append(idgredient_label)
                    lino += 1


class HUDElement(UIElement, Sprite): ...


class ComposedHUD(HUDElement):
    def __init__(self, parent: Node | None = None, *, inventory_ref: Container) -> None:
        super().__init__(parent=parent)
        self.health_bar = HealthBar(self)
        self.oxygen_bar = OxygenBar(self)
        self.hunger_bar = HungerBar(self)
        self.thirst_bar = ThirstBar(self)
        self.inventory = InventoryWheel(
            self,
            ref=inventory_ref,
            hide_anchor=Vec2(18.5, -4),
        ).with_position(x=settings.UI_LEFT_OFFSET + 10, y=4)
        self.hotbar_e = HotbarE(self).with_visibility(False)
        self.hotbar_1 = Hotbar1(self).with_visibility(False)
        self.hotbar_2 = Hotbar2(self).with_visibility(False)
        self.hotbar_3 = Hotbar3(self).with_visibility(False)
        self.crafting_gui = Crafting(self)


@group("hud-1")
class ComposedHUD1(ComposedHUD): ...


@group("hud-2")
class ComposedHUD2(ComposedHUD): ...
