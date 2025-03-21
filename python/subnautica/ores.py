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
    _ITEM = ItemID.GOLD_ORE
    color = colex.GOLDENROD
    texture = ["▓▒▓"]


class Titanium(Ore):
    _ITEM = ItemID.TITANIUM_ORE
    color = colex.from_hex("#797982")
    texture = ["▒░▒"]


class Copper(Ore):
    _ITEM = ItemID.COPPER_ORE
    color = colex.from_hex("#B87333")
    texture = ["▒▓▒"]


class Coal(Ore):
    _SOUND_COLLECT = pygame.mixer.Sound("assets/sounds/collect/coal.wav")
    _ITEM = ItemID.COAL_ORE
    color = colex.BLACK
    texture = ["▒▓▒"]
