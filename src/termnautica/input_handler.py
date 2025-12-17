from __future__ import annotations

from enum import Enum, unique, auto
from typing import Protocol, assert_never

import keyboard
import pygame
from charz import Vec2


type ActionMap[V] = dict[Action, V]
type Percent = int
"""Example: `x: Percent = 10`, meaning *10%*. When computing: `result = x / 100`"""


@unique
class Action(Enum):
    # TODO: Have `Player` check for each action, and not assume they will have same trigger
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    JUMP = auto()

    INTERACT = auto()
    CRAFT = auto()  # NOTE: Might be redundant because of `INTERACT` variant
    ATTACK = auto()  # NOTE: Might be redundant because of `INTERACT` variant
    THROW_HARPOON = auto()

    EAT = auto()
    DRINK = auto()
    HEAL = auto()

    SCROLL_UP = auto()
    SCROLL_DOWN = auto()
    CONFIRM = auto()
    OPEN_INVENTORY = auto()


class InputHandler(Protocol):
    def capture_states(self) -> None:
        """Capture press state of all `Action` variants, used for monitoring changes over time.

        Should be called at the start of the frame, *before* actions are checked for.
        """

    def is_action_pressed(self, action: Action) -> bool: ...
    def is_action_just_pressed(self, action: Action) -> bool: ...
    def get_vector(
        self,
        negative_x: Action,
        positive_x: Action,
        negative_y: Action,
        positive_y: Action,
    ) -> Vec2: ...


class Keyboard:
    type Key = str | int
    type ScanCode = int
    type KeyCombination = str | list[ScanCode]

    def __init__(
        self,
        action_map: ActionMap[Keyboard.Key | Keyboard.KeyCombination] | None = None,
        modifier_key: Keyboard.Key = "Shift",
    ) -> None:
        self._action_states = dict[Action, bool]()
        self._last_action_states = dict[Action, bool]()
        self._modifier_key = modifier_key
        self._action_map: ActionMap[Keyboard.Key | Keyboard.KeyCombination] = (
            {  # Adding defaults at bottom of dict
                Action.MOVE_LEFT: "A",
                Action.MOVE_RIGHT: "D",
                Action.MOVE_UP: "W",
                Action.MOVE_DOWN: "S",
                Action.JUMP: "Space",
                #
                Action.INTERACT: "E",
                Action.CRAFT: "E",
                Action.ATTACK: "E",
                Action.THROW_HARPOON: "R",
                #
                Action.EAT: "1",
                Action.DRINK: "2",
                Action.HEAL: "3",
                #
                Action.SCROLL_UP: "{modifier}+Tab",
                Action.SCROLL_DOWN: "Tab",
                Action.CONFIRM: "Q",
                Action.OPEN_INVENTORY: "F",
            }
            | (action_map or {})  # Adds default actions if not defined
        )
        assert all(map(self._action_map.__contains__, Action)), "Missing actions"

    def capture_states(self) -> None:
        self._last_action_states = self._action_states
        self._action_states = {
            action: self.is_action_pressed(action) for action in Action
        }

    def is_action_pressed(self, action: Action) -> bool:
        trigger = self._action_map[action]
        if isinstance(trigger, str):
            keys = trigger.format(modifier=self._modifier_key)
            return keyboard.is_pressed(keys)
        else:
            # Single or multiple scancode list
            return keyboard.is_pressed(trigger)

    def is_action_just_pressed(self, action: Action) -> bool:
        return (  # fmt: off
            not self._last_action_states.get(action, True)
            and self.is_action_pressed(action)
        )  # fmt: on

    def get_vector(
        self,
        negative_x: Action,
        positive_x: Action,
        negative_y: Action,
        positive_y: Action,
    ) -> Vec2:
        return Vec2(
            self.is_action_pressed(positive_x) - self.is_action_pressed(negative_x),
            self.is_action_pressed(positive_y) - self.is_action_pressed(negative_y),
        )


