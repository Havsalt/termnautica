import random
from enum import Enum, auto
from types import UnionType, get_original_bases
from typing import Any, Self, get_origin, get_args, assert_never

import colex
from charz import Sprite, Vec2

from .kelp import Kelp
from .particles import Bubble
from . import fish, ores


class SpawnMode(Enum):
    RANDOM = auto()
    ALL = auto()
    ALL_UNTIL = auto()
    FILL = auto()
    # CYCLE = auto()


# TODO: Implement
class Spawner[T: Sprite](Sprite):
    SPAWN_INTERVAL: int = 100
    SPAWN_OFFSET: Vec2 = Vec2.ZERO
    MAX_ACTIVE_SPAWNS: int = 1
    SPAWN_MODE: SpawnMode = SpawnMode.RANDOM
    INITIAL_SPAWN: bool = True
    color = colex.BLACK
    texture = ["<Unset Spawner Texture>"]
    _time_until_spawn: int = 0
    _spawned_instances: list[T]  # TODO: Remove from list when freed

    # Make unique in `__new__`, so `__init__` can be used to init spawner
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls, *args, **kwargs)
        instance._spawned_instances = []  # Make unique
        if not instance.INITIAL_SPAWN:
            instance._time_until_spawn = instance.SPAWN_INTERVAL
        return instance

    # NOTE: Might be slow
    def check_active_spawns_count(self) -> int:
        # NOTE: SIDE EFFECT: Remove from `_spawned_instances` if instance not alive
        count = 0
        for instance in self._spawned_instances:
            if instance.uid in Sprite.texture_instances:
                count += 1
            else:
                self._spawned_instances.remove(instance)
        return count

    def update(self, _delta: float) -> None:
        self._time_until_spawn -= 1
        # NOTE: Keep commented code in case of bad performance
        # if self._time_until_spawn <= 0:
        #     if self.check_active_spawns_count() < self.MAX_ACTIVE_SPAWNS:
        #         self._time_until_spawn = self.SPAWN_INTERVAL
        #         self.spawn()
        #     else:
        #         self._time_until_spawn = self.SPAWN_INTERVAL
        # NOTE: This implementation is worse in performance,
        #       as it does a lot of lookups *each* frame.
        #       However, it is better gamewise, as the spawn cooldown is not synced
        if self.check_active_spawns_count() < self.MAX_ACTIVE_SPAWNS:
            if self._time_until_spawn <= 0:
                self._time_until_spawn = self.SPAWN_INTERVAL
                self.spawn()
        else:
            self._time_until_spawn = self.SPAWN_INTERVAL

    def spawn(self) -> None:
        kinds = self._get_spawn_types()

        match self.SPAWN_MODE:
            case SpawnMode.RANDOM:
                kind = random.choice(kinds)
                # instance = kind()
                instance = kind().with_global_position(
                    self.global_position + self.SPAWN_OFFSET
                )
                self.init_spawned(instance)
                self._spawned_instances.append(instance)

            case SpawnMode.ALL:
                for kind in kinds:
                    instance = kind().with_global_position(
                        self.global_position + self.SPAWN_OFFSET
                    )
                    self.init_spawned(instance)
                    self._spawned_instances.append(instance)

            case SpawnMode.ALL_UNTIL:
                for kind in random.choices(kinds, k=len(kinds)):  # Shuffle random
                    instance = kind().with_global_position(
                        self.global_position + self.SPAWN_OFFSET
                    )
                    self.init_spawned(instance)
                    self._spawned_instances.append(instance)
                    if len(self._spawned_instances) >= self.MAX_ACTIVE_SPAWNS:
                        break

            case SpawnMode.FILL:
                while len(self._spawned_instances) < self.MAX_ACTIVE_SPAWNS:
                    kind = random.choice(kinds)
                    instance = kind().with_global_position(
                        self.global_position + self.SPAWN_OFFSET
                    )
                    self.init_spawned(instance)
                    self._spawned_instances.append(instance)

            case _ as never:
                assert_never(never)

    def init_spawned(self, instance: T) -> None: ...

    def _get_spawn_types(self) -> tuple[type, ...]:
        kind = get_original_bases(self.__class__)[0].__args__[0]
        if get_origin(kind) is UnionType:
            return get_args(kind)
        return (kind,)


class KelpSpawner(Spawner[Kelp]):
    SPAWN_OFFSET = Vec2(0, -6)
    position = Vec2(1, 1)
    color = colex.from_hex("#C2B280")
    centered = True
    texture = [",|."]


class OreSpawner(Spawner[ores.Gold | ores.Titanium | ores.Copper]):
    SPAWN_OFFSET = Vec2(-1, 0)
    position = Vec2.ZERO
    color = colex.GRAY
    texture = ["."]


# Coral
class FishSpawner(
    Spawner[fish.SmallFish | fish.MediumFish | fish.LongFish | fish.WaterFish]
):
    INITIAL_SPAWN = False
    MAX_ACTIVE_SPAWNS = 2
    SPAWN_MODE = SpawnMode.RANDOM
    position = Vec2(0, 1)
    centered = True
    color = colex.CORAL
    texture = ["o."]


class BubbleSpawner(Spawner[Bubble]):
    INITIAL_SPAWN = False
    SPAWN_INTERVAL = 8
    MAX_ACTIVE_SPAWNS = 2
    position = Vec2.ZERO
    centered = True
    visible = False

    def __init__(self) -> None:
        self._time_until_spawn = random.randint(0, self.SPAWN_INTERVAL)

    def init_spawned(self, instance: Bubble) -> None:
        instance.z_index -= 2  # Hide behind `OceanFloor`
