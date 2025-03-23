import random

import pygame
import colex
from colex import ColorValue
from charz import Sprite

from .props import Collectable, Interactable
from .item import ItemID
from .particles import ShineSpark


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


class Crystal(Ore):
    _SOUND_COLLECT = pygame.mixer.Sound("assets/sounds/collect/crystal.wav")
    _ITEM = ItemID.CRYSTAL
    _MIN_COLOR_CHANGE_INTERVAL: int = 10
    _MAX_COLOR_CHANGE_INTERVAL: int = 18
    _MIN_SHINE_INTERVAL: int = 5
    _MAX_SHINE_INTERVAL: int = 12
    _COLORS: list[ColorValue] = [
        colex.PURPLE,
        colex.ANTIQUE_WHITE,
        colex.PINK,
    ]
    color = colex.PURPLE
    texture = ["<*."]
    _color_change_cooldown: int = 0
    _shine_cooldown: int = 0

    def update(self, _delta: float) -> None:
        self._color_change_cooldown -= 1
        if self._color_change_cooldown <= 0:
            self._color_change_cooldown = random.randint(
                self._MIN_COLOR_CHANGE_INTERVAL,
                self._MAX_COLOR_CHANGE_INTERVAL,
            )
            self.color = random.choice(self._COLORS)

        self._shine_cooldown -= 1
        if self._shine_cooldown <= 0:
            self._shine_cooldown = random.randint(
                self._MIN_SHINE_INTERVAL,
                self._MAX_SHINE_INTERVAL,
            )
            spark = ShineSpark().with_global_position(self.global_position)
            spark.position.x += 1


class Diamond(Ore):
    _SOUND_COLLECT = pygame.mixer.Sound("assets/sounds/collect/diamond.wav")
    _ITEM = ItemID.DIAMOND
    color = colex.SKY_BLUE
    texture = ["▒▓▒"]