class Controller:
    type DeviceID = int
    type Button = int
    type Axis = int
    pygame.display.init()
    pygame.joystick.init()

    class Trigger:
        class Limit(Enum):
            POSITIVE = auto()
            NEGATIVE = auto()

        def __init__(
            self,
            axis: Controller.Axis,
            limit: Controller.Trigger.Limit | None = None,
            deadzone: Percent = 10,
        ) -> None:
            if deadzone <= 0:
                raise ValueError(f"Param 'deadzone' <= 0, got {deadzone}")
            self.axis = axis
            self.limit = limit
            self.deadzone = deadzone

    def __init__(
        self,
        action_map: ActionMap[Controller.Button | Controller.Trigger] | None = None,
        device_id: Controller.DeviceID | None = None,
    ) -> None:
        if device_id is not None:
            self._joystick = pygame.joystick.Joystick(device_id)
        else:  # Attempt to connect to the next available controller
            # NOTE: This branch might be redundant, and param `device_id` should be manual
            for attempt_id in range(pygame.joystick.get_count()):
                try:
                    joystick = pygame.joystick.Joystick(attempt_id)
                except pygame.error:
                    continue
                self._joystick = joystick
                break
            else:  # nobreak
                raise ValueError("Could not automatically find available controller")
        self._action_states = dict[Action, bool]()
        self._last_action_states = dict[Action, bool]()
        self._action_map: ActionMap[Controller.Button | Controller.Trigger] = (
            {  # Adding defaults at bottom of dict
                Action.MOVE_LEFT: Controller.Trigger(
                    pygame.CONTROLLER_AXIS_LEFTX,
                    Controller.Trigger.Limit.NEGATIVE,
                    deadzone=35,
                ),
                Action.MOVE_RIGHT: Controller.Trigger(
                    pygame.CONTROLLER_AXIS_LEFTX,
                    Controller.Trigger.Limit.POSITIVE,
                    deadzone=35,
                ),
                Action.MOVE_UP: Controller.Trigger(
                    pygame.CONTROLLER_AXIS_LEFTY,
                    Controller.Trigger.Limit.NEGATIVE,
                    deadzone=35,
                ),
                Action.MOVE_DOWN: Controller.Trigger(
                    pygame.CONTROLLER_AXIS_LEFTY,
                    Controller.Trigger.Limit.POSITIVE,
                    deadzone=35,
                ),
                Action.JUMP: pygame.CONTROLLER_BUTTON_A,
                #
                Action.INTERACT: pygame.CONTROLLER_BUTTON_X,
                Action.CRAFT: pygame.CONTROLLER_BUTTON_B,
                Action.ATTACK: pygame.CONTROLLER_BUTTON_A,
                Action.THROW_HARPOON: pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
                #
                Action.EAT: pygame.CONTROLLER_BUTTON_DPAD_UP,
                Action.DRINK: pygame.CONTROLLER_BUTTON_DPAD_DOWN,
                Action.HEAL: pygame.CONTROLLER_BUTTON_DPAD_RIGHT,
                #
                Action.SCROLL_UP: pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
                Action.SCROLL_DOWN: pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
                Action.CONFIRM: pygame.CONTROLLER_BUTTON_B,
                Action.OPEN_INVENTORY: pygame.CONTROLLER_BUTTON_Y,
            }
            | (action_map or {})  # Adds default actions if not defined
        )
        assert all(map(self._action_map.__contains__, Action)), "Missing actions"

    def capture_states(self) -> None:
        """NOTE: Requires `pygame.event.pump` to be called *before*"""
        self._last_action_states = self._action_states
        self._action_states = {
            action: self.is_action_pressed(action) for action in Action
        }

    def is_action_pressed(self, action: Action) -> bool:
        trigger = self._action_map[action]

        if not isinstance(trigger, Controller.Trigger):
            return self._joystick.get_button(trigger)

        strength = self._joystick.get_axis(trigger.axis)
        match trigger.limit:
            case Controller.Trigger.Limit.POSITIVE:
                return strength > trigger.deadzone / 100
            case Controller.Trigger.Limit.NEGATIVE:
                return strength < -trigger.deadzone / 100
            case None:
                return abs(strength) > trigger.deadzone / 100
            case _:
                assert_never(trigger.limit)

    def is_action_just_pressed(self, action: Action) -> bool:
        return (  # fmt: off
            not self._last_action_states.get(action, True)
            and self.is_action_pressed(action)
        )  # fmt: on

    def get_vector(
        self,
        negative_x: Action,
        positive_x: Action,
        negative_y: Action,
        positive_y: Action,
    ) -> Vec2:
        return Vec2(
            self.is_action_pressed(positive_x) - self.is_action_pressed(negative_x),
            self.is_action_pressed(positive_y) - self.is_action_pressed(negative_y),
        )
