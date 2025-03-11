import random
from math import sin, pi as PI
from typing import Self, ClassVar

import colex
from charz import Sprite, Vec2, Vec2i

from . import spawners
from .utils import groupwise, randf


type Coordinate = tuple[int, int]


# TODO: Add spawning requirements, like min and max height
# NOTE: Order will be randomized for each attempt
# Percent in int | Min 1, Max 100
SPAWN_CHANCES: dict[type[spawners.Spawner], int] = {
    spawners.KelpSpawner: 10,
    spawners.OreSpawner: 4,
    spawners.FishSpawner: 1,
    spawners.BubbleSpawner: 1,
}


class OceanFloor(Sprite):
    z_index = -1
    color = colex.from_hex("#C2B280")
    texture = ["_"]


class OceanWater(Sprite):
    _REST_LEVEL: float = 0  # Where the ocean rests, in world space
    _WAVE_AMPLITUDE: float = 2
    _WAVE_INTERVAL: float = 3 * 16  # frames
    _WAVE_DURATION: float = 3 * 16  # frames
    _WAVE_LENGTH: float = 100
    z_index = -1
    color = colex.MEDIUM_AQUAMARINE  # + colex.from_rgb(0, 150, 255, background=True)
    texture = ["~"]
    _wave_time_remaining: ClassVar[float] = 0
    _rest_location: Vec2

    @classmethod
    def advance_wave_time(cls) -> None:  # Call from `App.update`
        cls._wave_time_remaining -= 1
        if cls._wave_time_remaining < 0:
            cls._wave_time_remaining = cls._WAVE_DURATION

    @classmethod
    def wave_height_at(cls, wave_origin_x: float) -> float:
        """Calculate wave height at global location

        Args:
            wave_origin (Vec2): global origin of wave

        Returns:
            float: global wave height
        """
        # Write in math symbols that I'm used to
        phi = wave_origin_x / cls._WAVE_LENGTH
        x = cls._wave_time_remaining / cls._WAVE_INTERVAL
        # Asin(cx + phi) + d
        return cls._WAVE_AMPLITUDE * sin(2 * PI * x + phi) + cls._REST_LEVEL

    def save_rest_location(self) -> Self:
        self._rest_location = self.global_position
        return self

    def update(self, _delta: float) -> None:
        # Asin(cx + phi) + d
        self.position.y = (
            self.wave_height_at(self._rest_location.x) + self._rest_location.y
        )


class Ocean(dict[Coordinate, OceanWater | OceanFloor]):
    _WIDTH: int = 500

    def __init__(self) -> None:
        self.generate_ocean_floor()
        self.generate_ocean_water()

    def generate_ocean_water(self) -> None:
        for x in range(self._WIDTH):
            (
                OceanWater()
                .with_position(
                    x=x - self._WIDTH // 2,
                    y=random.randint(0, 1),
                )
                .save_rest_location()
            )

    def generate_ocean_floor(self):
        height = 0
        points: list[Vec2i] = []
        for x_position in range(self._WIDTH):
            height += randf(-1, 1)
            point = Vec2i(
                x_position - self._WIDTH // 2,
                int(height) + 15,
            )
            points.append(point)
        # FIXME: Implement properly - Almost working
        for prev, curr, peak in groupwise(points, n=3):
            is_climbing = peak.y - curr.y < 0
            is_flatting = abs(peak.y - curr.y) < 0.8
            was_dropping = curr.y - prev.y > 0
            if is_flatting:
                ocean_floor = OceanFloor(position=curr)
            elif is_climbing and was_dropping:
                ocean_floor = OceanFloor(position=curr, texture=["V"])
            elif not is_climbing and not was_dropping:
                ocean_floor = OceanFloor(position=curr, texture=["A"])
            elif is_climbing:
                ocean_floor = OceanFloor(position=curr, texture=["/"])
            elif not is_climbing:
                ocean_floor = OceanFloor(position=curr, texture=["\\"])
            else:
                ocean_floor = OceanFloor(position=curr)
            # Make rock color if high up
            if curr.y < 10:
                ocean_floor.color = colex.GRAY
            # Store ref - For faster collision
            self[curr.to_tuple()] = ocean_floor
            self.attempt_generate_spawner_at(curr)

    def attempt_generate_spawner_at(self, location: Vec2) -> None:
        all_spawners = list(SPAWN_CHANCES.keys())
        random.shuffle(all_spawners)
        for spawner in all_spawners:
            chance = SPAWN_CHANCES[spawner]
            if random.randint(1, 100) <= chance:
                spawner().with_global_position(location + spawner.position)
                break
