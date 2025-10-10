import colex
from charz import Sprite

from ..item import ItemID, Recipe
from ..props import Interactable
from ..fabrication import Fabrication


class NutrientSynthesizer(Fabrication, Interactable, Sprite):
    _RECIPES = [
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
    ]
    centered = True
    color = colex.SKY_BLUE
    texture = [
        ".--<",
        "====",
    ]
