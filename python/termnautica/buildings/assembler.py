import colex
from charz import Sprite

from ..item import ItemID, Recipe
from ..props import Interactable
from ..fabrication import Fabrication


class Assembler(Fabrication, Interactable, Sprite):
    _RECIPES = [
        Recipe(
            products={ItemID.STEEL_KNIFE: 1},
            idgredients={
                ItemID.STEEL_BAR: 2,
                ItemID.STRING: 1,
            },
        ),
        Recipe(
            products={ItemID.IMPROVED_DIVING_MASK: 1},
            idgredients={
                ItemID.DIAMOND: 2,
                ItemID.STRING: 1,
                ItemID.FABRIC: 1,
            },
        ),
        Recipe(
            products={ItemID.ADVANCED_SUITE: 1},
            idgredients={
                ItemID.CRYSTAL: 3,
                ItemID.STEEL_THREAD: 1,
                ItemID.FABRIC: 2,
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
