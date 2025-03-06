import colex
from charz import Sprite, Vec2, text


class Inventory(Sprite):
    z_index = 5
    position = Vec2(-40, -4)
    # color = colex.from_hex(background="#24ac2d")
    color = colex.BOLD + colex.WHITE

    def __init__(self, content: dict[str, int]) -> None:
        self._inner = content
        self._update_texture()

    def __getitem__(self, key: str) -> int:
        if key not in self._inner:
            return 0
        return self._inner[key]

    def __setitem__(self, key: str, value: int) -> None:
        self._inner[key] = value
        self._update_texture()

    def _update_texture(self) -> None:
        self.texture = text.fill_lines(
            [
                f"- {item.capitalize().replace("_", " ")}: {count}"
                for item, count in self._inner.items()
            ]
        )
        self.texture.insert(0, "Inventory:")

    # def update(self, _delta: float) -> None:
    #     self.parent = Camera.current
    #     self.global_position = Camera.current.global_position
