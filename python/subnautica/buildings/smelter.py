import colex
from charz import Sprite, Vec2

from ..player import Player
from ..item import Item, ItemID
from ..recipe import Recipe
from ..props import Interactable, Crafter


class Smelter(Interactable, Crafter, Sprite):
    _REACH = 3
    _REACH_CENTER = Vec2(3, 0.5)
    _RECIPES = [
        Recipe(
            product=Item(ItemID.COPPER_BAR, 2),
            idgredients={
                ItemID.COPPER_ORE: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
        Recipe(
            product=Item(ItemID.TITANIUM_BAR, 2),
            idgredients={
                ItemID.TITANIUM_ORE: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
        Recipe(
            product=Item(ItemID.GOLD_BAR, 2),
            idgredients={
                ItemID.GOLD_ORE: 2,
                ItemID.COAL_ORE: 1,
            },
        ),
    ]
    color = colex.ORANGE_RED
    texture = [
        "/^\\¨¨¨\\",
        "\\_/___/",
    ]

    def on_interact(self, interactor: Sprite) -> None:
        assert isinstance(
            interactor,
            Player,
        ), "Only `Player` can interact with `Smelter`"
        self.craft_each_if_possible(interactor.inventory)
