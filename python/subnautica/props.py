"""Properties that can be used as "tags" when defining a node class

Classes defined here will be used as `mixin components`
"""

import colex
from charz import Texture, Color, Sprite

# NOTE: Add manually when a new tag is created
__all__ = [
    "Collectable",
    "Interactable",
    "Eatable",
    "Building",
]


class Collectable:
    name: str | None = None

    def get_tags(self) -> list[type]:
        tags = []
        for base in self.__class__.__mro__:
            if base.__name__ in __all__:
                tags.append(base)
        return tags


# TODO: Add center of grab reach thingy
class Interactable:
    reach: float = 8  # Maximum length the interactor can be from the `Interactable`
    reach_fraction: float = 2 / 3  # Y-axis fraction, in linear transformation
    interactable: bool = True  # Turn off when in use
    highlight_z_index: int | None = None
    _last_z_index: int | None = None

    def grab_focus(self) -> None:
        assert isinstance(self, Texture) and isinstance(self, Color)
        self.color = colex.REVERSE + (self.__class__.color or colex.WHITE)
        if self.highlight_z_index is not None and self._last_z_index is None:
            self._last_z_index = self.z_index
            self.z_index = self.highlight_z_index

    def loose_focus(self) -> None:
        assert isinstance(self, Texture) and isinstance(self, Color)
        self.color = self.__class__.color
        if self.highlight_z_index is not None and self._last_z_index is not None:
            self.z_index = self._last_z_index
            self._last_z_index = None

    def on_interact(self, interactor: Sprite) -> None: ...


# TODO: Make it `Consumable` instead, and have hunger, thirst and such be stat vars
class Eatable: ...


# TODO: Define building room bounding hitbox, that can be checked from `Player`
# TODO: Move building gravity of `Lifepod` into `Player`
class Building:
    has_oxygen: bool = True

    def on_exit(self) -> None: ...  # Triggered when actor (`Player`) exits the building
