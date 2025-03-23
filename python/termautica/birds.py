import random

import colex
from charz import AnimatedSprite, AnimationSet, Animation, Vec2, text

from .props import Interactable, Collectable
from . import ocean


# Expand text flipping DB
text._h_conversions["»"] = "«"
text._h_conversions["«"] = "»"


class BirdAI:
    _SPEED_SCALE: float = 0.3

    def update(self, _delta: float) -> None:
        assert isinstance(self, AnimatedSprite)

        velocity = Vec2(
            random.randint(-1, 1),
            random.randint(-1, 1),
        )
        self.position += velocity * self._SPEED_SCALE
        while self.global_position.y > ocean.Water.wave_height_at(
            self.global_position.x
        ):
            self.global_position += Vec2.UP

        if random.randint(1, 100) < 30:
            self.texture = text.flip_lines_h(self.texture)


class BaseBird(BirdAI, Interactable, Collectable, AnimatedSprite):
    transparency = "."
    centered = True
    repeat = True
    is_playing = True


class SmallBird(BaseBird):
    animations = AnimationSet(
        Flap=Animation("birds/small/flap"),
    )
    color = colex.SADDLE_BROWN
    current_animation = animations.Flap
    texture = current_animation.frames[0]


class MediumBird(BaseBird):
    animations = AnimationSet(
        Flap=Animation("birds/medium/flap"),
    )
    color = colex.LIGHT_GRAY
    texture = ["V"]
    current_animation = animations.Flap
    texture = current_animation.frames[0]


class LargeBird(BaseBird):
    animations = AnimationSet(
        Flap=Animation("birds/large/flap"),
    )
    color = colex.BURLY_WOOD
    texture = ["V"]
    current_animation = animations.Flap
    texture = current_animation.frames[0]
