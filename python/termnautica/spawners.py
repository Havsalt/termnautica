import random
from enum import Enum, auto
from types import UnionType, get_original_bases
from typing import Any, Self, get_origin, get_args, assert_never

import colex
from charz import Sprite, Vec2

from . import fish, ores, ocean
from .kelp import Kelp
from .particles import Bubble


class SpawnMode(Enum):
    RANDOM = auto()
    ALL = auto()
    ALL_UNTIL = auto()
    FILL = auto()
    # CYCLE = auto()


# TODO: Implement
class Spawner[T: Sprite](Sprite):
    _SPAWN_INTERVAL: int = 100
    _SPAWN_OFFSET: Vec2 = Vec2.ZERO
    _MAX_ACTIVE_SPAWNS: int = 1
    _SPAWN_MODE: SpawnMode = SpawnMode.RANDOM
    _INITIAL_SPAWN: bool = True
    color = colex.BLACK
    texture = ["<Unset Spawner Texture>"]
    _time_until_spawn: int = 0
    _spawned_instances: list[T]  # TODO: Remove from list when freed

    # Make unique in `__new__`, so `__init__` can be used to init spawner
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls, *args, **kwargs)
        instance._spawned_instances = []  # Make unique
        if not instance._INITIAL_SPAWN:
            instance._time_until_spawn = instance._SPAWN_INTERVAL
        return instance

    def check_active_spawns_count(self) -> int:
        # NOTE: SIDE EFFECT: Remove from `_spawned_instances` if instance not alive
        count = 0
        for instance in self._spawned_instances:  # O(n) loop
            if instance.uid in Sprite.texture_instances:  # O(1) lookup
                count += 1
            else:
                self._spawned_instances.remove(instance)
        return count

    def update(self, _delta: float) -> None:
        self._time_until_spawn -= 1
        if self.check_active_spawns_count() < self._MAX_ACTIVE_SPAWNS:
            if self._time_until_spawn <= 0:
                self._time_until_spawn = self._SPAWN_INTERVAL
                self.spawn()
        else:
            self._time_until_spawn = self._SPAWN_INTERVAL

    def spawn(self) -> None:
        kinds = self._get_spawn_types()

        match self._SPAWN_MODE:
            case SpawnMode.RANDOM:
                kind = random.choice(kinds)
                # instance = kind()
                instance = kind().with_global_position(
                    self.global_position + self._SPAWN_OFFSET
                )
                self.init_spawned(instance)
                self._spawned_instances.append(instance)

            case SpawnMode.ALL:
                for kind in kinds:
                    instance = kind().with_global_position(
                        self.global_position + self._SPAWN_OFFSET
                    )
                    self.init_spawned(instance)
                    self._spawned_instances.append(instance)

            case SpawnMode.ALL_UNTIL:
                for kind in random.choices(kinds, k=len(kinds)):  # Shuffle random
                    instance = kind().with_global_position(
                        self.global_position + self._SPAWN_OFFSET
                    )
                    self.init_spawned(instance)
                    self._spawned_instances.append(instance)
                    if len(self._spawned_instances) >= self._MAX_ACTIVE_SPAWNS:
                        break

            case SpawnMode.FILL:
                while len(self._spawned_instances) < self._MAX_ACTIVE_SPAWNS:
                    kind = random.choice(kinds)
                    instance = kind().with_global_position(
                        self.global_position + self._SPAWN_OFFSET
                    )
                    self.init_spawned(instance)
                    self._spawned_instances.append(instance)

            case _:
                assert_never(self._SPAWN_MODE)

    def init_spawned(self, instance: T) -> None: ...

    def _get_spawn_types(self) -> tuple[type[T], ...]:
        kind = get_original_bases(self.__class__)[0].__args__[0]
        if get_origin(kind) is UnionType:
            return get_args(kind)
        return (kind,)


class KelpSpawner(Spawner[Kelp]):
    _SPAWN_OFFSET = Vec2(0, -6)
    position = Vec2(1, 1)
    color = colex.from_hex("#C2B280")
    centered = True
    texture = [",|."]

    def init_spawned(self, instance: Kelp) -> None:
        assert instance.current_animation is not None, "Animation should have started"
        instance._frame_index = random.randint(
            0,
            len(instance.current_animation.frames) - 1,
        )


class OreSpawner(Spawner[ores.Gold | ores.Titanium | ores.Copper | ores.Coal]):
    _SPAWN_OFFSET = Vec2(-1, 0)
    position = Vec2.ZERO
    color = colex.GRAY
    texture = ["."]


class CrystalSpawner(Spawner[ores.Crystal]):
    _SPAWN_OFFSET = Vec2(-1, 0)
    position = Vec2(-1, 0)
    color = colex.ANTIQUE_WHITE
    texture = ["."]


class DiamondOreSpawner(Spawner[ores.Diamond]):
    _SPAWN_OFFSET = Vec2(-1, 0)
    position = Vec2(-1, 0)
    color = colex.AZURE
    texture = ["_"]


# Coral
class FishSpawner(
    Spawner[fish.SmallFish | fish.MediumFish | fish.LongFish | fish.WaterFish]
):
    _INITIAL_SPAWN = False
    _MAX_ACTIVE_SPAWNS = 2
    _SPAWN_MODE = SpawnMode.RANDOM
    position = Vec2(0, 1)
    centered = True
    color = colex.CORAL
    texture = ["o."]

    def init_spawned(
        self,
        instance: fish.SmallFish | fish.MediumFish | fish.LongFish | fish.WaterFish,
    ) -> None:
        while ocean.Floor.has_loose_point_inside(instance.global_position):
            instance.position += Vec2.UP


class BubbleSpawner(Spawner[Bubble]):
    _INITIAL_SPAWN = False
    _SPAWN_INTERVAL = 8
    _MAX_ACTIVE_SPAWNS = 2
    position = Vec2.ZERO
    centered = True
    visible = False

    def __init__(self) -> None:
        self._time_until_spawn = random.randint(0, self._SPAWN_INTERVAL)

    def init_spawned(self, instance: Bubble) -> None:
        instance.z_index -= 2  # Hide behind `OceanFloor`
