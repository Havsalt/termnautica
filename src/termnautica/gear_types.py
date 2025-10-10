# NOTE: Manually import every `NewType` instance
from .item import (
    ItemID,
    Slot,
    GearStat,
    Damage,
    BreathReduction,
    PressureReduction,
    CriticalDepth,
    gear,
)


# IDEA: Have each gear have 1 single stat


class Gear:
    _SLOT: Slot
    _STAT_DEFAULT_VALUE: GearStat

    def __init__(
        self,
        model: ItemID | None,
    ) -> None:
        # Check for valid oxygen tank
        assert model is None or (model in gear and self._SLOT is gear[model][0]), (
            f"Invalid model: {model}"
        )
        self._model = model

    @property
    def model(self) -> ItemID | None:
        return self._model

    @model.setter
    def model(self, new_model: ItemID | None) -> None:
        # Check if new oxygen tank is valid
        assert new_model is None or (
            new_model in gear and self._SLOT in gear[new_model]
        ), f"Invalid model: {new_model}"
        self._model = new_model

    @property
    def value(self) -> float:
        return (
            gear[self._model][1]
            if self._model is not None
            else self._STAT_DEFAULT_VALUE
        )


class Knife(Gear):
    _SLOT = Slot.MELEE
    _STAT_DEFAULT_VALUE = Damage(1)


class DivingSuite(Gear):
    _SLOT = Slot.SUITE
    _STAT_DEFAULT_VALUE = CriticalDepth(20)


class DivingMask(Gear):
    _SLOT = Slot.MASK
    _STAT_DEFAULT_VALUE = BreathReduction(0.00)


class O2Tank(Gear):
    _SLOT = Slot.TANK
    _STAT_DEFAULT_VALUE = PressureReduction(0.00)


class Harpoon(Gear):
    _SLOT = Slot.RANGED
    _STAT_DEFAULT_VALUE = Damage(0)
