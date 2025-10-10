from pathlib import Path as _Path


FPS: float = 16
WORLD_WIDTH: int = 500 + 500
ASSETS_FOLDER = _Path(__file__).parent.joinpath("assets")
SPRITES_FOLDER = ASSETS_FOLDER / "sprites"
ANIMATION_FOLDER = ASSETS_FOLDER / "animations"
SOUNDS_FOLDER = ASSETS_FOLDER / "sounds"
MUSIC_FOLDER = ASSETS_FOLDER / "music"
