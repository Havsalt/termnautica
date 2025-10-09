"""Abstract classes defining properties for common functionality.

These classes are properties that can be used as "tags" when defining a node class.
Classes defined here will be used as `mixin components`.
They may also provide methods, either to be overwritten, or as base case.
"""

from typing import Self

import pygame
import colex
from charz import Sprite, Hitbox, Vec2, clamp

from . import settings
from .item import ItemID, Recipe


type Count = int


class Collectable:
    _ITEM: ItemID
    _SOUND_COLLECT: pygame.mixer.Sound | None = pygame.mixer.Sound(
        settings.SOUNDS_FOLDER / "collect" / "default.wav"
    )

    def collect_into(self, inventory: dict[ItemID, Count]) -> None:
        assert self._ITEM is not None, f"{self}.name is `None`"

        if self._ITEM in inventory:
            inventory[self._ITEM] += 1
        else:
            inventory[self._ITEM] = 1

        if self._SOUND_COLLECT is not None:
            self._SOUND_COLLECT.play()


class Interactable:
    _REACH: float = 8  # Maximum length the interactor can be from the `Interactable`
    _REACH_FRACTION: float = 2 / 3  # Y-axis fraction, in linear transformation
    _REACH_CENTER: Vec2 = Vec2.ZERO  # Offset
    _HIGHLIGHT_Z_INDEX: int | None = None
    interactable: bool = True  # Turn off when in use
    _last_z_index: int | None = None

    def with_interacting(self, state: bool, /) -> Self:
        self.interactable = state
        return self

    def grab_focus(self) -> None:
        assert isinstance(self, Sprite)
        self.color = colex.REVERSE + (self.__class__.color or colex.WHITE)
        if self._HIGHLIGHT_Z_INDEX is not None and self._last_z_index is None:
            self._last_z_index = self.z_index
            self.z_index = self._HIGHLIGHT_Z_INDEX

    def loose_focus(self) -> None:
        assert isinstance(self, Sprite)
        self.color = self.__class__.color
        if self._HIGHLIGHT_Z_INDEX is not None and self._last_z_index is not None:
            self.z_index = self._last_z_index
            self._last_z_index = None

    def is_in_range_of(self, global_point: Vec2) -> tuple[bool, float]:
        assert isinstance(self, Sprite)
        if not self.interactable:
            return (False, 0)
        reach_point = self.global_position + self._REACH_CENTER
        relative = global_point - reach_point
        relative.y /= self._REACH_FRACTION  # Apply linear transformation on Y-axis
        # NOTE: Using squared lengths for a bit more performance
        dist_squared = relative.length_squared()
        return (dist_squared <= self._REACH * self._REACH, dist_squared)

    def on_interact(self, actor: Sprite) -> None: ...

    # NOTE: May be triggered each frame if selected by `Player`
    def when_selected(self, actor: Sprite) -> None: ...

    # NOTE: Only triggered one time
    def on_deselect(self, actor: Sprite) -> None: ...


class Building:
    HAS_OXYGEN: bool = True
    _BOUNDARY: Hitbox | None = None
    _OPEN_CEILING: bool = False

    def on_exit(self) -> None: ...  # Triggered when actor (`Player`) exits the building

    def move_and_collide_inside(self, node: Sprite, velocity: Vec2) -> None:
        assert isinstance(self, Sprite)
        if self._BOUNDARY is None:
            return

        if self._BOUNDARY.centered:
            start = -self._BOUNDARY.size / 2
            end = self._BOUNDARY.size / 2
        else:
            start = Vec2.ZERO
            end = self._BOUNDARY.size.copy()
        start += node.texture_size / 2
        end -= node.texture_size / 2

        # Apply gravity
        velocity.y += 1
        # Translate with snap
        if self._OPEN_CEILING:
            node.position.y = min(node.position.y + velocity.y, end.y)
        else:
            node.position.y = clamp(node.position.y + velocity.y, start.y, end.y)
        node.position.x = clamp(node.position.x + velocity.x, start.x, end.x)


class Crafting:
    _RECIPES: list[Recipe] = []  # NOTE: Order matter

    def can_craft(self, recipe: Recipe, inventory: dict[ItemID, Count]) -> bool:
        return all(
            inventory.get(idgredient, 0) >= idgredient_cost
            for idgredient, idgredient_cost in recipe.idgredients.items()
        )

    def consume_idgredients(
        self,
        recipe: Recipe,
        inventory: dict[ItemID, Count],
    ) -> None:
        for idgredient, idgredient_cost in recipe.idgredients.items():
            if idgredient not in inventory:
                raise KeyError(
                    f"Attempted removing {idgredient_cost}x{idgredient},"
                    f" but {idgredient} is not found in {inventory}"
                )
            inventory[idgredient] -= idgredient_cost

    def add_products(
        self,
        recipe: Recipe,
        inventory: dict[ItemID, Count],
    ) -> None:
        for product, production_count in recipe.products.items():
            if product in inventory:
                inventory[product] += production_count
            else:
                inventory[product] = production_count

    def craft(
        self,
        recipe: Recipe,
        inventory: dict[ItemID, Count],
    ) -> None:
        self.consume_idgredients(recipe, inventory)
        self.add_products(recipe, inventory)

    # def craft_each_if_possible(
    #     self,
    #     inventory: dict[ItemID, Count],
    # ) -> None:
    #     for recipe in self._RECIPES:
    #         if self.can_craft(recipe, inventory):
    #             self.craft(recipe, inventory)


class _Marker(Sprite):
    transparency = " "
    color = colex.CRIMSON
    centered = True
    texture = [
        " + ",
        "-+-",
        " + ",
    ]


class Targetable:
    _marker: Sprite | None = None

    def gain_target(self) -> None:
        assert isinstance(self, Sprite), "Missing `Sprite` base"

        if self._marker is None:
            self._marker = _Marker(self)
        else:
            self._marker.show()

    def loose_target(self) -> None:
        if self._marker is not None:
            self._marker.hide()


class HasHealth:  # Health property might be overridden in subclass
    _health: float

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value: float) -> None:
        self._health = value
