import pygame
import colex
from charz import AnimatedSprite, AnimationSet, Animation, Sprite, Vec2

from .props import Collectable, Interactable
from .item import ItemID


class Kelp(Interactable, Collectable, AnimatedSprite):
    ID = ItemID.KELP
    color = colex.SEA_GREEN
    transparency = " "
    animations = AnimationSet(
        Sway=Animation("kelp"),
    )
    repeat = True
    is_playing = True
    current_animation = animations.Sway
    texture = current_animation.frames[0]

    def __init__(self) -> None:
        self._supporting_sand = Sprite(
            self,
            z_index=1,
            position=Vec2(0, 6),
            texture=[",|."],
            color=colex.from_hex("#C2B280"),
        )
