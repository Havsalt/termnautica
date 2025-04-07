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
            products={ItemID.FABRIC: 1},
            idgredients={
                ItemID.KELP: 1,
            },
        ),
        Recipe(
            products={ItemID.STRING: 2},
            idgredients={
                ItemID.KELP: 1,
                ItemID.FABRIC: 1,
            },
        ),
        Recipe(
            products={ItemID.WATER_BOTTLE: 1},
            idgredients={
                ItemID.BLADDER_FISH: 1,
                ItemID.KELP: 2,
            },
        ),
        Recipe(
            products={ItemID.CHOCOLATE: 2},
            idgredients={
                ItemID.KELP: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
        Recipe(
            products={ItemID.MEDKIT: 1},
            idgredients={
                ItemID.KELP: 2,
                ItemID.STRING: 1,
                ItemID.FABRIC: 4,
                ItemID.GOLD_ORE: 1,
            },
        ),
        Recipe(
            products={ItemID.BANDAGE: 1},
            idgredients={
                ItemID.FABRIC: 2,
                ItemID.STRING: 1,
            },
        ),
        Recipe(
            products={ItemID.STEEL_KNIFE: 1},
            idgredients={
                ItemID.STEEL_BAR: 2,
                ItemID.STRING: 1,
            },
        ),
        Recipe(
            products={ItemID.BASIC_DIVING_MASK: 1},
            idgredients={
                ItemID.FABRIC: 2,
                ItemID.STRING: 1,
            },
        ),
    ]
    centered = True
    color = colex.MEDIUM_AQUAMARINE
    texture = [
        "__..__",
        ":    :",
        "\\.__./",
    ]
