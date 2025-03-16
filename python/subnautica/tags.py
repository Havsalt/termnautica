"""Tags that can be instantiated on their own

Similar to props, see `props.py`
"""

# NOTE: Add manually when a new tag/mixin is created
tag_members: dict[str, list[str]] = {
    "Eatable": ["hunger_value"],
    "Drinkable": ["thirst_value"],
    "Healing": ["heal_value"],
}


class Eatable:
    def __init__(self, hunger_value: int | None = None) -> None:
        if hunger_value is not None:
            self.hunger_value = hunger_value


class Drinkable:
    def __init__(self, thirst_value: int | None = None) -> None:
        if thirst_value is not None:
            self.thirst_value = thirst_value


class Healing:
    def __init__(self, heal_value: int | None = None) -> None:
        if heal_value is not None:
            self.heal_value = heal_value
