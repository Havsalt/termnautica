import colex
from charz import Sprite

from ..item import ItemID, Recipe
from ..props import Interactable
from ..fabrication import Fabrication


class Fabricator(Fabrication, Interactable, Sprite):
    _REACH = 4
    _REACH_FRACTION = 1
    _RECIPES = [
        Recipe(
            products={ItemID.FABRIC: 1},
            idgredients={ItemID.KELP: 1},
        ),
        Recipe(
            products={ItemID.STRING: 2},
            idgredients={
                ItemID.KELP: 1,
                ItemID.FABRIC: 1,
            },
        ),
        Recipe(
            products={ItemID.SHARP_ROCK: 1},
            idgredients={
                ItemID.IRON_ORE: 2,
            },
        ),
        Recipe(
            products={ItemID.BASIC_DIVING_MASK: 1},
            idgredients={
                ItemID.FABRIC: 2,
                ItemID.STRING: 1,
            },
        ),
        Recipe(
            products={ItemID.BASIC_SUITE: 1},
            idgredients={
                ItemID.FABRIC: 2,
                ItemID.TITANIUM_BAR: 2,
            },
        ),
        Recipe(
            products={ItemID.O2_TANK: 1},
            idgredients={
                ItemID.STRING: 1,
                ItemID.COPPER_BAR: 2,
                ItemID.GOLD_BAR: 1,
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
