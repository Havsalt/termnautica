import random
from math import pi as PI
from typing import TYPE_CHECKING

import colex
from colex import ColorValue
from charz import Sprite, AnimatedSprite, AnimationSet, Animation, Vec2, text

from .utils import randf

# Type checking for lazy loading
if TYPE_CHECKING:
    from .ocean import Water
else:
    Water = None


def _ensure_ocean_water() -> None:
    # Lazy loading - A quick workaround
    global Water
    if Water is None:
        from .ocean import Water


class Bubble(AnimatedSprite):
    _FLOAT_SPEED: float = 0.5
    _COLORS: list[ColorValue] = [
        colex.AQUA,
        colex.AQUAMARINE,
        colex.ANTIQUE_WHITE,
    ]
    centered = True
    animations = AnimationSet(
        Float=Animation("bubble/float"),
        Pop=Animation("bubble/pop"),
    )
    is_playing = True
    current_animation = animations.Float
    texture = current_animation.frames[0]

    def __init__(self) -> None:
        if random.randint(0, 1):
            self.animations.Pop.frames = list(
                map(text.flip_lines_h, self.animations.Pop.frames)
            )

    def is_submerged(self) -> bool:
        _ensure_ocean_water()
        self_height = self.global_position.y - self.get_texture_size().y / 2
        wave_height = Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def update(self) -> None:
        self.color = random.choice(self._COLORS)
        self.position.y -= self._FLOAT_SPEED
        if not self.is_submerged() and self.current_animation != self.animations.Pop:
            self.play("Pop")
        elif self.current_animation == self.animations.Pop:
            self.queue_free()
        elif not self.is_playing:
            self.play("Float")


class Particle(Sprite):
    _INITAL_SPEED: float = 1
    _INITIAL_DIRECTION: Vec2 = Vec2.UP
    _CONE: float = PI / 2
    _GRAVITY_DIRECTION: Vec2 = Vec2.DOWN
    _GRAVITY_STRENGTH: float = 1
    _COLORS: list[ColorValue] = []
    _TEXTURES: list[list[str]] = []
    _LIFETIME = 10
    _time_remaining: int = 0
    _velocity: Vec2

    def __init__(self) -> None:
        self._time_remaining = self._LIFETIME
        self.texture = random.choice(self._TEXTURES)
        self.color = random.choice(self._COLORS)
        direction = self._INITIAL_DIRECTION.normalized().rotated(
            randf(self._CONE, -self._CONE)
        )
        self._velocity = direction * self._INITAL_SPEED

    def update(self) -> None:
        self._time_remaining -= 1
        if self._time_remaining <= 0:
            self.queue_free()
        self._velocity += self._GRAVITY_DIRECTION.normalized() * self._GRAVITY_STRENGTH
        self.position += self._velocity
        self.texture = random.choice(self._TEXTURES)
        self.color = random.choice(self._COLORS)


class Blood(Particle):
    _INITAL_SPEED = 0.9
    _CONE = PI / 3
    _GRAVITY_STRENGTH = 0.1
    _COLORS = [
        colex.CRIMSON,
        colex.PINK,
        colex.INDIAN_RED,
    ]
    _TEXTURES = [
        ["*"],
        ["'"],
    ]


class Fire(Particle):
    _INITAL_SPEED = 2
    _CONE = PI / 9
    _GRAVITY_STRENGTH = 0.2
    _COLORS = [
        colex.RED,
        colex.TOMATO,
        colex.GOLD,
        colex.CRIMSON,
        colex.DARK_ORANGE,
        colex.DARK_RED,
    ]
    _TEXTURES = [
        ["^"],
        ["*"],
        ["."],
    ]


class ShineSpark(Particle):
    _LIFETIME = 3
    _INITAL_SPEED = 0.8
    _GRAVITY_STRENGTH = 0
    _COLORS = [
        colex.PURPLE,
        colex.ANTIQUE_WHITE,
        colex.PINK,
    ]
    _TEXTURES = [
        ["*"],
        ["."],
    ]
    z_index = 1
