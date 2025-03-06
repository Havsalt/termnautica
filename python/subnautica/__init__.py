import keyboard
from charz import Engine, Camera, Screen, Animation, Vec2

Animation.folder_path = "python/animations"

from rust import RustScreen
from .ocean import Ocean
from .player import Player


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


class App(Engine):
    fps = 16
    screen = RustScreen(auto_resize=True)
    clear_console = True

    def __init__(self) -> None:
        self.player = Player().with_position(Vec2(0, 5))
        DevCamera(self.player).with_mode(
            Camera.MODE_CENTERED | Camera.MODE_INCLUDE_SIZE
        ).as_current()
        # Camera.current.parent = self.player
        # Camera.current.mode = Camera.MODE_CENTERED
        self.ocean = Ocean()

    # def update(self, delta: float) -> None:
    #     print(delta)


def main() -> int:
    app = App()
    app.run()
    return 0
