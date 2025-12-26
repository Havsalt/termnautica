from __future__ import annotations

from typing import Protocol

from charz import Scene, Vec2
from charz_core.typing import NodeID

from .. import ocean
from ..item import ItemID
from .schemas import SaveData


class SpawnerProtocol(Protocol):
    uid: NodeID


def apply_save_data(data: SaveData) -> None:
    # Lazy loading - A quick workaround
    from ..player import Player

    players = Scene.current.get_group_members("player", type_hint=Player)
    for player, player_data in zip(players, data["players"]):
        player.global_position = Vec2(*player_data["position"])

        player.health = player_data["health"]
        player.hud.oxygen_bar.value = player_data["oxygen"]
        player.hud.hunger_bar.value = player_data["hunger"]
        player.hud.thirst_bar.value = player_data["thirst"]

        player.inventory.clear()  # Does nothing, really...
        for item_name, item_count in player_data["inventory"].items():
            try:
                item_id = ItemID(item_name)
            except ValueError as err:
                exit(f"Could not load item with name {item_name}: {err}")
            player.inventory.give(item_id, item_count)

    # spawners = Scene.current.get_group_members("spawners", type_hint=SpawnerProtocol)
    # spawners = Scene.current.groups["spawners"]
    # for spawner_data in data["spawners"]:
    #     if spawner_data["uid"] in spawners:
    # in Scene.current.get_group_members(
    #     "spawners", type_hint=SpawnerProtocol
    # ):

    ocean.Water.wave_time_remaining = data["wave_time"]
