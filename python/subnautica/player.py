import colex
import keyboard
import pygame
from charz import Camera, Sprite, Label, Vec2

from . import ui, ocean
from .props import Collectable, Interactable, Eatable, Building
from .particles import Bubble, Blood

pygame.mixer.init()


type Action = str | int


class Player(Sprite):
    _ACTIONS: tuple[Action, ...] = (  # Order is also precedence - First is highest
        "e",
        "1",
        "2",
    )
    position = Vec2(17, -8)
    z_index = 1
    color = colex.AQUA
    transparency = " "
    centered = True
    texture = [
        "  O",
        "/ | \\",
        " / \\",
    ]
    _current_action: Action | None = None
    _key_just_pressed: bool = False
    _current_interactable: Sprite | None = None
    _drown_sound = pygame.mixer.Sound("python/sounds/bubble.wav")
    # DEV
    # _drown_sound.set_volume(0)

    def __init__(self) -> None:
        # NOTE: Current `Camera` has to be initialized before `Player.__init__` is called
        self._inventory = ui.Inventory({}).with_parent(Camera.current)
        self._health_bar = ui.HealthBar().with_parent(Camera.current)
        self._oxygen_bar = ui.OxygenBar().with_parent(Camera.current)
        self._hunger_bar = ui.HungerBar().with_parent(Camera.current)
        self._thirst_bar = ui.ThirstBar().with_parent(Camera.current)
        self._hotbar1 = Label(
            self,
            text="Interact [E",
            color=colex.SALMON,
            position=Vec2(40, -5),
        )
        self._hotbar2 = Label(
            self,
            text="     Eat [1",
            color=colex.SANDY_BROWN,
            position=Vec2(40, -3),
        )
        self._hotbar3 = Label(
            self,
            text="   Drink [2",
            color=colex.AQUA,
            position=Vec2(40, -2),
        )

    def update(self, _delta: float) -> None:
        # Order of tasks
        self.handle_action_input()
        self.handle_movement()
        self.handle_interact_selection()
        self.handle_interact()
        self.handle_collect()
        self.handle_oxygen()
        self.handle_hunger()
        self.handle_thirst()
        self.dev_drinking()
        self.dev_eating()
        # Check if dead
        if self._health_bar.value == 0:
            self.on_death()

    # DEV
    def dev_eating(self) -> None:
        if self._current_action == "1" and self._key_just_pressed:
            for item_name, item in tuple(self._inventory.items()):
                if item.count > 0 and Eatable in item.tags:
                    self._inventory[item_name].count -= 1
                    self._hunger_bar.fill()
                    break

    # DEV
    def dev_drinking(self) -> None:
        if self._current_action == "2" and self._key_just_pressed:
            if (
                "bladder fish" in self._inventory
                and self._inventory["bladder fish"].count >= 1
                and "kelp" in self._inventory
                and self._inventory["kelp"].count >= 2
            ):
                self._inventory["bladder fish"].count -= 1
                self._inventory["kelp"].count -= 2
                self._thirst_bar.fill()

    def is_submerged(self) -> bool:
        self_height = self.global_position.y - self.texture_size.y / 2
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def is_in_ocean(self):
        self_height = self.global_position.y + self.texture_size.y / 2 - 1
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def is_colliding_with_ocean_floor(self) -> bool:
        # FIXME: Find out why it says `int | float` and not just `int` for `<Vec2i>.x`
        center = self.global_position
        if self.centered:
            center -= self.texture_size / 2
        for x_offset in range(int(self.texture_size.x)):
            for y_offset in range(int(self.texture_size.y)):
                global_point = (
                    int(center.x + x_offset),
                    int(center.y + y_offset),
                )
                if global_point in ocean.Floor.points:
                    return True
        return False

    def handle_action_input(self) -> None:
        if self._current_action is None:
            # Check for pressed
            for action in self._ACTIONS:
                if keyboard.is_pressed(action):
                    self._current_action = action
                    self._key_just_pressed = True
                    break
        elif self._key_just_pressed:
            # Deactivate "bool signal" after 1 single frame
            self._key_just_pressed = False
        elif not keyboard.is_pressed(self._current_action):
            # Release
            self._current_action = None

    def handle_movement(self) -> None:
        # TODO: Add acceleration and speed for at least Y-axis
        # Fall down while in air, except for when in building
        if self.parent is None and not self.is_in_ocean():
            self.position.y += 1
            return
        # Keyboard input
        velocity = Vec2(
            keyboard.is_pressed("d") - keyboard.is_pressed("a"),
            keyboard.is_pressed("s") - keyboard.is_pressed("w"),
        )
        # NOTE: Order of x/y matter
        self.position.y += velocity.y
        # Revert motion if ended up colliding
        if self.is_colliding_with_ocean_floor():
            self.position.y -= velocity.y
        self.position.x += velocity.x
        # Revert motion if ended up colliding
        if self.is_colliding_with_ocean_floor():
            self.position.x -= velocity.x

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
        # Decrease health if no oxygen, and spawn particles each tick
        if self._oxygen_bar.value == 0:
            self._health_bar.value = self._health_bar.value - 1
            Blood().with_global_position(
                x=self.global_position.x - 1,
                y=self.global_position.y - 1,
            )
            return
        # Decrease oxygen
        self._oxygen_bar.value = self._oxygen_bar.value - 1
        raw_count = self._oxygen_bar.MAX_VALUE / self._oxygen_bar.MAX_CELL_COUNT
        # NOTE: Might be fragile logic, but works at least when
        #       MAX_VALUE = 300 and MAX_CELL_COUNT = 10
        if self._oxygen_bar.value % raw_count == 0:
            Bubble().with_global_position(
                x=self.global_position.x,
                y=self.global_position.y - 1,
            )
            self._drown_sound.play()

    def handle_hunger(self) -> None:
        self._hunger_bar.value = self._hunger_bar.value - 1
        if self._hunger_bar.value == 0:
            self._health_bar.value = self._health_bar.value - 1
            Blood().with_global_position(
                x=self.global_position.x - 1,
                y=self.global_position.y - 1,
            )

    def handle_thirst(self) -> None:
        self._thirst_bar.value = self._thirst_bar.value - 1
        if self._thirst_bar.value == 0:
            self._health_bar.value = self._health_bar.value - 1
            Blood().with_global_position(
                x=self.global_position.x - 1,
                y=self.global_position.y - 1,
            )

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
            if self._current_interactable is not None:  # Reset color to class color
                assert isinstance(self._current_interactable, Interactable)
                self._current_interactable.loose_focus()
            # Reverse color of current interactable
            first = proximite_interactables[0][1]
            assert isinstance(
                first, Sprite
            ), f"{first.__class__} is missing `Sprite` base"
            self._current_interactable = first
            self._current_interactable.grab_focus()
        # Or unselect last interactable that *was* in reach
        elif self._current_interactable is not None:
            assert isinstance(self._current_interactable, Interactable)
            self._current_interactable.loose_focus()
            self._current_interactable = None

    def handle_interact(self) -> None:
        if self._current_interactable is None:
            return
        assert isinstance(self._current_interactable, Interactable)
        # Trigger interaction function
        if self._current_action == "e" and self._key_just_pressed:
            # TODO: Check for z_index change, so that it respects z_index change in on_interact
            self._current_interactable.on_interact(self)

    def handle_collect(self) -> None:
        if self._current_interactable is None:
            return
        if not isinstance(self._current_interactable, Collectable):
            return
        # Collect collectable that is selected
        # `self._curr_interactable` is already in reach
        if self._current_action == "e" and self._key_just_pressed:
            assert (
                self._current_interactable.name is not None
            ), f"{self._current_interactable}.name is `None`"
            item_name = self._current_interactable.name
            if item_name in self._inventory:
                self._inventory[item_name].count += 1
            else:  # Insert new item with count of 1
                self._inventory[item_name] = ui.Item(
                    item_name,
                    1,
                    self._current_interactable.get_tags(),
                )
            self._current_interactable.queue_free()
            self._current_interactable = None

    # TODO: Implement
    def on_death(self) -> None:
        self.queue_free()
