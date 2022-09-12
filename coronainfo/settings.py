from dataclasses import dataclass

from coronainfo.models.model_base import BaseData


@dataclass
class Settings(BaseData):
    last_fetched: str

    @classmethod
    def placeholder(cls):
        return cls(
            ""
        )
