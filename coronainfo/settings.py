import logging
from dataclasses import dataclass, asdict

from coronainfo.enums import Paths
from coronainfo.utils.files import get_json, write_json


@dataclass
class AppSettings:
    last_fetched: str

    @classmethod
    def fetch_settings(cls):
        try:
            settings = cls(**get_json(Paths.SETTINGS_JSON))
            logging.debug(f"App settings: {settings}")
            return settings

        except Exception as err:
            logging.warning(f"An error has occurred while getting app settings: {err}")
            logging.info("Attempting to return placeholder settings")
            settings = cls.placeholder()
            logging.debug(f"Placeholder app settings: {settings}")
            return settings

    @classmethod
    def placeholder(cls):
        return cls(
            ""
        )

    def commit(self):
        path = Paths.SETTINGS_JSON
        logging.debug(f"Saving app settings to: {path}")
        write_json(path, asdict(self))
