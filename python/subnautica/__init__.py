import random

import keyboard
from charz import Engine, Camera, Screen, AssetLoader, Vec2

AssetLoader.animation_root = "python/animations"
AssetLoader.texture_root = "python/sprites"
random.seed(3)

from rust import RustScreen
from .ocean import Ocean, OceanWater
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
# TODO: CRAFTING - WATER 0/4


class App(Engine):
    fps = 16
    screen = RustScreen(auto_resize=True)
    clear_console = True

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
        self.lifepod = Lifepod()
        self.ocean = Ocean()
        middle_ocean_water = OceanWater().save_rest_location()
        self.lifepod.parent = middle_ocean_water
        # DEV
        # from .fish import WaterFish
        # from .spawners import Coral

        # for i in range(0, 5):
        #     f = WaterFish(position=Vec2(20, -10))
        #     f.position.x += i * 10
        #     f.position.y += random.randint(-2, 2)
        #     f.speed_y = -20
        # Coral().with_global_position(x=20, y=-10)

    def update(self, _delta: float) -> None:
        OceanWater.advance_wave_time()


def main() -> int:
    app = App()
    app.run()
    return 0
