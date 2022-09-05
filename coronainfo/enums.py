from pathlib import Path


class Paths:
    SOURCE_DIR = Path(__file__).parent
    RESOURCES = SOURCE_DIR / "resources"
    UI = RESOURCES / "ui"

    CACHE_DIR = Path.home() / ".cache" / "coronainfo"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE = CACHE_DIR / "data.json"
