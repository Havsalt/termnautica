import colex
from charz import Sprite

from .props import Collectable, Interactable


class Ore(Interactable, Collectable, Sprite):
    color = colex.DARK_GRAY
    z_index = 1
    texture = ["<Unset Ore Texture>"]


class Gold(Ore):
    name = "gold_ore"
    color = colex.GOLDENROD
    texture = ["▓▒▓"]


class Titanium(Ore):
    name = "titanium_ore"
    color = colex.from_hex("#797982")
    texture = ["▒░▒"]


class Copper(Ore):
    name = "copper_ore"
    color = colex.from_hex("#B87333")
    texture = ["▒▓▒"]
