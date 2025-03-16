import colex
from charz import Sprite, Collider, Hitbox, Vec2, load_texture

from ..player import Player
from ..props import Interactable


class Airlock(Interactable, Collider, Sprite):
    hitbox = Hitbox(size=Vec2(1, 3))
    color = colex.LIGHT_GRAY
    texture = load_texture("airlock/closed.txt")
    disabled: bool = False

    def on_interact(self, interactor: Player) -> None:
        self.disabled = not self.disabled
        # TEMP FIX:
        interactor.disabled = self.disabled

        if self.disabled:
            self.texture = load_texture("airlock/open.txt")
        else:
            self.texture = load_texture("airlock/closed.txt")
