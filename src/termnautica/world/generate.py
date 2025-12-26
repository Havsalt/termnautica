import random
import tomllib
from typing import BinaryIO

from .. import ocean
from .schemas import Seed, SaveData


SEED_MIN: Seed = 1
SEED_MAX: Seed = 1000


def generate_static() -> None:
    ocean.generate_floor()
    ocean.generate_water()


def generate_world(*, save_file: BinaryIO | None = None) -> SaveData:
    # Lazy loading - A quick workaround
    from ..buildings.lifepod import Lifepod

    if save_file is not None:
        toml = tomllib.load(save_file)
        try:
            data = SaveData(**toml)  # Also works as validation
        except tomllib.TOMLDecodeError as err:
            exit(f"Invalid toml save: {err}")
        random.seed(data["seed"])
    else:
        # random.seed(3)  # DEV
        new_seed = random.randint(SEED_MIN, SEED_MAX)
        random.seed(new_seed)
        data = SaveData(
            seed=new_seed,
            wave_time=0,
            players=[],
            # spawners=[],
            # tiles=[],
        )
    generate_static()
    # Attatch lifepod to waving water
    # TODO: Update `Lifepod` position internally using ocean formula
    lifepod = Lifepod()
    middle_ocean_water = ocean.Water().save_rest_location()
    lifepod.parent = middle_ocean_water
    return data
