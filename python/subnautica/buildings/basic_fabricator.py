import colex
from charz import Sprite

from ..item import ItemID, Recipe
from ..props import Interactable
from ..fabrication import Fabrication


class BasicFabricator(Fabrication, Interactable, Sprite):
    _REACH = 4
    _REACH_FRACTION = 1
    _RECIPES = [
        Recipe(
            products={ItemID.WATER_BOTTLE: 1},
            idgredients={
                ItemID.BLADDER_FISH: 1,
                ItemID.KELP: 2,
            },
        ),
        Recipe(
            products={
                ItemID.CHOCOLATE: 3,
                ItemID.TITANIUM_BAR: 1,
            },
            idgredients={
                ItemID.KELP: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
        Recipe(
            products={ItemID.MEDKIT: 1},
            idgredients={
                ItemID.KELP: 6,
                ItemID.GOLD_ORE: 1,
            },
        ),
        Recipe(
            products={ItemID.BANDAGE: 1},
            idgredients={ItemID.KELP: 4},
        ),
    ]
    centered = True
    color = colex.MEDIUM_AQUAMARINE
    transparency = " "
    texture = [
        "__..__",
        ":    :",
        "\\.__./",
    ]
