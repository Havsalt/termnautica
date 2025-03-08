import random

import colex
from charz import Sprite, text, sign

from .props import Collectable, Interactable, Eatable


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


class BaseFish(FishAI, Eatable, Interactable, Collectable, Sprite): ...


class SmallFish(BaseFish):
    name = "gold_fish"
    color = colex.DARK_SALMON
    centered = True
    texture = ["<><"]


class MediumFish(BaseFish):
    name = "cod"
    color = colex.from_hex("#659285")
    centered = True
    texture = ["<[Xx"]


class LongFish(BaseFish):
    name = "salmon"
    color = colex.SALMON
    centered = True
    texture = ["<º)))))}><"]


class WaterFish(BaseFish):
    name = "bladder fish"
    color = colex.PINK
    texture = ["<?))<>"]
