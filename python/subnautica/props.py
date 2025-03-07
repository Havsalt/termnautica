"""Properties that can be used as "tags" when defining a node class

Classes defined here will be used as `mixin components`
"""

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


class Interactable: ...


class Eatable: ...
