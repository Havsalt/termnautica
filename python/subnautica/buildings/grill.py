import colex
from charz import Sprite, Vec2

from ..particles import Fire
from ..props import Interactable
from ..fabrication import Fabrication
from ..item import ItemID, Recipe


class Grill(Fabrication, Interactable, Sprite):
    _FIRE_OFFSET: Vec2 = Vec2(1, 0)
    _FIRE_EMMIT_INTERVAL: int = 8
    _RECIPES = [
        Recipe(
            products={ItemID.FRIED_FISH_NUGGET: 2},
            idgredients={
                ItemID.GOLD_FISH: 1,
                ItemID.KELP: 1,
            },
        ),
        Recipe(
            products={ItemID.COD_SOUP: 2},
            idgredients={
                ItemID.COD: 1,
                ItemID.WATER_BOTTLE: 1,
            },
        ),
        Recipe(
            products={ItemID.GRILLED_SALMON: 2},
            idgredients={
                ItemID.SALMON: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
    ]
    color = colex.DARK_ORANGE
    texture = [
        "~~~",
        "\\ /",
    ]
    _time_since_emmit: int = 0

    def update(self, _delta: float) -> None:
        self._time_since_emmit -= 1
        if self._time_since_emmit <= 0:
            self._time_since_emmit = self._FIRE_EMMIT_INTERVAL
            Fire().with_global_position(self.global_position + self._FIRE_OFFSET)
