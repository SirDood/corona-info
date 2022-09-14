import os
from pathlib import Path


class App:
    ID = "com.izzthedude.CoronaInfo"
    NAME = "Corona Info"
    VERSION = "0.2.1"
    WEBSITE = "https://github.com/izzthedude/corona-info"


class Paths:
    SOURCE_DIR = Path(__file__).parent
    RESOURCES = SOURCE_DIR / "resources"
    UI = RESOURCES / "ui"

    _xdg_cache = os.environ.get("XDG_CACHE_HOME")
    CACHE_DIR = Path(_xdg_cache) if _xdg_cache else Path.home() / ".cache" / App.ID
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_JSON = CACHE_DIR / "cache.json"

    _xdg_data = os.environ.get("XDG_DATA_HOME")
    DATA_DIR = Path(_xdg_data) if _xdg_data else CACHE_DIR
    SETTINGS_JSON = DATA_DIR / "settings.json"

    _xdg_state = os.environ.get("XDG_STATE_HOME")
    STATE_DIR = Path(_xdg_state) if _xdg_state else DATA_DIR
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    LOGS_DIR = STATE_DIR / "logs"

    DOWNLOADS_DIR = Path.home() / "Downloads"


class Date:
    RAW_FORMAT = "%Y-%m-%d %H:%M:%S"
    FILE_FORMAT = "%Y-%m-%d-%H-%M-%S"
    DISPLAY_FORMAT = "%-d %b %H:%M"
