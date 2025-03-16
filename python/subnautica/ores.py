import pygame
import colex
from charz import Sprite

from .props import Collectable, Interactable
from .item import ItemID


class Ore(Interactable, Collectable, Sprite):
    _SOUND_COLLECT = pygame.mixer.Sound("assets/sounds/collect/ore.wav")
    color = colex.DARK_GRAY
    z_index = 1
    texture = ["<Unset Ore Texture>"]


class Gold(Ore):
    ID = ItemID.GOLD_ORE
    color = colex.GOLDENROD
    texture = ["▓▒▓"]


class Titanium(Ore):
    ID = ItemID.TITANIUM_ORE
    color = colex.from_hex("#797982")
    texture = ["▒░▒"]


class Copper(Ore):
    ID = ItemID.COPPER_ORE
    color = colex.from_hex("#B87333")
    texture = ["▒▓▒"]


class Coal(Ore):
    ID = ItemID.COAL_ORE
    color = colex.BLACK
    texture = ["▒▓▒"]
