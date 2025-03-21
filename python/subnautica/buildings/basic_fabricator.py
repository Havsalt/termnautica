import colex
from charz import Sprite

from ..player import Player
from ..item import ItemID, Recipe
from ..props import Interactable, Crafter


class BasicFabricator(Interactable, Crafter, Sprite):
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
            products={ItemID.CHOCOLATE: 3},
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

    def on_interact(self, interactor: Sprite) -> None:
        assert isinstance(
            interactor,
            Player,
        ), "Only `Player` can interact with `Smelter`"
        self.craft_each_if_possible(interactor._inventory)
