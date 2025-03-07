import colex
from charz import AnimatedSprite, AnimationSet, Animation, Sprite, Vec2

from .props import Collectable


class Kelp(Collectable, AnimatedSprite):
    name = "kelp"
    color = colex.SEA_GREEN
    animations = AnimationSet(
        Sway=Animation("kelp"),
    )
    transparency = " "
    texture = animations.Sway.frames[0]
    is_on_last_frame = False

    def __init__(self) -> None:
        self._supporting_sand = Sprite(
            self,
            z_index=1,
            position=Vec2(0, 6),
            texture=[",|."],
            color=colex.from_hex("#C2B280"),
        )

    def update(self, _delta: float) -> None:
        if self.is_on_last_frame:
            self.is_on_last_frame = False
            self.play("Sway")
        if not self.is_playing:
            self.is_on_last_frame = True


class Ore(Collectable, Sprite):
    color = colex.DARK_GRAY
    z_index = 1
    texture = [
        "▒░▒",
    ]

    # "ß",
    # "▒█▒ ▓░▓ █▓█ ▒░▒ ",


class Gold(Ore):
    name = "gold_ore"
    color = colex.GOLDENROD


class Titanium(Ore):
    name = "titanium_ore"
    color = colex.from_hex("#797982")


class Copper(Ore):
    name = "copper_ore"
    color = colex.from_hex("#B87333")
