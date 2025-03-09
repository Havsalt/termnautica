from __future__ import annotations

from typing import TYPE_CHECKING

import colex
from charz import Sprite, Label, Vec2, load_texture, clamp

from .props import Interactable, Building

if TYPE_CHECKING:
    from .player import Player


class Ladder(Interactable, Sprite):
    reach = 2
    reach_fraction = 2 / 1
    z_index = 1
    color = colex.from_hex("#aaa9ad")
    transparency = " "
    centered = True
    texture = load_texture("python/sprites/lifepod/ladder.txt")
    parent: Lifepod

    def on_interact(self, interactor: Player) -> None:
        self.parent.on_exit()


# TODO: Crafting | Fabricatror (Medkit), Radio, O2, Power (Solar), Storage
class Lifepod(Interactable, Building, Sprite):
    _FLOOR_LEVEL: int = 3
    name = "lifepod mk8"
    reach = 15
    reach_fraction = 3 / 7
    z_index = -2  # Increase when stepping into
    highlight_z_index = 0
    color = colex.BOLD + colex.WHITE
    centered = True
    texture = load_texture("python/sprites/lifepod/front.txt")
    entry_location = Vec2(0, -8)
    exit_location = Vec2(0, -7)
    _curr_interactor: Player | None = None

    def __init__(self) -> None:
        self._name = Label(
            self,
            text="Lifepod",
            color=colex.ITALIC + colex.SLATE_GRAY,
            position=self.texture_size / -2,
        )
        self._name.position.y -= 3
        self._ladder = Ladder(self).as_visible(False)

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
        self.texture = load_texture("python/sprites/lifepod/inside.txt")
        self._curr_interactor = interactor
        self._ladder.show()

    # TODO: Improve
    def update(self, _delta: float) -> None:
        if not self.interactable:
            self.z_index = 0
        # Collision inside
        if self._curr_interactor is not None:
            # Gravity inside
            self._curr_interactor.position.y = min(
                self._FLOOR_LEVEL,
                self._curr_interactor.position.y + 1,
            )
            # Wall collision
            self._curr_interactor.position.x = clamp(
                self._curr_interactor.position.x,
                self.texture_size.x // -2 + 4,
                self.texture_size.x // 2 - 3,
            )

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
        self.texture = load_texture("python/sprites/lifepod/front.txt")
        self._ladder.hide()
