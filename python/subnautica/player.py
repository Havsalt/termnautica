import colex
import keyboard
from charz import Camera, Sprite, Vec2

from . import ui
from .props import Collectable, Interactable, Eatable, Building
from .ocean import OceanWater


# TODO: Implement HP
class Player(Sprite):
    position = Vec2(0, 5)
    z_index = 1
    color = colex.AQUA
    transparency = " "
    centered = True
    texture = [
        "  O",
        "/ | \\",
        " / \\",
    ]
    _curr_interactable: Sprite | None = None

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
        # Order of tasks
        self.handle_movement()
        self.handle_interact_selection()
        self.handle_interact()
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
                self._oxygen_bar.fill()

    def dev_eating(self) -> None:
        if keyboard.is_pressed("q"):
            for item_name, item in tuple(self._inventory.items()):
                if item.count > 0 and Eatable in item.tags:
                    self._inventory[item_name].count -= 1
                    self._hunger_bar.fill()
                    break

    def is_submerged(self) -> bool:
        self_height = self.global_position.y - self.texture_size.y / 2
        wave_height = OceanWater.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def is_in_ocean(self):
        self_height = self.global_position.y + self.texture_size.y / 2 - 1
        wave_height = OceanWater.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def handle_movement(self) -> None:
        # TODO: Add acceleration and speed for at least Y-axis
        # Fall down while in air, except for when in building
        if (
            not self.is_in_ocean()
            and self.parent is None
            and isinstance(self.parent, Building)
        ):
            self.position.y += 1
            return
        # Keyboard input
        velocity = Vec2(
            keyboard.is_pressed("d") - keyboard.is_pressed("a"),
            keyboard.is_pressed("s") - keyboard.is_pressed("w"),
        )
        self.position += velocity

    def handle_oxygen(self) -> None:
        # Restore oxygen if inside a building with O2
        if (
            self.parent is not None
            and isinstance(self.parent, Building)
            and self.parent.has_oxygen
        ):
            self._oxygen_bar.fill()
            return
        # Restore oxygen if above ocean waves
        if not self.is_submerged():
            self._oxygen_bar.fill()
            return
        # Decrease health if no oxygen
        if self._oxygen_bar.value == 0:
            self._health_bar.value = self._health_bar.value - 1
            return
        # Decrease oxygen
        self._oxygen_bar.value = self._oxygen_bar.value - 1

    def handle_hunger(self) -> None:
        self._hunger_bar.value = max(0, self._hunger_bar.value - 1)
        if self._hunger_bar.value == 0:
            self._health_bar.value = max(0, self._health_bar.value - 1)

    def handle_thirst(self) -> None:
        self._thirst_bar.value = max(0, self._thirst_bar.value - 1)
        if self._thirst_bar.value == 0:
            self._health_bar.value = max(0, self._health_bar.value - 1)

    def handle_interact_selection(self) -> None:
        proximite_interactables: list[tuple[float, Interactable]] = []
        self_global_position = self.global_position

        for node in Sprite.texture_instances.values():
            if isinstance(node, Interactable) and node.interactable:
                diff = node.global_position - self_global_position
                diff.y /= node.reach_fraction  # Apply linear transformation on Y-axis
                # NOTE: Using squared lengths for a bit more performance
                dist = diff.length_squared()
                if dist < node.reach * node.reach:
                    proximite_interactables.append((dist, node))

        # Highlight closest interactable
        if proximite_interactables:
            proximite_interactables.sort(key=lambda pair: pair[0])
            # Allow this because `Interactable` should always be used with `Sprite`
            if self._curr_interactable is not None:  # Reset color to class color
                assert isinstance(self._curr_interactable, Interactable)
                self._curr_interactable.loose_focus()
            # Reverse color of current interactable
            first = proximite_interactables[0][1]
            assert isinstance(
                first, Sprite
            ), f"{first.__class__} is missing `Sprite` base"
            self._curr_interactable = first
            self._curr_interactable.grab_focus()
        # Or unselect last interactable that *was* in reach
        elif self._curr_interactable is not None:
            assert isinstance(self._curr_interactable, Interactable)
            self._curr_interactable.loose_focus()
            self._curr_interactable = None

    def handle_interact(self) -> None:
        if self._curr_interactable is None:
            return
        assert isinstance(self._curr_interactable, Interactable)
        # Trigger interaction function
        if keyboard.is_pressed("e"):
            # TODO: Check for z_index change, so that it respects z_index change in on_interact
            self._curr_interactable.on_interact(self)

    def handle_collect(self) -> None:
        if self._curr_interactable is None:
            return
        if not isinstance(self._curr_interactable, Collectable):
            return
        # Collect collectable that is selected
        # `self._curr_interactable` is already in reach
        if keyboard.is_pressed("e"):
            assert (
                self._curr_interactable.name is not None
            ), f"{self._curr_interactable}.name is `None`"
            item_name = self._curr_interactable.name
            if item_name in self._inventory:
                self._inventory[item_name].count += 1
            else:  # Insert new item with count of 1
                self._inventory[item_name] = ui.Item(
                    item_name,
                    1,
                    self._curr_interactable.get_tags(),
                )
            self._curr_interactable.queue_free()
            self._curr_interactable = None

    # TODO: Implement
    def on_death(self) -> None:
        self.queue_free()
