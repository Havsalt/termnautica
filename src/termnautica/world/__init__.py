from charz import Scene

from .. import settings
from .generate import generate_world
from .save import save_world
from .load import apply_save_data
from .schemas import Seed


def create() -> Seed:
    save_path = settings.SAVE_FOLDER / "save.toml"
    if save_path.exists():
        with save_path.open("rb") as file:
            world_data = generate_world(save_file=file)
            apply_save_data(world_data)
        return world_data["seed"]
    else:
        world_data = generate_world()
        return world_data["seed"]


def save(*, seed: Seed) -> None:
    save_world(Scene.current, seed=seed)
