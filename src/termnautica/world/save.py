import tomli_w
from charz import Scene

from .. import settings, ocean
from .schemas import SaveData, PlayerData  # , SpawnerData, EntetyData


def save_world(scene: Scene, *, seed: int) -> None:
    # Lazy loading - A quick workaround
    from ..player import Player
    from ..spawners import Spawner

    save_data = SaveData(
        seed=seed,
        wave_time=ocean.Water.wave_time_remaining,
        players=[
            PlayerData(
                health=player.hud.health_bar.value,
                oxygen=player.hud.oxygen_bar.value,
                hunger=player.hud.hunger_bar.value,
                thirst=player.hud.thirst_bar.value,
                position=((pos := player.global_position).x, pos.y),
                inventory={
                    item: player.inventory.count(item)
                    for item in player.inventory.ids()
                },
            )
            for player in scene.get_group_members("player", type_hint=Player)
        ],
        # spawners=[
        #     SpawnerData(
        #         qualname=spawner.__class__.__qualname__,
        #         time_until_spawn=spawner.time_until_spawn,
        #         enteties=[
        #             EntetyData(
        #                 type_index=spawner.get_spawn_types().index(entety.__class__),
        #                 position=((pos := spawner.global_position).x, pos.y),
        #             )
        #             for entety in spawner.spawned_instances
        #         ],
        #     )
        #     for spawner in scene.get_group_members("spawner", type_hint=Spawner)
        # ],
        # tiles=[
        #     TileData(
        #         name=sprite.__class__.__name__,
        #         position=((pos := sprite.global_position).x, pos.y),
        #         color=sprite.color,
        #         texture=sprite.texture,
        #     )
        #     if sprite.color is not None
        #     else TileData(
        #         position=((pos := sprite.global_position).x, pos.y),
        #         name=sprite.__class__.__name__,
        #         texture=sprite.texture,
        #     )
        #     for sprite in Scene.current.groups[Group.NODE].values()
        #     if isinstance(sprite, Sprite)
        # ],
        # tiles=[],
    )
    settings.SAVE_FOLDER.mkdir(parents=True, exist_ok=True)
    save_path = settings.SAVE_FOLDER / "save.toml"
    with save_path.open("wb") as save_file:
        tomli_w.dump(save_data, save_file)
    ## DEV: Some work in progress, cooler styled toml
    # with Path("save.toml").open("w", encoding="utf-8") as file:
    #     file.write(f"{seed = }\n")
    #     for player in save_data["players"]:
    #         file.write(f"\n[[player]]\n")
    #         file.write(f"uid = {player['uid']}\n")
    #         file.write(f"\n[[player.inventory]]\n")
    #         for item, count in player["inventory"].items():
    #             file.write(f"{item} = {count}\n")
