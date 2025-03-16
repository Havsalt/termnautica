from __future__ import annotations

from typing import TYPE_CHECKING

import colex
from charz import Sprite, Label, Hitbox, Vec2, load_texture

from .item import Item, ItemID
from .recipe import Recipe
from .props import Interactable, Building, Crafter

from .player import Player


class Smelter(Interactable, Crafter, Sprite):
    color = colex.ORANGE_RED
    texture = [
        "/^\\¨¨¨\\",
        "\\_/___/",
    ]
    _RECIPES = [
        Recipe(
            product=Item(ItemID.COPPER_BAR, 2),
            idgredients={
                ItemID.COPPER_ORE: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
        Recipe(
            product=Item(ItemID.TITANIUM_BAR, 2),
            idgredients={
                ItemID.TITANIUM_ORE: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
        Recipe(
            product=Item(ItemID.GOLD_BAR, 2),
            idgredients={
                ItemID.GOLD_ORE: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
    ]

    def on_interact(self, interactor: Sprite) -> None:
        assert isinstance(
            interactor, Player
        ), "Only `Player` can interact with `Smelter`"

        inventory = interactor.inventory  # Ref

        for recipe in self._RECIPES:
            if all(
                inventory.get(idgredient, default=Item(ItemID.NONE, 0)).count >= count
                for idgredient, count in recipe.idgredients.items()
            ):
                # Consume idgredients
                for idgredient, count in recipe.idgredients.items():
                    inventory[idgredient].count -= count
                # Add product
                if not recipe.product.id in inventory:
                    inventory[recipe.product.id] = Item(recipe.product.id, 0)
                inventory[recipe.product.id].count += recipe.product.count


class Ladder(Interactable, Sprite):
    _REACH = 2
    _REACH_FRACTION = 2 / 1
    interactable = False
    z_index = 1
    color = colex.from_hex("#aaa9ad")
    transparency = " "
    centered = True
    texture = load_texture("lifepod/ladder.txt")

    def on_interact(self, interactor: Player) -> None:
        assert isinstance(self.parent, Lifepod)
        self.parent.on_exit()


# TODO: Crafting | Fabricatror (Medkit), Radio, O2, Power (Solar), Storage
class Lifepod(Interactable, Building, Sprite):
    _BOUNDARY = Hitbox(size=Vec2(19, 9), centered=True)
    _OPEN_CEILING = True
    _REACH = 15
    _REACH_FRACTION = 3 / 7
    _HIGHLIGHT_Z_INDEX = 0
    z_index = -2  # Increase when stepping into
    color = colex.BOLD + colex.WHITE
    centered = True
    texture = load_texture("lifepod/front.txt")
    entry_location = Vec2(0, -8)
    exit_location = Vec2(0, -7)
    # Used to track `Player`, for teleporting to exit location
    _curr_interactor: Player | None = None

    def __init__(self) -> None:
        self._name = Label(
            self,
            text="Lifepod",
            color=colex.ITALIC + colex.SLATE_GRAY,
            position=self.texture_size / -2,
        )
        self._name.position.y -= 3
        self._ladder = Ladder(self, visible=False)
        self._ladder.interactable = False
        self._smelter = Smelter(self, position=Vec2(2, 2), visible=False)
        self._smelter.interactable = False
        self._smelter_overlay = Sprite(
            self._smelter,
            texture=["", Smelter.texture[1]],
        )

    def on_interact(self, interactor: Player) -> None:
        # Reparent without moving
        location = interactor.global_position
        interactor.parent = self
        interactor.global_position = location
        # DEV
        interactor.global_position = self.global_position + self.entry_location
        # Change state and texture
        self.interactable = False
        # self.z_index = 2
        self.texture = load_texture("lifepod/inside.txt")
        self._curr_interactor = interactor
        self._ladder.show()
        self._ladder.interactable = True
        self._smelter.show()
        self._smelter.interactable = True

    # TODO: Improve
    def update(self, _delta: float) -> None:
        if not self.interactable:
            self.z_index = 0

    def on_exit(self) -> None:
        assert (
            self._curr_interactor is not None
        ), "current interactor is `None` when exited building"
        assert isinstance(self._curr_interactor.parent, Sprite), (
            f"{self._curr_interactor}.parent "
            f"({self._curr_interactor.parent}) is missing `Sprite` base"
        )
        # Unset parent of player
        self._curr_interactor.parent = None
        self._curr_interactor.global_position = (
            self.global_position + self.exit_location
        )
        # Unset player
        self._curr_interactor = None
        self.interactable = True
        # Transition to outside perspective
        self.z_index = self.__class__.z_index
        self.texture = load_texture("lifepod/front.txt")
        # Disable inside interactables
        self._ladder.hide()
        self._ladder.interactable = False
        self._smelter.hide()
        self._smelter.interactable = False
