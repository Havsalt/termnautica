import pygame
import colex
from charz import Sprite

from .props import Collectable, Interactable


class Ore(Interactable, Collectable, Sprite):
    _SOUND_COLLECT = pygame.mixer.Sound("assets/sounds/collect/ore.wav")
    color = colex.DARK_GRAY
    z_index = 1
    texture = ["<Unset Ore Texture>"]


class Gold(Ore):
    NAME = "gold_ore"
    color = colex.GOLDENROD
    texture = ["▓▒▓"]


class Titanium(Ore):
    NAME = "titanium_ore"
    color = colex.from_hex("#797982")
    texture = ["▒░▒"]


class Copper(Ore):
    NAME = "copper_ore"
    color = colex.from_hex("#B87333")
    texture = ["▒▓▒"]
