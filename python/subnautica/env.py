import random

import colex
from charz import AnimatedSprite, AnimationSet, Animation, Sprite, Vec2, text, sign

from .interactable import Interactable


class FishAI:
    ACCELERATION: float = 10
    speed: float = 0

    def update(self, _delta: float) -> None:
        assert isinstance(self, Sprite), "`Sprite` base missing"
        direction = random.randint(-1, 1)
        if sign(direction) == -1:
            self.texture = self.__class__.texture
        elif sign(direction) == 1:
            self.texture = text.flip_lines_h(self.__class__.texture)
        self.speed += direction * self.ACCELERATION
        self.position.x += direction


class SmallFish(FishAI, Interactable, Sprite):
    name = "gold_fish"
    color = colex.DARK_SALMON
    centered = True
    texture = ["<><"]


class Fish(FishAI, Interactable, Sprite):
    name = "cod"
    color = colex.from_hex("#659285")
    centered = True
    texture = ["<[Xx"]


class LongFish(FishAI, Interactable, Sprite):
    name = "salmon"
    color = colex.SALMON
    centered = True
    texture = ["<º)))))}><"]


class WaterFish(FishAI, Interactable, Sprite):
    name = "bladder fish"
    color = colex.PINK
    texture = ["<?))<>"]


class Kelp(Interactable, AnimatedSprite):
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


class Ore(Interactable, Sprite):
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
