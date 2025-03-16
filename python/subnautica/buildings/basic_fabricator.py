import colex
from charz import Sprite

from ..player import Player
from ..item import Item, ItemID
from ..recipe import Recipe
from ..props import Interactable, Crafter
from ..tags import Drinkable, Healing


class BasicFabricator(Interactable, Crafter, Sprite):
    _REACH = 4
    _REACH_FRACTION = 1
    _RECIPES = [
        Recipe(
            product=Item(ItemID.WATER_BOTTLE, 1, [Drinkable(15)]),
            idgredients={
                ItemID.BLADDER_FISH: 1,
                ItemID.KELP: 2,
            },
        ),
        Recipe(
            product=Item(ItemID.MEDKIT, 1, [Healing(70)]),
            idgredients={
                ItemID.KELP: 6,
                ItemID.GOLD_ORE: 1,
            },
        ),
        Recipe(
            product=Item(ItemID.BANDAGE, 1, [Healing(30)]),
            idgredients={
                ItemID.KELP: 4,
            },
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
        self.craft_each_if_possible(interactor.inventory)
