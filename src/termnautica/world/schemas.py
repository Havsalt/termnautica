from typing import TypedDict, NotRequired

from colex import ColorValue

from ..item import ItemCount


type Seed = int
type ItemName = str
type Vec2[T] = tuple[T, T]


class PlayerData(TypedDict):
    health: float
    oxygen: float
    hunger: float
    thirst: float
    position: tuple[float, float]
    inventory: dict[ItemName, ItemCount]


# class TileData(TypedDict):
#     name: str
#     position: Vec2[float]
#     color: NotRequired[ColorValue]
#     texture: list[str]


class EntetyData(TypedDict):
    type_index: int
    position: Vec2[float]


# class SpawnerData(TypedDict):
#     qualname: str
#     time_until_spawn: float
#     enteties: list[EntetyData]


class SaveData(TypedDict):
    seed: Seed
    wave_time: float
    players: list[PlayerData]
    # spawners: list[SpawnerData]
    # tiles: list[TileData]
