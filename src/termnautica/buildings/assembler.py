import colex
from charz import Sprite

from ..item import ItemID, Recipe
from ..props import Interactable
from ..fabrication import Fabrication


class Assembler(Fabrication, Interactable, Sprite):
    _RECIPES = [
        Recipe(
            products={ItemID.STEEL_KNIFE: 1},
            ingredients={
                ItemID.STEEL_BAR: 2,
                ItemID.STRING: 1,
            },
        ),
        Recipe(
            products={ItemID.IMPROVED_DIVING_MASK: 1},
            ingredients={
                ItemID.DIAMOND: 2,
                ItemID.STRING: 1,
                ItemID.FABRIC: 1,
            },
        ),
        Recipe(
            products={ItemID.ADVANCED_SUITE: 1},
            ingredients={
                ItemID.CRYSTAL: 3,
                ItemID.STEEL_THREAD: 1,
                ItemID.FABRIC: 2,
            },
        ),
        Recipe(
            products={ItemID.STEEL_HARPOON: 1},
            ingredients={
                ItemID.STEEL_THREAD: 2,
                ItemID.CRYSTAL: 1,
                ItemID.FABRIC: 3,
            },
        ),
    ]
    centered = True
    color = colex.BROWN
    texture = [
        "/¨¨¨\\",
        "|   v",
        "|",
    ]
