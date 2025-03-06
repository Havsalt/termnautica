import colex
import keyboard
from charz import Sprite, Vec2

from . import env, ui
from .interactable import Interactable


class Player(Sprite):
    color = colex.AQUA
    transparency = " "
    texture = [
        "  O",
        "/ | \\",
        " / \\",
    ]
    _curr_interactable: Sprite | None = None

    def __init__(self) -> None:
        self._inventory = ui.Inventory({"gold": 5, "stone": 7}).with_parent(self)

    # self._interaction_label = Label(
    #     text="[ E ]",
    #     color=colex.WHITE,
    #     z_index=3,
    #     visible=False,
    #     centered=True,
    #     position=Vec2(4, -1),
    # )

    def update(self, _delta: float) -> None:
        self.handle_movement()
        self.handle_interact()

    def handle_movement(self) -> None:
        if keyboard.is_pressed("a"):
            self.position.x -= 1
        if keyboard.is_pressed("d"):
            self.position.x += 1
        if keyboard.is_pressed("w"):
            self.position.y -= 1
        if keyboard.is_pressed("s"):
            self.position.y += 1

    def handle_interact(self) -> None:
        proximite_interactables: list[tuple[float, Interactable]] = []
        center = self.global_position + Vec2(2, 1)

        for node in Sprite.texture_instances.values():
            if isinstance(node, Interactable):
                dist = center.distance_to(node.global_position)
                if dist < 8:
                    proximite_interactables.append((dist, node))

        if proximite_interactables:
            proximite_interactables.sort(key=lambda pair: pair[0])
            # Allow this because `Interactable` should always be used with `Sprite`
            if self._curr_interactable is not None:  # Reset color
                self._curr_interactable.color = self._curr_interactable.__class__.color
            # Reverse color of current interactable
            first = proximite_interactables[0][1]
            assert isinstance(first, Sprite)
            self._curr_interactable = first
            assert self._curr_interactable.__class__.color is not None
            self._curr_interactable.color = (
                colex.REVERSE + self._curr_interactable.__class__.color
            )
        elif self._curr_interactable is not None:
            self._curr_interactable.color = self._curr_interactable.__class__.color
            self._curr_interactable = None

        if self._curr_interactable is not None:
            if keyboard.is_pressed("e"):
                assert isinstance(self._curr_interactable, Interactable)
                assert (
                    self._curr_interactable.name is not None
                ), f"{self._curr_interactable}.name is `None`"
                item = self._curr_interactable.name
                self._inventory[item] += 1
                self._curr_interactable.queue_free()
                self._curr_interactable = None

        # proximite_interactables: list[tuple[float, env.Ore | env.Kelp]] = []
        # center = self.global_position + Vec2(2, -3)
        # for node in Sprite.texture_instances.values():
        #     if isinstance(node, (env.Ore, env.Kelp)):
        #         dist = center.distance_to(node.global_position)
        #         if dist < 8:
        #             proximite_interactables.append((dist, node))

        # if proximite_interactables:
        #     proximite_interactables.sort(key=lambda pair: pair[0])
        #     first_ore = proximite_interactables[0][1]
        #     # self._interaction_label.parent = first_ore
        #     assert first_ore.__class__.color is not None
        #     first_ore.color = colex.REVERSE + first_ore.__class__.color
        #     # self._interaction_label.show()
        # else:
        #     # self._interaction_label.parent = None  # Don't keep potential ref alive
        #     # self._interaction_label.hide()
        #     ...
        # if keyboard.is_pressed("e"):
        #     # self._interaction_label.color = colex.REVERSE + colex.WHITE
        #     if proximite_interactables:
        #         first_ore = proximite_interactables[0][1]
        #         first_ore.queue_free()
        # else:
        #     # self._interaction_label.color = colex.WHITE
        #     ...
