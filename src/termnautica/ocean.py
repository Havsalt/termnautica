import random
from math import sin, floor, pi as PI
from typing import Self, ClassVar

import colex
from charz import Sprite, Vec2, Vec2i

from . import settings, spawners
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
DEPTH_LAYERS: tuple[int, ...] = (
    20,  # Tier 0 - "Safe"
    40,  # Tier 1
    60,  # TIer 2
)


class Floor(Sprite):
    REST_DEPTH: int = 30
    ROCK_START_HEIGHT: int = -10
    z_index = -1
    color = colex.from_hex("#C2B280")
    texture = ["_"]
    # TODO: Might be faster to have `points` be of type `dict[int, int]`,
    #       where the key is X-position, and value is Y-position.
    #       This way, an instant lookup can be done on X-position,
    #       which is the first required information part
    points: ClassVar[set[Coordinate]] = set()

    @classmethod
    def has_point_inside(cls, point: Coordinate) -> bool:
        # With "Inside", I mean under any tile in Y-axis (including tile location itself)
        for floor in cls.points:
            if floor[0] == point[0] and floor[1] <= point[1]:
                return True
        return False

    @classmethod
    def has_loose_point_inside(cls, point: Vec2) -> bool:
        snapped = tuple(map(int, point))
        assert len(snapped) == 2
        return cls.has_point_inside(snapped)


class Water(Sprite):
    REST_LEVEL: float = 0  # Where the ocean rests, in world space
    _WAVE_AMPLITUDE: float = 2
    _WAVE_INTERVAL: float = 3 * settings.FPS  # Frames
    _WAVE_DURATION: float = 3 * settings.FPS  # Frames
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
        return cls._WAVE_AMPLITUDE * sin(2 * PI * x + phi) + cls.REST_LEVEL

    def save_rest_location(self) -> Self:
        self._rest_location = self.global_position
        return self

    def update(self) -> None:
        # Asin(cx + phi) + d
        self.position.y = floor(
            self.wave_height_at(self._rest_location.x) + self._rest_location.y
        )


class Abyss:
    SPAWN_CHANCE: ClassVar[int] = 200  # 1 out of X chance
    MIN_WIDTH: ClassVar[int] = 10
    MAX_WIDTH: ClassVar[int] = 20
    MIN_DEPTH: ClassVar[int] = 20
    MAX_DEPTH: ClassVar[int] = 60
    length_left: ClassVar[int] = 0
    current_depth: ClassVar[int] = 0
    just_began: ClassVar[bool] = False
    just_ended: ClassVar[bool] = False
    floor_points: ClassVar[set[Coordinate]] = set()


def generate_water() -> None:
    for x in range(settings.WORLD_WIDTH):
        (
            Water()
            .with_position(
                x=x - settings.WORLD_WIDTH // 2,
                y=random.randint(0, 1),
            )
            .save_rest_location()
        )


def attempt_generate_spawner_at(location: Vec2) -> None:
    all_spawners = list(SPAWN_CHANCES.keys())
    random.shuffle(all_spawners)
    for spawner in all_spawners:
        chance = SPAWN_CHANCES[spawner]
        if random.randint(1, 100) <= chance:
            spawner().with_global_position(location + spawner.position)
            break


def generate_floor():
    depth = 0
    texture_points: list[Vec2] = []

    for x_position in range(-settings.WORLD_WIDTH // 2, settings.WORLD_WIDTH // 2):
        # Check if starting to generate an abyss
        if not Abyss.length_left and random.randint(1, Abyss.SPAWN_CHANCE) == 1:
            Abyss.just_began = True
            Abyss.current_depth = random.randint(
                Abyss.MIN_DEPTH,
                Abyss.MAX_DEPTH,
            )
            Abyss.length_left = random.randint(
                Abyss.MIN_WIDTH,
                Abyss.MAX_WIDTH,
            )

        depth += randf(-1, 1)
        point = Vec2i(x_position, int(depth) + Floor.REST_DEPTH)

        if Abyss.length_left:
            point.y += Abyss.current_depth
            Abyss.floor_points.add((point.x, point.y))
            Abyss.length_left -= 1
            if Abyss.length_left == 0:
                Abyss.just_ended = True

        # Temp point - For deciding texture
        texture_points.append(point)

        # Generate abyss walls + `CrystalSpawner`
        if Abyss.just_began or Abyss.just_ended:
            Abyss.just_ended = False
            Abyss.just_began = False
            for i in range(Abyss.current_depth):
                abyss_wall_point = Vec2i(
                    x_position,
                    int(depth) + Floor.REST_DEPTH + i,
                )
                abyss_wall_point.x += random.randint(-1, 0)
                Floor.points.add((abyss_wall_point.x, abyss_wall_point.y))
                texture_points.append(abyss_wall_point)
                if random.randint(1, 30) == 1:
                    spawners.CrystalSpawner().with_global_position(
                        abyss_wall_point + spawners.CrystalSpawner.position
                    )

        # Store point over time - Used for collision
        Floor.points.add((point.x, point.y))

    # FIXME: Implement properly - Almost working
    for prev, curr, peak in groupwise(texture_points, n=3):
        is_climbing = peak.y - curr.y < 0
        is_flatting = abs(peak.y - curr.y) < 0.8
        was_dropping = curr.y - prev.y > 0
        is_steep = curr.y - prev.y >= 1 and peak.y - curr.y >= 1
        if is_steep:
            ocean_floor = Floor(position=curr, texture=["|"])
            if random.randint(1, 3) == 1:
                if random.randint(1, 2) == 1:
                    ocean_floor.texture = ["<"]
                else:
                    ocean_floor.texture = [">"]
        elif is_flatting:
            ocean_floor = Floor(position=curr)
        elif is_climbing and was_dropping:
            ocean_floor = Floor(position=curr, texture=["V"])
        elif not is_climbing and not was_dropping:
            ocean_floor = Floor(position=curr, texture=["A"])
        elif is_climbing:
            ocean_floor = Floor(position=curr, texture=["/"])
        elif not is_climbing:
            ocean_floor = Floor(position=curr, texture=["\\"])
        else:
            ocean_floor = Floor(position=curr)
        # Make rock color if high up
        if curr.y <= Floor.ROCK_START_HEIGHT:
            ocean_floor.color = colex.GRAY
        if is_steep:  # Don't generate spawners in too steep terrain
            continue
        snapped = (
            floor(curr.x),
            floor(curr.y),
        )
        if snapped in Abyss.floor_points:
            if random.randint(1, 8) == 1:
                spawners.DiamondOreSpawner().with_global_position(
                    curr + spawners.DiamondOreSpawner.position
                )
            continue
        attempt_generate_spawner_at(curr)
