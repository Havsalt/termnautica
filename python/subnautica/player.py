import colex
import keyboard
from charz import Camera, Sprite, Vec2

from . import ui
from .props import Collectable, Eatable
from .ui import Item


# TODO: Implement HP
class Player(Sprite):
    _REACH: float = 8
    position = Vec2(0, 5)
    color = colex.AQUA
    transparency = " "
    texture = [
        "  O",
        "/ | \\",
        " / \\",
    ]
    _curr_collectable: Sprite | None = None

    def __init__(self) -> None:
        # NOTE: Current `Camera` has to be initialized before `Player.__init__` is called
        self._inventory = ui.Inventory({"gold": 5, "stone": 7}).with_parent(
            Camera.current
        )
        self._health_bar = ui.HealthBar(Camera.current).init()
        self._oxygen_bar = ui.OxygenBar(Camera.current).init()
        self._hunger_bar = ui.HungerBar(Camera.current).init()
        self._thirst_bar = ui.ThirstBar(Camera.current).init()

    def update(self, _delta: float) -> None:
        self.handle_movement()
        self.handle_collect()
        self.handle_oxygen()
        self.handle_hunger()
        self.handle_thirst()
        self.dev_crafting()
        self.dev_eating()
        # Check if dead
        if self._health_bar.value == 0:
            self.on_death()

    # DEV
    def dev_crafting(self) -> None:
        if keyboard.is_pressed("f"):
            if (
                "bladder fish" in self._inventory
                and self._inventory["bladder fish"].count >= 1
                and "kelp" in self._inventory
                and self._inventory["kelp"].count >= 2
            ):
                self._inventory["bladder fish"].count -= 1
                self._inventory["kelp"].count -= 2
                self._oxygen_bar.value = self._oxygen_bar.MAX_VALUE

    def dev_eating(self) -> None:
        if keyboard.is_pressed("q"):
            for item_name, item in tuple(self._inventory.items()):
                if item.count > 0 and Eatable in item.tags:
                    self._inventory[item_name].count -= 1
                    self._hunger_bar.value = self._hunger_bar.MAX_VALUE
                    break

    # TODO: Improve water detection, like considering waves
    def is_submerged(self) -> bool:
        return self.global_position.y > 0

    def handle_movement(self) -> None:
        if keyboard.is_pressed("a"):
            self.position.x -= 1
        if keyboard.is_pressed("d"):
            self.position.x += 1
        if keyboard.is_pressed("w"):
            self.position.y -= 1
        if keyboard.is_pressed("s"):
            self.position.y += 1

    def handle_oxygen(self) -> None:
        # Restore oxygen if above ocean waves
        if not self.is_submerged():
            self._oxygen_bar.value = self._oxygen_bar.MAX_VALUE
            return
        # Decrease oxygen
        if self._oxygen_bar.value > 0:
            self._oxygen_bar.value = max(0, self._oxygen_bar.value - 1)
        else:  # Or decrease health if not oxygen...
            self._health_bar.value = max(0, self._health_bar.value - 1)

    def handle_hunger(self) -> None:
        self._hunger_bar.value = max(0, self._hunger_bar.value - 1)
        if self._hunger_bar.value == 0:
            self._health_bar.value = max(0, self._health_bar.value - 1)

    def handle_thirst(self) -> None:
        self._thirst_bar.value = max(0, self._thirst_bar.value - 1)
        if self._thirst_bar.value == 0:
            self._health_bar.value = max(0, self._health_bar.value - 1)

    def handle_collect(self) -> None:
        proximite_collectables: list[tuple[float, Collectable]] = []
        center = self.global_position + Vec2(2, 1)

        for node in Sprite.texture_instances.values():
            if isinstance(node, Collectable):
                dist = center.distance_to(node.global_position)
                if dist < self._REACH:
                    proximite_collectables.append((dist, node))

        # Highlight closest collectable
        if proximite_collectables:
            proximite_collectables.sort(key=lambda pair: pair[0])
            # Allow this because `Collectable` should always be used with `Sprite`
            if self._curr_collectable is not None:  # Reset color to class color
                self._curr_collectable.color = self._curr_collectable.__class__.color
            # Reverse color of current interactable
            first = proximite_collectables[0][1]
            assert isinstance(first, Sprite)
            self._curr_collectable = first
            assert (
                self._curr_collectable.__class__.color is not None
            ), f"{self._curr_collectable.__class__.__qualname__}.color is `None`"
            self._curr_collectable.color = (
                colex.REVERSE + self._curr_collectable.__class__.color
            )
        # Or unselect last collectable that *was* in reach
        elif self._curr_collectable is not None:
            self._curr_collectable.color = self._curr_collectable.__class__.color
            self._curr_collectable = None

        # Collect collectable that is in reach and selected
        if self._curr_collectable is not None:
            if keyboard.is_pressed("e"):
                assert isinstance(self._curr_collectable, Collectable)
                assert (
                    self._curr_collectable.name is not None
                ), f"{self._curr_collectable}.name is `None`"
                item_name = self._curr_collectable.name
                if not item_name in self._inventory:
                    self._inventory[item_name] = Item(
                        item_name,
                        0,  # Will be incremented to `1` in the next statement
                        self._curr_collectable.get_tags(),
                    )
                self._inventory[item_name].count += 1
                self._curr_collectable.queue_free()
                self._curr_collectable = None

    # TODO: Implement
    def on_death(self) -> None:
        self.queue_free()
