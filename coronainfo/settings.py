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
        write_json(Paths.SETTINGS_JSON, self.as_dict())
