import logging
from dataclasses import dataclass

from coronainfo.enums import Paths
from coronainfo.models.model_base import BaseData
from coronainfo.utils.files import write_json


@dataclass
class AppSettings(BaseData):
    last_fetched: str

    @classmethod
    def placeholder(cls):
        return cls(
            ""
        )

    def commit(self):
        path = Paths.SETTINGS_JSON
        logging.debug(f"Saving app settings to: {path}")
        write_json(path, self.as_dict())
