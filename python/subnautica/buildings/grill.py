import colex
from charz import Sprite

from ..player import Player
from ..item import Item, ItemID
from ..recipe import Recipe
from ..props import Crafter, Interactable
from ..tags import Eatable, Drinkable


class Grill(Interactable, Crafter, Sprite):
    _RECIPES = [
        Recipe(
            product=Item(ItemID.FRIED_FISH_NUGGET, 2, [Eatable(15)]),
            idgredients={
                ItemID.GOLD_FISH: 1,
                ItemID.KELP: 1,
            },
        ),
        Recipe(
            product=Item(ItemID.COD_SOUP, 2, [Eatable(10), Drinkable(30)]),
            idgredients={
                ItemID.COD: 1,
                ItemID.WATER_BOTTLE: 1,
            },
        ),
        Recipe(
            product=Item(ItemID.GRILLED_SALMON, 2, [Eatable(20)]),
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

    def on_interact(self, interactor: Sprite) -> None:
        assert isinstance(
            interactor,
            Player,
        ), "Only `Player` can interact with `Smelter`"
        self.craft_each_if_possible(interactor.inventory)
