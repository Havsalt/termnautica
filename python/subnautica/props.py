"""Properties that can be used as "tags" when defining a node class

Classes defined here will be used as `mixin components`
"""

import colex
from charz import Color

# NOTE: Add manually when a new tag is created
__all__ = [
    "Collectable",
    "Interactable",
    "Eatable",
]


class Collectable:
    name: str | None = None

    def get_tags(self) -> list[type]:
        tags = []
        for base in self.__class__.__mro__:
            if base.__name__ in __all__:
                tags.append(base)
        return tags


class Interactable:
    def grab_focus(self) -> None:
        assert isinstance(self, Color)
        self.color = colex.REVERSE + (self.__class__.color or colex.WHITE)

    def loose_focus(self) -> None:
        assert isinstance(self, Color)
        self.color = self.__class__.color


class Eatable: ...
