import os
import random

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import keyboard
from charz import Engine, Camera, Screen, AssetLoader, Vec2

AssetLoader.animation_root = "assets/animations"
AssetLoader.texture_root = "assets/sprites"
random.seed(3)  # DEV

pygame.mixer.init()

from rust import RustScreen
from . import ocean
from .player import Player
from .buildings import Lifepod


# NOTE: Game time is calculated in frames (int),
#       because delta time is unstable at the moment


class DevCamera(Camera):
    def update(self, _delta: float) -> None:
        if keyboard.is_pressed("a"):
            self.position.x -= 1
        if keyboard.is_pressed("d"):
            self.position.x += 1
        if keyboard.is_pressed("w"):
            self.position.y -= 1
        if keyboard.is_pressed("s"):
            self.position.y += 1


# TODO: O2 1/2
# TODO: LIFEPOD 1/3
# TODO: CRAFTING - WATER 1/4
# TODO: Fix Sound not triggering the first time


class App(Engine):
    fps = 16
    screen = RustScreen(
        auto_resize=True,
        initial_clear=True,
    )

    def __init__(self) -> None:
        camera = (
            Camera()
            .with_mode(Camera.MODE_CENTERED | Camera.MODE_INCLUDE_SIZE)
            .as_current()
        )
        self.player = Player()
        # Attatch camera to player
        camera.parent = self.player
        # Attatch lifepod to waving water
        ocean.generate_floor()
        ocean.generate_water()
        self.lifepod = Lifepod()
        middle_ocean_water = ocean.Water().save_rest_location()
        self.lifepod.parent = middle_ocean_water
        # Music
        pygame.mixer_music.load("assets/music/main.mp3")
        pygame.mixer_music.set_volume(0.50)
        pygame.mixer_music.play(-1)  # Infinite loop
        # pygame.mixer.set_num_channels(64)
        # Dev stuff stashed away in this method
        self.dev()

    def dev(self) -> None:
        from .fish import SwordFish
        from .birds import SmallBird, MediumBird, LargeBird

        SwordFish(position=Vec2(20, -18))

        for i in range(-10, 10):
            if random.randint(1, 3) == 1:
                continue
            if random.randint(1, 8) == 1:
                LargeBird().with_global_position(
                    x=random.randint(0, 5) + i * 15 - 50,
                    y=random.randint(0, 10) - 20,
                )
                continue
            bird = random.choice([SmallBird, MediumBird])
            bird().with_global_position(
                x=random.randint(0, 5) + i * 15 - 50,
                y=random.randint(0, 10) - 20,
            )

        # from .fish import WaterFish
        # from .spawners import FishSpawner

        # for i in range(0, 5):
        #     f = WaterFish(position=Vec2(20, -10))
        #     f.position.x += i * 10
        #     f.position.y += random.randint(-2, 2)
        #     f.speed_y = -20
        # FishSpawner().with_global_position(x=20, y=-10)

    def update(self, _delta: float) -> None:
        ocean.Water.advance_wave_time()
        if keyboard.is_pressed("esc"):
            self.is_running = False
            self.screen.clear()
            pygame.quit()


def main() -> int | None:
    app = App()
    app.run()
