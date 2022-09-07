import os
from pathlib import Path


class App:
    ID = "com.izzthedude.CoronaInfo"
    NAME = "Corona Info"
    VERSION = "0.1.0"
    WEBSITE = "https://github.com/izzthedude/corona-info"


class Paths:
    SOURCE_DIR = Path(__file__).parent
    RESOURCES = SOURCE_DIR / "resources"
    UI = RESOURCES / "ui"

    _xdg_cache = os.environ.get("XDG_CACHE_HOME")
    CACHE_DIR = Path(_xdg_cache) if _xdg_cache else Path.home() / ".cache" / App.ID
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE = CACHE_DIR / "data.json"
