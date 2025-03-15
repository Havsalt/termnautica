import random

import colex
from charz import AnimatedSprite, AnimationSet, Animation, Vec2, text

from .props import Eatable, Interactable, Collectable
from . import ocean


# Expand text flipping db
text._h_conversions["»"] = "«"
text._h_conversions["«"] = "»"


class BirdAI:
    _SPEED_SCALE: float = 0.3
    _is_on_last_frame: bool = False

    def update(self, _delta: float) -> None:
        assert isinstance(self, AnimatedSprite)

        if self._is_on_last_frame:
            self._is_on_last_frame = False
            self.play("Flap")
        if not self.is_playing:
            self._is_on_last_frame = True

        velocity = Vec2(
            random.randint(-1, 1),
            random.randint(-1, 1),
        )
        self.position += velocity * self._SPEED_SCALE
        while self.global_position.y > ocean.Water.wave_height_at(
            self.global_position.x
        ):
            self.global_position += Vec2.UP


class BaseBird(BirdAI, Eatable, Interactable, Collectable, AnimatedSprite):
    transparency = "."
    centered = True


class SmallBird(BaseBird):
    animations = AnimationSet(
        Flap=Animation("birds/small/flap"),
    )
    color = colex.SADDLE_BROWN
    texture = animations.Flap.frames[0]


class MediumBird(BaseBird):
    animations = AnimationSet(
        Flap=Animation("birds/medium/flap"),
    )
    color = colex.LIGHT_GRAY
    texture = ["V"]
    texture = animations.Flap.frames[0]


class LargeBird(BaseBird):
    animations = AnimationSet(
        Flap=Animation("birds/large/flap"),
    )
    color = colex.BURLY_WOOD
    texture = ["V"]
    texture = animations.Flap.frames[0]
