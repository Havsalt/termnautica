from typing import Self

import colex
from charz import Node, Sprite

from .props import Targetable, HasHealth


class HarpoonSpear(Sprite):
    _MARGIN: float = 3
    _SPEED: float = 3  # Per frame
    _target: Targetable | None = None
    _damage: float | None = None
    color = colex.AZURE
    texture = ["====!"]

    def with_target(self, target: Sprite | None, /) -> Self:
        assert isinstance(target, Targetable)
        self._target = target
        return self

    def with_damage(self, damage: float | None, /) -> Self:
        self._damage = damage
        return self

    def update(self, _delta: float) -> None:
        assert isinstance(self._target, Sprite), (
            f"Target {self._target} missing `Sprite` base"
        )
        assert isinstance(self._damage, (float, int)), (
            f"Damage is not set. Use `.with_damage(...)`"
        )

        # Check if target is still in world
        if self._target.uid not in Node.node_instances:
            self.queue_free()
            return

        # TODO: ADD GRAVITY
        direction = self.global_position.direction_to(self._target.global_position)
        distance = self.global_position.distance_to(self._target.global_position)
        move_distance = min(self._SPEED, distance)
        self.global_position += direction * move_distance

        location = self.global_position
        margin_squared = self._MARGIN * self._MARGIN
        for node in tuple(Sprite.texture_instances.values()):
            if node is self:
                continue
            # DEV
            if node.__class__.__name__ == "Player":
                continue
            if not isinstance(node, HasHealth):
                continue
            if location.distance_squared_to(node.global_position) < margin_squared:
                node.health -= self._damage
                self.queue_free()
