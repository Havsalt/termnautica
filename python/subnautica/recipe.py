from dataclasses import dataclass

from .item import Item, ItemID


type Count = int


@dataclass
class Recipe:
    product: Item
    idgredients: dict[ItemID, Count]
