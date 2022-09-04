from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def as_tuple(cls):
        return tuple(attribute.name for attribute in cls)

    def __str__(self):
        return self.name

    def __int__(self):
        return self.value - 1
