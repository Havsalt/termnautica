import colex
import keyboard
import pygame
from charz import Camera, Sprite, Label, Collider, Hitbox, Vec2

from . import ui, ocean
from .props import Collectable, Interactable, Building
from .tags import Eatable, Drinkable, Healing
from .particles import Bubble, Blood
from .item import ItemID
from .utils import move_toward


type Action = str | int


class Player(Collider, Sprite):
    _GRAVITY: float = 0.91
    _JUMP_STRENGTH: float = 4
    _AIR_FRICTION: float = 0.7
    _WATER_FRICTION: float = 0.3
    _MAX_SPEED: Vec2 = Vec2(2, 2)
    _HURT_SOUND = pygame.mixer.Sound("assets/sounds/hurt.wav")
    _HURT_CHANNEL = pygame.mixer.Channel(0)
    _DROWN_SOUND = pygame.mixer.Sound("assets/sounds/bubble.wav")
    _BREATH_SOUND = pygame.mixer.Sound("assets/sounds/breath.wav")
    # DEV
    # _DROWN_SOUND.set_volume(0)
    _ACTIONS: tuple[Action, ...] = (  # Order is also precedence - First is highest
        "e",
        "1",
        "2",
        "3",
        "space",
    )
    position = Vec2(17, -18)
    hitbox = Hitbox(size=Vec2(5, 3), centered=True)
    z_index = 1
    color = colex.AQUA
    transparency = " "
    centered = True
    texture = [
        "  O",
        "/ | \\",
        " / \\",
    ]
    _y_speed: float = 0
    _current_action: Action | None = None
    _key_just_pressed: bool = False
    _current_interactable: Sprite | None = None

    def __init__(self) -> None:
        # NOTE: Current `Camera` has to be initialized before `Player.__init__` is called
        self.inventory = ui.Inventory(
            {
                ItemID.WATER_BOTTLE: (2, [Drinkable(20)]),
            }
        ).with_parent(Camera.current)
        self._health_bar = ui.HealthBar().with_parent(Camera.current)
        self._oxygen_bar = ui.OxygenBar().with_parent(Camera.current)
        self._hunger_bar = ui.HungerBar().with_parent(Camera.current)
        self._thirst_bar = ui.ThirstBar().with_parent(Camera.current)
        self._hotbar1 = Label(
            self,
            text="Interact [E".rjust(11),
            transparency=" ",
            color=colex.SALMON,
            position=Vec2(40, -5),
        )
        self._hotbar2 = Label(
            self,
            text="Eat [1".rjust(11),
            transparency=" ",
            color=colex.SANDY_BROWN,
            position=Vec2(40, -3),
        )
        self._hotbar3 = Label(
            self,
            text="Drink [2".rjust(11),
            transparency=" ",
            color=colex.AQUA,
            position=Vec2(40, -2),
        )
        self._hotbar3 = Label(
            self,
            text="Heal [3".rjust(11),
            transparency=" ",
            color=colex.PINK,
            position=Vec2(40, -1),
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
        # NOTE: Order of drinking, eating and healing is not visually correct
        self.handle_drinking()
        self.handle_eating()
        self.handle_healing()
        # Check if dead
        if self._health_bar.value == 0:
            self.on_death()

    def handle_eating(self) -> None:
        if not (self._current_action == "1" and self._key_just_pressed):
            return

        found_eatable = False
        for item in self.inventory.values():
            if item.count < 1:
                continue

            for tag in item.tags:
                if not isinstance(tag, Eatable):
                    continue
                # Is `Eatable`
                item.count -= 1
                self._hunger_bar.value += tag.hunger_value
                # Check if also `Drinkable`
                for tag2 in item.tags:
                    if isinstance(tag2, Drinkable):
                        self._thirst_bar.value += tag2.thirst_value
                found_eatable = True
                break
            if found_eatable:
                break

    # TODO: Check for drinking, eating and healing at the same time
    def handle_drinking(self) -> None:
        if not (self._current_action == "2" and self._key_just_pressed):
            return

        found_drinkable = False
        for item in self.inventory.values():
            if item.count < 1:
                continue

            for tag in item.tags:
                if not isinstance(tag, Drinkable):
                    continue
                # Is `Drinkable`
                item.count -= 1
                self._thirst_bar.value += tag.thirst_value
                # Check if also `Eatable`
                for tag2 in item.tags:
                    if isinstance(tag2, Eatable):
                        self._hunger_bar.value += tag2.hunger_value
                found_drinkable = True
                break
            if found_drinkable:
                break
    
    def handle_healing(self) -> None:
        if not (self._current_action == "3" and self._key_just_pressed):
            return
        
        found_healing = False
        for item in self.inventory.values():
            if item.count < 1:
                continue

            for tag in item.tags:
                if not isinstance(tag, Healing):
                    continue
                # Is `Healing`
                item.count -= 1
                self._health_bar.value += tag.heal_value
                found_healing = True
                break
            if found_healing:
                break


    def is_submerged(self) -> bool:
        self_height = self.global_position.y - self.texture_size.y / 2
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def is_in_ocean(self):
        self_height = self.global_position.y + self.texture_size.y / 2 - 1
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def is_in_building(self) -> bool:
        return isinstance(self.parent, Building)

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

    def handle_movement_in_building(self, velocity: Vec2) -> None:
        assert isinstance(self.parent, Building)
        # TODO: Check if is on floor first
        if self._current_action == "space" and self._key_just_pressed:
            self._y_speed = -self._JUMP_STRENGTH
        combined_velocity = Vec2(velocity.x, self._y_speed).clamped(
            -self._MAX_SPEED,
            self._MAX_SPEED,
        )
        self.parent.move_and_collide_inside(self, combined_velocity)
        # Apply friction
        self._y_speed = move_toward(self._y_speed, 0, self._AIR_FRICTION)

    def handle_movement(self) -> None:
        velocity = Vec2(
            keyboard.is_pressed("d") - keyboard.is_pressed("a"),
            keyboard.is_pressed("s") - keyboard.is_pressed("w"),
        )
        # Is in builindg movement
        if self.is_in_building():
            self.handle_movement_in_building(velocity)
            return
        # Is in air movement
        elif not self.is_in_ocean():
            self._y_speed += self._GRAVITY
        # Is in ocean movement
        combined_velocity = Vec2(velocity.x, velocity.y + self._y_speed).clamped(
            -self._MAX_SPEED,
            self._MAX_SPEED,
        )
        # NOTE: Order of x/y matter
        self.position.y += combined_velocity.y
        # Revert motion if ended up colliding
        if self.is_colliding_with_ocean_floor() or self.is_colliding():
            self.position.y -= combined_velocity.y
            self._y_speed = 0  # Hit ocean floor
        self.position.x += combined_velocity.x
        # Revert motion if ended up colliding
        if self.is_colliding_with_ocean_floor() or self.is_colliding():
            self.position.x -= combined_velocity.x
        # Apply friction
        friction = self._WATER_FRICTION if self.is_submerged() else self._AIR_FRICTION
        self._y_speed = move_toward(self._y_speed, 0, friction)

    def handle_oxygen(self) -> None:
        # Restore oxygen if inside a building with O2
        if (  # Is in building with oxygen
            isinstance(self.parent, Building) and self.parent.HAS_OXYGEN
        ):
            self._oxygen_bar.fill()
            return
        # Restore oxygen if above ocean waves
        if not self.is_submerged():
            if self._oxygen_bar.value != self._oxygen_bar.MAX_VALUE:
                self._BREATH_SOUND.play()
                self._oxygen_bar.fill()
            return
        # Decrease health if no oxygen, and spawn particles each tick
        if self._oxygen_bar.value == 0:
            self._health_bar.value -= 1
            if not self._HURT_CHANNEL.get_busy():
                self._HURT_CHANNEL.play(self._HURT_SOUND)
            Blood().with_global_position(
                x=self.global_position.x - 1,
                y=self.global_position.y - 1,
            )
            return
        # Decrease oxygen
        self._oxygen_bar.value -= 1 / 16
        raw_count = self._oxygen_bar.MAX_VALUE / self._oxygen_bar.MAX_CELL_COUNT
        # NOTE: Might be fragile logic, but works at least when
        #       MAX_VALUE = 300 and MAX_CELL_COUNT = 10
        if self._oxygen_bar.value % raw_count == 0:
            Bubble().with_global_position(
                x=self.global_position.x,
                y=self.global_position.y - 1,
            )
            self._DROWN_SOUND.play()

    def handle_hunger(self) -> None:
        self._hunger_bar.value -= 1 / 16
        if self._hunger_bar.value == 0:
            self._health_bar.value -= 1
            Blood().with_global_position(
                x=self.global_position.x - 1,
                y=self.global_position.y - 1,
            )

    def handle_thirst(self) -> None:
        self._thirst_bar.value -= 1 / 16
        if self._thirst_bar.value == 0:
            self._health_bar.value -= 1
            Blood().with_global_position(
                x=self.global_position.x - 1,
                y=self.global_position.y - 1,
            )

    def handle_interact_selection(self) -> None:
        proximite_interactables: list[tuple[float, Interactable]] = []
        global_point = self.global_position  # Store property value outside loop
        for node in Sprite.texture_instances.values():
            if (
                isinstance(node, Interactable)
                and node.interactable
                and (condition_and_dist := node.is_in_range_of(global_point))[0]
            ):  # I know this syntax might be a bit too much,
                # but know that it made it easier to split logic into mixin class
                proximite_interactables.append((condition_and_dist[1], node))

        # Highlight closest interactable
        if proximite_interactables:
            proximite_interactables.sort(key=lambda pair: pair[0])
            # Allow this because `Interactable` should always be used with `Sprite`
            if isinstance(
                self._current_interactable, Interactable
            ):  # Reset color to class color
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
            self._current_interactable.collect_into(self.inventory.inner)
            self._current_interactable.queue_free()
            self._current_interactable = None

    # TODO: Implement
    def on_death(self) -> None:
        self.queue_free()
        if isinstance(self._current_interactable, Interactable):
            self._current_interactable.loose_focus()
        # Reset states
        self._current_interactable = None
        self._current_action = None
        self._key_just_pressed = False
