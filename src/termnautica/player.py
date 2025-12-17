import random
from math import floor
from copy import deepcopy
from typing import assert_never

import colex
from charz import (
    Camera,
    Sprite,
    Scene,
    Group,
    ColliderComponent,
    Hitbox,
    Vec2,
)

from . import gear_types, projectiles, settings, ui, ocean
from .input_handler import InputHandler, Keyboard, Action
from .props import Collectable, Interactable, Building, Targetable
from .fabrication import Fabrication
from .particles import Bubble, Blood
from .item import ItemID, Slot, ConsumableStat, SizedInventory, gear, consumables
from .utils import move_toward


type ActionName = str
type Count = int


ARROW_UP: int = 72
ARROW_DOWN: int = 80


class PlayerDeathDrop(Interactable, Sprite):
    _SUBMERGE_SPEED: float = 3.2  # Units/s
    _DETECTION_OFFSET: Vec2 = Vec2(1, 1.5)
    _BUBBLE_SPAWN_OFFSET: Vec2 = Vec2(2, 3)
    _BUBBLE_SPAWN_SPREAD: int = 3
    _HIDE_ANCHOR_OFFSET: Vec2 = Vec2(1, 1)
    color = colex.YELLOW
    texture = [
        " ╽ ",
        "|#|",
        "╰╴╯",
    ]

    def __init__(self) -> None:
        self.inventory = SizedInventory(slot_limit=8)
        ui_offset = Vec2(settings.UI_RIGHT_OFFSET - 10, 1)
        self._ui = ui.InventoryWheel(
            self,
            ref=self.inventory,
            hide_anchor=-ui_offset + self._HIDE_ANCHOR_OFFSET,
        ).with_position(ui_offset)
        self._stop_submerging = False

    def grab_focus(self) -> None:
        # self._ui.hide_anchor = self.global_position - self._ui.global_position
        super().grab_focus()
        self._ui.animate_show()

    def loose_focus(self) -> None:
        super().loose_focus()
        self._ui.animate_hide()

    def on_interact(self, actor: Sprite) -> None:
        assert isinstance(actor, Player), (
            f"Only `{Player.__name__}` can loot `{self.__class__.__name__}`"
        )
        for item in self.inventory.ids():
            count = self.inventory.count(item)
            # Transfer loot
            self.inventory.take(item, count)
            actor.inventory.give(item, count)
            break  # Only take 1 item
        if not self.inventory.ids():
            self._ui.animate_hide()

    def update(self) -> None:
        if not self.inventory.ids() and not self._ui.is_open():
            self.queue_free()
            Bubble().with_global_position(self.global_position)
            return
        if self._stop_submerging:
            return

        bubble = Bubble().with_global_position(
            self.global_position + self._BUBBLE_SPAWN_OFFSET
        )
        bubble.position.x += random.randint(
            -self._BUBBLE_SPAWN_SPREAD, self._BUBBLE_SPAWN_SPREAD
        )

        self.position.y += (1 / settings.FPS) * self._SUBMERGE_SPEED
        if ocean.Floor.has_loose_point_inside(
            self.global_position + self._DETECTION_OFFSET
        ):
            while ocean.Floor.has_loose_point_inside(
                self.global_position + self._DETECTION_OFFSET
            ):
                self.position += Vec2.UP
            self._stop_submerging = True


