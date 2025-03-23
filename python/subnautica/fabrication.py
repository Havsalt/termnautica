from typing import TYPE_CHECKING

from charz import Sprite

from .props import Crafting
from .item import ItemID


# Type checking for lazy loading
if TYPE_CHECKING:
    from .player import Player
else:
    Player = None


def _ensure_player() -> None:
    # Lazy loading - A quick workaround
    global Player
    if Player is None:
        from .player import Player


type Count = int


# NOTE: Has to be *before* `Interactable` in mro
class Fabrication(Crafting):  # Extended Component (mixin class)
    _selected_recipe_index: int = 0  # Persist when GUI is closed

    def attempt_select_next_recipe(self) -> None:
        # NOTE: Use min-max until `int | float` is changed in `linflex`
        self._selected_recipe_index = min(
            len(self._RECIPES) - 1,
            max(
                0,
                self._selected_recipe_index + 1,
            ),
        )

    def attempt_select_previous_recipe(self) -> None:
        # NOTE: Use min-max until `int | float` is changed in `linflex`
        self._selected_recipe_index = min(
            len(self._RECIPES) - 1,
            max(
                0,
                self._selected_recipe_index - 1,
            ),
        )

    def can_craft_by_index(
        self,
        inventory: dict[ItemID, Count],
    ) -> bool:
        # Use local mutable variable
        recipe = self._RECIPES[self._selected_recipe_index]
        return self.can_craft(recipe, inventory)

    def craft_by_index(
        self,
        inventory: dict[ItemID, Count],
    ) -> None:
        # Use local mutable variable
        recipe = self._RECIPES[self._selected_recipe_index]
        self.craft(recipe, inventory)

    def when_selected(self, actor: Sprite) -> None:
        _ensure_player()
        assert isinstance(
            actor,
            Player,
        ), "Only `Player` can select `BasicFabricator`"
        actor.crafting_gui.show()
        all_recipe_states = [
            (
                recipe,
                self.can_craft(recipe, actor.inventory),
            )
            for recipe in self._RECIPES
        ]
        # TODO: Implement `selected_recipe_index`
        recipe = self._RECIPES[self._selected_recipe_index]
        selected_idgredient_counts = tuple(
            actor.inventory.get(item, 0) for item in recipe.idgredients
        )
        actor.crafting_gui.update_from_recipe(
            recipe,
            selected_idgredient_counts,
            all_recipe_states,
        )

    def on_deselect(self, actor: Sprite) -> None:
        _ensure_player()
        assert isinstance(
            actor,
            Player,
        ), "Only `Player` can select `BasicFabricator`"
        actor.crafting_gui.hide()

    def on_interact(self, actor: Sprite) -> None:
        _ensure_player()
        assert isinstance(
            actor,
            Player,
        ), "Only `Player` can interact with `BasicFabricator`"
        if self.can_craft_by_index(actor.inventory):
            self.craft_by_index(actor.inventory)
