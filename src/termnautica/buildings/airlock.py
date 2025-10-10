import colex
from charz import Sprite, ColliderComponent, Hitbox, Vec2, load_texture

from ..player import Player
from ..props import Interactable


class Airlock(Interactable, ColliderComponent, Sprite):
    hitbox = Hitbox(size=Vec2(1, 3))
    color = colex.LIGHT_GRAY
    texture = load_texture("airlock/closed.txt")

    def on_interact(self, interactor: Sprite) -> None:
        assert isinstance(
            interactor,
            Player,
        ), "Only `Player` can interact with `Airlock`"
        self.hitbox.disabled = not self.hitbox.disabled
        # TEMP FIX:
        interactor.hitbox.disabled = self.hitbox.disabled

        if self.hitbox.disabled:
            self.texture = load_texture("airlock/open.txt")
        else:
            self.texture = load_texture("airlock/closed.txt")
