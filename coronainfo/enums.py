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

    CACHE_DIR = Path.home() / ".cache" / "com.izzthedude.CoronaInfo"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE = CACHE_DIR / "data.json"
