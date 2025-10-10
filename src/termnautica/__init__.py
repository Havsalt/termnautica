import os
import random
from pathlib import Path

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import keyboard
from charz import Engine, Camera, AssetLoader, Vec2
from charz_rust import RustScreen

from . import settings

AssetLoader.animation_root = settings.ANIMATION_FOLDER
AssetLoader.texture_root = settings.SPRITES_FOLDER
random.seed(3)  # DEV

pygame.mixer.init()

from . import ocean
from .player import Player
from .buildings.lifepod import Lifepod


# NOTE: Game time is calculated in frames (int),
#       because delta time is unstable at the moment


class DevCamera(Camera):
    def update(self) -> None:
        if keyboard.is_pressed("a"):
            self.position.x -= 1
        if keyboard.is_pressed("d"):
            self.position.x += 1
        if keyboard.is_pressed("w"):
            self.position.y -= 1
        if keyboard.is_pressed("s"):
            self.position.y += 1


# TODO: LIFEPOD 2/3: Respawn
# TODO: INVENTORY SIZE: 0/1
# TODO: PREVENT HEALING ON CRUSHING DEPTHS
# TODO: Make `HealthCarrier` prop


class App(Engine):
    fps = settings.FPS
    screen = RustScreen(
        auto_resize=True,
        initial_clear=True,
        margin_right=0,
        margin_bottom=0,
    )

    def __init__(self) -> None:
        Camera.current = (
            Camera()
            .with_mode(Camera.MODE_CENTERED)
            .with_position(Vec2(-2, -2))
        )
        self.player = Player()
        # Attatch new camera to player, *after* player has been created
        Camera.current.parent = self.player
        # Attatch lifepod to waving water
        ocean.generate_floor()
        ocean.generate_water()
        # TODO: Update `Lifepod` position internally using ocean formula
        self.lifepod = Lifepod()
        middle_ocean_water = ocean.Water().save_rest_location()
        self.lifepod.parent = middle_ocean_water
        # Music
        pygame.mixer_music.load(settings.MUSIC_FOLDER / "main.mp3")
        pygame.mixer_music.set_volume(0.50)
        # # DEV
        # pygame.mixer_music.set_volume(0)
        pygame.mixer_music.play(-1)  # Infinite loop
        # pygame.mixer.set_num_channels(64)
        # DEV: Stuff stashed away in this method
        self.dev()

    def dev(self) -> None:
        from .fish import SwordFish, Nemo
        # from .birds import SmallBird, MediumBird, LargeBird

        SwordFish(position=Vec2(80, -18))
        Nemo(position=Vec2(-40, -20))

        # for i in range(-10, 10):
        #     if random.randint(1, 3) == 1:
        #         continue
        #     if random.randint(1, 8) == 1:
        #         LargeBird().with_global_position(
        #             x=random.randint(0, 5) + i * 15 - 50,
        #             y=random.randint(0, 10) - 20,
        #         )
        #         continue
        #     bird = random.choice([SmallBird, MediumBird])
        #     bird().with_global_position(
        #         x=random.randint(0, 5) + i * 15 - 50,
        #         y=random.randint(0, 10) - 20,
        #     )

        from .buildings.grill import Grill

        Grill(position=Vec2(10, 10))

        # from .fish import WaterFish
        # from .spawners import FishSpawner

        # for i in range(0, 5):
        #     f = WaterFish(position=Vec2(20, -10))
        #     f.position.x += i * 10
        #     f.position.y += random.randint(-2, 2)
        #     f.speed_y = -20
        # FishSpawner().with_global_position(x=20, y=-10)

    def update(self) -> None:
        ocean.Water.advance_wave_time()
        if keyboard.is_pressed("esc"):
            self.is_running = False
            pygame.quit()

        self.dev_update()  # DEV

    def dev_update(self) -> None:
        from .buildings.hallway import Hallway
        from .item import ItemID

        if keyboard.is_pressed("b"):
            if (
                ItemID.TITANIUM_BAR in self.player.inventory
                and self.player.inventory[ItemID.TITANIUM_BAR] >= 3
            ):
                self.player.inventory[ItemID.TITANIUM_BAR] -= 3
                Hallway().with_global_position(
                    self.player.global_position + Vec2.RIGHT * 5
                )


def main() -> int | None:
    app = App()
    app.run()
