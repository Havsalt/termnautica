import colex
from charz import Sprite, Label, Vec2, load_texture

from .props import Interactable


# TODO: Crafting | Fabricatror (Medkit), Radio, O2, Power (Solar), Storage
class Lifepod(Interactable, Sprite):
    name = "lifepod mk8"
    z_index = -2  # Increase when stepping into
    color = colex.BOLD + colex.WHITE
    centered = True
    texture = load_texture("python/sprites/lifepod")

    def __init__(self) -> None:
        self._name = Label(
            self,
            text="Lifepod",
            color=colex.ITALIC + colex.SLATE_GRAY,
            position=self.texture_size / -2,
        )
        self._name.position.y -= 3
