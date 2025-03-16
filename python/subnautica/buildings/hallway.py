import colex
from charz import Sprite, Collider, Hitbox, Node2D, Vec2, load_texture

from .airlock import Airlock


class HallwayRoof(Collider, Node2D):
    hitbox = Hitbox(size=Vec2(29, 1))


class Hallway(Sprite):
    transparency = " "
    color = colex.WHITE
    texture = load_texture("modules/hallway.txt")

    def __init__(self) -> None:
        HallwayRoof(self, position=Vec2(0, 2))
        HallwayRoof(self, position=Vec2(0, 4))
        Airlock(self, position=Vec2(1, 1))
        Airlock(self, position=Vec2(27, 1))
