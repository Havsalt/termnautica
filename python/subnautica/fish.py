import random
from enum import ReprEnum, Enum, auto
from typing import TYPE_CHECKING, assert_never

import pygame
import colex
from charz import Sprite, Vec2, text, clamp

from .props import Collectable, Interactable, Eatable
from .utils import move_toward

# Type checking for lazy loading
if TYPE_CHECKING:
    from . import ocean
else:
    ocean = None


def _ensure_ocean() -> None:
    # Lazy loading - A quick workaround
    global ocean
    if ocean is None:
        from . import ocean


type MinFrameTime = int
type MaxFrameTime = int


class FishState(tuple[MinFrameTime, MaxFrameTime], ReprEnum):
    IDLE = (43, 63)
    WANDRING = (17, 87)
    FLEEING = (20, 40)
    FLOATING = (30, 42)


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()


class FishAI:
    _SPEED_SCALE: float = 0.1
    _ACCELERATION: Vec2 = Vec2(0.2, 1.1)
    _FRICTION: Vec2 = Vec2(0.15, 0.50)
    _MAX_SPEED: Vec2 = Vec2(7, 10)
    _QUICK_FACTOR: float = 3
    speed_x: float = 0
    speed_y: float = 0
    _state: FishState = FishState.IDLE
    _direction: Direction = Direction.LEFT  # Sprites are drawn facing left
    _action_time_remaining: int = 0
    assert _ACCELERATION > _FRICTION, "invalid constant values"

    def update(self, _delta: float) -> None:
        assert isinstance(self, Sprite), f"`Sprite` base missing for {self}"

        if self.is_submerged():  # Activate AI when in water
            self._action_time_remaining -= 1
            if self._action_time_remaining <= 0:
                states = tuple(FishState._member_map_.values())  # type: tuple[FishState, ...]  # type: ignore
                self._state = (min_time, max_time) = random.choice(states)
                self._action_time_remaining = random.randint(min_time, max_time)
                self._direction = Direction.NONE
                # Random change of Y-level
                self.position.y += random.randint(-1, 1)

        match self._state:
            case FishState.IDLE:
                self.speed_x = move_toward(self.speed_x, 0, self._FRICTION.x)
                self.position.x += self.speed_x * self._SPEED_SCALE
            case FishState.WANDRING:
                self.move()
            case FishState.FLEEING:
                self.move(quick=True)
            case FishState.FLOATING:
                self.position.x += self.speed_x * self._SPEED_SCALE
            case _ as never:
                assert_never(never)

        # Fall if above ocean top - Gravity
        if self.is_submerged():
            self.speed_y = move_toward(self.speed_y, 0, self._FRICTION.y)
            while ocean.Floor.has_loose_point_inside(self.global_position):
                self.position += Vec2.UP
        else:
            self.speed_y += self._ACCELERATION.y
            self.speed_y = clamp(self.speed_y, -self._MAX_SPEED.y, self._MAX_SPEED.y)
        self.position.y += self.speed_y * self._SPEED_SCALE

    def is_submerged(self) -> bool:
        _ensure_ocean()  # Lazy load `OceanWater`
        assert isinstance(self, Sprite), f"`Sprite` base missing for {self}"
        self_height = self.global_position.y - self.texture_size.y / 2
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def move(self, quick: bool = False) -> None:
        assert isinstance(self, Sprite), f"`Sprite` base missing for {self}"

        acceleration = (
            self._ACCELERATION.x
            if not quick
            else self._QUICK_FACTOR * self._ACCELERATION.x
        )

        if self._direction is Direction.NONE:
            if random.randint(0, 1):
                self._direction = Direction.LEFT
                self.texture = self.__class__.texture
            else:
                self._direction = Direction.RIGHT
                self.texture = text.flip_lines_h(self.__class__.texture)

        if self._direction is Direction.LEFT:
            self.speed_x -= acceleration
        elif self._direction is Direction.RIGHT:
            self.speed_x += acceleration
        self.speed_x = clamp(self.speed_x, -self._MAX_SPEED.x, self._MAX_SPEED.x)

        self.position.x += self.speed_x * 0.1
        if not quick:  # Friction when moving normal
            self.speed_x = move_toward(self.speed_x, 0, self._FRICTION.x)


class BaseFish(FishAI, Eatable, Interactable, Collectable, Sprite):
    _SOUND_COLLECT = pygame.mixer.Sound("assets/sounds/collect/fish.wav")
    centered = True


class SmallFish(BaseFish):
    NAME = "gold_fish"
    color = colex.DARK_SALMON
    texture = ["<><"]


class MediumFish(BaseFish):
    NAME = "cod"
    color = colex.from_hex("#659285")
    texture = ["<[Xx"]


class LongFish(BaseFish):
    NAME = "salmon"
    color = colex.SALMON
    texture = ["<º)))))}><"]


class WaterFish(BaseFish):
    NAME = "bladder fish"
    color = colex.PINK
    texture = ["<?))>("]
