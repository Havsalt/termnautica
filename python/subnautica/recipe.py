from dataclasses import dataclass

from .item import ItemID


type Count = int


@dataclass
class Recipe:
    products: dict[ItemID, Count]
    idgredients: dict[ItemID, Count]
