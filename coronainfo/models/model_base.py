import typing
from dataclasses import Field, astuple, fields, asdict
from enum import Enum
from typing import Iterable

from coronainfo.utils.functions import spread_subtypes


class BaseData:
    @classmethod
    def get_fields(cls) -> tuple[Field]:
        return fields(cls)

    def as_tuple(self):
        return astuple(self)

    def as_dict(self):
        return asdict(self)

    def __post_init__(self):
        self._tuple = astuple(self)

        # Type checking
        for field in fields(self):
            field_value = self.__dict__[field.name]
            field_type = field.type

            # Validate subtypes
            if isinstance(field_value, Iterable) and type(field_value) is not str:
                sub_types = typing.get_args(field_type)  # get the 'int' from list[int] etc.
                sub_types = spread_subtypes(sub_types)
                if sub_types:
                    field_type = typing.get_origin(field_type)  # get the 'list' from list[int] etc.

                for item in field_value:
                    if type(item) not in sub_types:
                        raise TypeError(
                            f"The field '{field.name}' with value(s) '{field_value}' contains one or more items "
                            f"that are not {sub_types}"
                        )

            if not type(field_value) == field_type:
                raise TypeError(
                    f"The field '{field.name}' with value '{getattr(self, field.name)}' is not of type "
                    f"{field.type}"
                )

    def __getitem__(self, item: int | str):
        # Make this accessible by subscripting.
        # Example: bruh_data[0] or bruh_data["attribute"]
        if type(item) is int:
            return self._tuple[item]
        elif type(item) is str:
            return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __len__(self):
        return len(self._tuple)


class BaseEnum(Enum):
    @classmethod
    def as_tuple(cls):
        return tuple(attribute.name for attribute in cls)

    def __str__(self):
        return self.name

    def __int__(self):
        return self.value - 1
