import colex
from charz import Sprite

from ..item import ItemID, Recipe
from ..props import Interactable
from ..fabrication import Fabrication


class Medbay(Fabrication, Interactable, Sprite):
    _RECIPES = [
        Recipe(
            products={ItemID.BANDAGE: 1},
            ingredients={
                ItemID.FABRIC: 2,
                ItemID.STRING: 1,
            },
        ),
        Recipe(
            products={ItemID.MEDKIT: 1},
            ingredients={
                ItemID.KELP: 2,
                ItemID.STRING: 1,
                ItemID.FABRIC: 4,
                ItemID.GOLD_ORE: 1,
            },
        ),
    ]
    centered = True
    color = colex.ANTIQUE_WHITE
    texture = [
        "|^+++^|",
        "'^___^'",
    ]