class Player(ColliderComponent, Sprite):
    _GRAVITY: float = 0.91
    _MAX_SPEED: Vec2 = Vec2(2, 2)
    _JUMP_STRENGTH: float = 4
    _AIR_FRICTION: float = 0.7
    _WATER_FRICTION: float = 0.3

    _HUNGER_RATE: float = 0.25
    _THIRST_RATE: float = 0.25
    _OXYGEN_RATE: float = 30

    _DEATH_DROP_OFFSET: Vec2 = Vec2(-2, -1)
    _HUD_TYPE: type[ui.ComposedHUD] = ui.ComposedHUD

    _DROWN_DAMAGE: float = 40  # Per second
    _CRITICAL_DEPTH_DROWN_DAMAGE_MULTIPLIER: float = 5
    _CRITICAL_DEPTH_AIR_CONSUMPTION_MULTIPLIER: float = 3

    _RANGED_REACH: float = 40

    input_handler: InputHandler = Keyboard()
    hitbox = Hitbox(size=Vec2(5, 3))
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
    _current_interactable: Sprite | None = None
    _current_targetable: Sprite | None = None

    def __init__(self) -> None:
        self.inventory = SizedInventory(slot_limit=8)
        # Gear - May be base model; `None`
        self._knife = gear_types.Knife(model=None)
        self._diving_mask = gear_types.DivingMask(model=None)
        self._o2_tank = gear_types.O2Tank(model=None)
        self._swimming_suite = gear_types.DivingSuite(model=None)
        self._harpoon = gear_types.Harpoon(model=ItemID.MAKESHIFT_HARPOON)
        # UI
        # NOTE: Current `Camera` has to be initialized before `Player.__init__` is called
        self.hud = self._HUD_TYPE(Camera.current, inventory_ref=self.inventory)

    @property
    def health(self) -> float:
        return self.hud.health_bar.value

    @health.setter  # NOTE: Clamped health
    def health(self, new_health: float) -> None:
        # NOTE: Use min-max until `int | float` is changed in `linflex`
        change = new_health - self.hud.health_bar.value
        self.hud.health_bar.value = min(
            max(
                new_health,
                0,
            ),
            self.hud.health_bar.MAX_VALUE,
        )
        if change < 0:  # Took damage
            Blood().with_global_position(
                x=self.global_position.x - 1,
                y=self.global_position.y - 1,
            )

    @property
    def damage(self) -> float:
        return self._knife.value

    def update(self) -> None:
        # Order of tasks
        self.input_handler.capture_states()
        self.handle_gui()
        self.handle_movement()
        self.handle_interact_selection()
        self.handle_interact()
        self.handle_target_selection()
        self.handle_target()
        self.handle_collect()
        self.handle_oxygen()
        self.handle_hunger()
        self.handle_thirst()
        self.handle_eating()
        self.handle_drinking()
        self.handle_healing()
        self.handle_gear_texture()
        # Check if dead
        if self.health == 0:
            self.on_death()

    def consume_item(self, item: ItemID, count: Count = 1) -> None:
        assert item in consumables, (
            f"All consumable items require additional metadata, for item: {item}"
        )
        if not self.inventory.has(item):
            raise KeyError(
                f"Attempted removing {count} {item.name},"
                f" but {item.name} is not found in {self.inventory}"
            )
        elif count > self.inventory.count(item):
            raise ValueError(
                f"Attempted to remove {count} {item.name},"
                f" but only has {self.inventory.count(item)} in {self.inventory}"
            )
        self.inventory.take(item, count)

        for stat in ConsumableStat:
            if stat not in consumables[item]:
                continue

            match stat:
                case ConsumableStat.HUNGER:
                    hunger_restore = consumables[item][stat]
                    self.hud.hunger_bar.value += hunger_restore
                case ConsumableStat.THIRST:
                    thirst_restore = consumables[item][stat]
                    self.hud.thirst_bar.value += thirst_restore
                case ConsumableStat.HEALING:
                    healing = consumables[item][stat]
                    self.hud.health_bar.value += healing
                case _:
                    assert_never(stat)

    def equip_gear(self, item: ItemID) -> None:
        assert item in gear, f"Gear item {item} is not in gear registry"
        assert self.inventory.has(item), (
            f"Attempted to equip {item}, but it's not found in inventory"
        )
        # NOTE: Currently does not allow to keep extra gear crafted
        self.inventory.set(item, 0)

        slot = gear[item][0]
        match slot:
            case Slot.MELEE:
                self._knife.model = item
            case Slot.MASK:
                self._diving_mask.model = item
            case Slot.SUITE:
                self._swimming_suite.model = item
            case Slot.TANK:
                self._o2_tank.model = item
            case Slot.RANGED:
                self._harpoon.model = item
            case _:
                assert_never(slot)

    def handle_eating(self) -> None:
        if self.input_handler.is_action_just_pressed(Action.EAT):
            for item in self.inventory.ids():
                if item in consumables and ConsumableStat.HUNGER in consumables[item]:
                    self.consume_item(item)
                    break

    def handle_drinking(self) -> None:
        if self.input_handler.is_action_just_pressed(Action.DRINK):
            for item in self.inventory.ids():
                if item in consumables and ConsumableStat.THIRST in consumables[item]:
                    self.consume_item(item)
                    break

    def handle_healing(self) -> None:
        if self.input_handler.is_action_just_pressed(Action.HEAL):
            for item in self.inventory.ids():
                if item in consumables and ConsumableStat.HEALING in consumables[item]:
                    self.consume_item(item)
                    break

    def is_submerged(self) -> bool:
        self_height = self.global_position.y - self.get_texture_size().y / 2
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def is_in_ocean(self):
        self_height = self.global_position.y + self.get_texture_size().y / 2 - 1
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def is_at_critical_depth(self) -> bool:
        return (
            self.global_position.y - ocean.Water.REST_LEVEL > self._swimming_suite.value
        )

    def is_in_building(self) -> bool:
        return isinstance(self.parent, Building)

    def is_colliding_with_ocean_floor(self) -> bool:
        center = self.global_position
        if self.centered:
            center -= self.get_texture_size() / 2
        for x_offset in range(int(self.get_texture_size().x)):
            for y_offset in range(int(self.get_texture_size().y)):
                global_point = (
                    floor(center.x + x_offset),
                    floor(center.y + y_offset),
                )
                if global_point in ocean.Floor.points:
                    return True
        return False

    def handle_gui(self) -> None:
        if not isinstance(self._current_interactable, Fabrication):
            if self.input_handler.is_action_just_pressed(Action.OPEN_INVENTORY):
                if self.hud.inventory.is_open():
                    self.hud.inventory.animate_hide()
                else:
                    self.hud.inventory.animate_show()
            return
        if self.input_handler.is_action_just_pressed(Action.SCROLL_DOWN):
            self._current_interactable.attempt_select_next_recipe()
        elif self.input_handler.is_action_just_pressed(Action.SCROLL_UP):
            self._current_interactable.attempt_select_previous_recipe()

    def handle_movement_in_building(self, velocity: Vec2) -> None:
        assert isinstance(self.parent, Building)
        # TODO: Check if is on floor first
        if self.input_handler.is_action_just_pressed(Action.JUMP):
            self._y_speed = -self._JUMP_STRENGTH
        combined_velocity = Vec2(velocity.x, self._y_speed).clamp(
            -self._MAX_SPEED,
            self._MAX_SPEED,
        )
        self.parent.move_and_collide_inside(self, combined_velocity)
        # Apply friction
        self._y_speed = move_toward(self._y_speed, 0, self._AIR_FRICTION)

    def handle_movement(self) -> None:
        # TODO: Apply axis snapping
        velocity = self.input_handler.get_vector(
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
            Action.MOVE_UP,
            Action.MOVE_DOWN,
        )
        # Is in builindg movement
        if self.is_in_building():
            self.handle_movement_in_building(velocity)
            return
        # Is in air movement
        elif not self.is_in_ocean():
            self._y_speed += self._GRAVITY
        # Is in ocean movement
        combined_velocity = Vec2(velocity.x, velocity.y + self._y_speed).clamp(
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
        if (  # Is in building with oxygen - Type safe
            isinstance(self.parent, Building) and self.parent.HAS_OXYGEN
        ):
            self.hud.oxygen_bar.fill()
            return
        # Restore oxygen if above ocean waves
        if not self.is_submerged():
            if self.hud.oxygen_bar.value != self.hud.oxygen_bar.MAX_VALUE:
                self.hud.oxygen_bar.fill()
            return
        # Decrease health if no oxygen
        if self.hud.oxygen_bar.value == 0:
            drown_damage = self._DROWN_DAMAGE / settings.FPS  # X HP per second
            if self.is_at_critical_depth():
                drown_damage *= self._CRITICAL_DEPTH_DROWN_DAMAGE_MULTIPLIER
                drown_damage *= 1 - self._o2_tank.value
            self.health -= drown_damage
            return
        # Decrease oxygen
        rate = self._OXYGEN_RATE / settings.FPS
        if self.is_at_critical_depth():
            rate *= self._CRITICAL_DEPTH_AIR_CONSUMPTION_MULTIPLIER
            rate *= 1 - self._o2_tank.value
        oxygen_bubble_count = self.hud.oxygen_bar.cell_count
        rate *= 1 - self._diving_mask.value
        self.hud.oxygen_bar.value -= rate
        if self.hud.oxygen_bar.cell_count < oxygen_bubble_count:
            Bubble().with_global_position(
                x=self.global_position.x,
                y=self.global_position.y - 1,
            )

    def handle_hunger(self) -> None:
        self.hud.hunger_bar.value -= self._HUNGER_RATE / settings.FPS
        if self.hud.hunger_bar.value == 0:
            self.health -= 1

    def handle_thirst(self) -> None:
        self.hud.thirst_bar.value -= self._THIRST_RATE / settings.FPS
        if self.hud.thirst_bar.value == 0:
            self.health -= 1

    def handle_interact_selection(self) -> None:
        proximite_interactables: list[tuple[float, Interactable]] = []
        global_point = self.global_position  # Store property value outside loop
        for node in Scene.current.get_group_members(Group.TEXTURE, type_hint=Sprite):
            if (
                isinstance(node, Interactable)
                and node.interactable
                and (condition_and_dist := node.is_in_range_of(global_point))[0]
            ):  # I know this syntax might be a bit too much,
                # but know that it made it easier to split logic into mixin class
                proximite_interactables.append((condition_and_dist[1], node))

        # Highlight closest interactable - Using DSU
        if proximite_interactables:
            proximite_interactables.sort(key=lambda pair: pair[0])
            # Allow this because `Interactable` should always be used with `Sprite`
            if isinstance(self._current_interactable, Interactable):
                # Reset color to class color
                self._current_interactable.loose_focus()
                self._current_interactable.on_deselect(self)
            # Reverse color of current interactable
            first = proximite_interactables[0][1]
            assert isinstance(
                first,
                Sprite,
            ), f"{first.__class__} is missing `Sprite` base"
            self._current_interactable = first
            self._current_interactable.grab_focus()
            self._current_interactable.when_selected(self)
        # Or unselect last interactable that *was* in reach
        elif self._current_interactable is not None:
            assert isinstance(self._current_interactable, Interactable)
            self._current_interactable.loose_focus()
            self._current_interactable.on_deselect(self)
            self._current_interactable = None

    def handle_interact(self) -> None:
        if self._current_interactable is None:
            return
        assert isinstance(self._current_interactable, Interactable)
        # Trigger interaction function
        if self.input_handler.is_action_just_pressed(Action.INTERACT):
            # TODO: Check for z_index change, so that it respects z_index change in on_interact
            # TODO: Check if current interactable is capable of crafting -> Use `Action.CRAFTING`
            self._current_interactable.on_interact(self)

    def handle_target_selection(self) -> None:
        proximite_targetables: list[tuple[float, Targetable]] = []
        global_point = self.global_position  # Store property value outside loop
        reach_squared = self._RANGED_REACH * self._RANGED_REACH
        # TODO: Iterate over a smaller collection
        for node in Scene.current.get_group_members(Group.TEXTURE, type_hint=Sprite):
            if (
                isinstance(node, Targetable)
                and (distance := global_point.distance_squared_to(node.global_position))
                < reach_squared
            ):  # I know this syntax might be a bit too much,
                # but know that it made it easier to split logic into mixin class
                proximite_targetables.append((distance, node))

        # Highlight closest interactable - Using DSU
        if proximite_targetables:
            proximite_targetables.sort(key=lambda pair: pair[0])
            # Allow this because `Interactable` should always be used with `Sprite`
            if isinstance(self._current_targetable, Targetable):
                # Reset color to class color
                self._current_targetable.gain_target()
            # Reverse color of current interactable
            first = proximite_targetables[0][1]
            assert isinstance(
                first,
                Sprite,
            ), f"{first.__class__} is missing `Sprite` base"
            self._current_targetable = first
            # TODO: Do Harpoon aiming here, and fire if key pressed
            if (
                self.input_handler.is_action_just_pressed(Action.THROW_HARPOON)
                and self._harpoon.model is not None
            ):
                harpoon_info = gear[self._harpoon.model]
                damage = harpoon_info[1]
                projectiles.HarpoonSpear(
                    position=self.global_position,
                ).with_target(first).with_damage(damage)
            # self._current_targetable.grab_focus()
            # self._current_targetable.when_selected(self)
        # Or unselect last interactable that *was* in reach
        elif self._current_targetable is not None:
            assert isinstance(self._current_targetable, Targetable)
            self._current_targetable.loose_target()
            self._current_targetable = None

    def handle_target(self) -> None:
        if self._current_targetable is None:
            return
        assert isinstance(self._current_targetable, Targetable)
        # Trigger interaction function
        if self.input_handler.is_action_just_pressed(Action.INTERACT):
            # TODO: Check for z_index change, so that it respects z_index change in on_interact
            self._current_targetable.gain_target()

    def handle_collect(self) -> None:
        if self._current_interactable is None:
            return
        if not isinstance(self._current_interactable, Collectable):
            return
        # Collect collectable that is selected
        # `self._current_interactable` is already in reach
        if self.input_handler.is_action_just_pressed(Action.INTERACT):
            self._current_interactable.collect_into(self.inventory)
            self._current_interactable.queue_free()
            self._current_interactable = None

    def handle_gear_texture(self) -> None:
        self.texture = deepcopy(self.__class__.texture)
        if self.is_in_building():
            return
        if not self.is_in_ocean():
            return
        match self._swimming_suite.model:
            case ItemID.BASIC_SUITE:
                self.texture[1] = "/{|}\\"
            case ItemID.ADVANCED_SUITE:
                self.texture[1] = "/(|)\\"
        match self._o2_tank.model:
            case ItemID.O2_TANK:
                self.texture[1] = self.texture[1][:2] + "&" + self.texture[1][3:]
            case ItemID.HIGH_CAPACITY_O2_TANK:
                self.texture[1] = self.texture[1][:2] + "%" + self.texture[1][3:]
        if not self.is_submerged():
            return
        match self._diving_mask.model:
            case ItemID.BASIC_DIVING_MASK:
                self.texture[0] = " {#}"
            case ItemID.IMPROVED_DIVING_MASK:
                self.texture[0] = " [#]"

    def on_death(self) -> None:
        # Reset stats
        self.health = self.hud.health_bar.MAX_VALUE
        self.hud.hunger_bar.value = self.hud.hunger_bar.MAX_VALUE
        self.hud.thirst_bar.value = self.hud.thirst_bar.MAX_VALUE

        # Drop loot sack
        if self.inventory.ids():
            sack = PlayerDeathDrop().with_global_position(
                self.global_position + self._DEATH_DROP_OFFSET
            )
            for item in self.inventory.ids():
                count = self.inventory.count(item)
                # Transfer loot
                self.inventory.take(item, count)
                sack.inventory.give(item, count)
            self.inventory.clear()

        # TP back to surface air
        self.global_position = Vec2(20 + random.randint(0, 20), -20)
        while self.is_colliding():  # Avoid colliding with player in air at respawn
            self.global_position = Vec2(20 + random.randint(0, 20), -20)

        # Hide inventory UI instantly
        self.hud.inventory.animate_hide()
        self.hud.inventory.hide()

        # Release current interactable focus
        self.parent = None  # Just in case, temp anyways...
        if isinstance(self._current_interactable, Interactable):
            self._current_interactable.loose_focus()

        # Reset states
        self._current_interactable = None
        self._current_action = None
        self._key_just_pressed = False


# The following player classes below are for co-op mode


class Player1(Player):
    _HUD_TYPE = ui.ComposedHUD1
    position = Vec2(17, -3)
    color = colex.CYAN


class Player2(Player):
    _HUD_TYPE = ui.ComposedHUD2
    position = Vec2(-15, -3)
    color = colex.YELLOW
    input_handler = Keyboard(
        {
            Action.MOVE_LEFT: "H",
            Action.MOVE_RIGHT: "L",
            Action.MOVE_DOWN: "J",
            Action.MOVE_UP: "K",
            Action.INTERACT: "Ø",
            Action.CONFIRM: "M",
            Action.EAT: "Y",
            Action.DRINK: "U",
            Action.HEAL: "I",
            Action.JUMP: "P",
            Action.SCROLL_UP: ",",
            Action.SCROLL_DOWN: ".",
            Action.THROW_HARPOON: "-",
            Action.OPEN_INVENTORY: "N",
        },
        modifier_key="Alt Gr",
    )
