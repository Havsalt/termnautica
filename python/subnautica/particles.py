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
    texture = animations.Float.frames[0]
    # FIXME: Temp fix until fixed in `charz`
    _has_updated: bool = True

    def __init__(self) -> None:
        if random.randint(0, 1):
            self.animations.Pop.frames = list(
                map(text.flip_lines_h, self.animations.Pop.frames)
            )

    def is_submerged(self) -> bool:
        _ensure_ocean_water()
        self_height = self.global_position.y - self.texture_size.y / 2
        wave_height = Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def update(self, _delta: float) -> None:
        self.color = random.choice(self._COLORS)
        self.position.y -= self._FLOAT_SPEED
        if not self.is_submerged() and self.current_animation != self.animations.Pop:
            self._has_updated = False
            self.play("Pop")
        elif self._has_updated and self.current_animation == self.animations.Pop:
            self.queue_free()
        elif not self._has_updated:
            self._has_updated = True
        elif not self.is_playing:
            self._has_updated = False
            self.play("Float")


class Blood(Sprite):
    _INITAL_SPEED: float = 0.9
    _GRAVITY: float = 0.1
    _CONE: float = PI / 3
    _COLORS: list[ColorValue] = [
        colex.CRIMSON,
        colex.PINK,
        colex.INDIAN_RED,
    ]
    _TEXTURES: list[list[str]] = [
        ["*"],
        ["'"],
    ]
    texture = ["*"]
    _time_remaining: int = 10
    _direction: Vec2

    def __init__(self) -> None:
        self.texture = random.choice(self._TEXTURES)
        self.color = random.choice(self._COLORS)
        self._direction = (
            Vec2.UP.rotated(randf(self._CONE, -self._CONE)) * self._INITAL_SPEED
        )

    def update(self, _delta: float) -> None:
        self._time_remaining -= 1
        if self._time_remaining <= 0:
            self.queue_free()
        self._direction += Vec2.DOWN * self._GRAVITY
        self.position += self._direction
        self.texture = random.choice(self._TEXTURES)
        self.color = random.choice(self._COLORS)
