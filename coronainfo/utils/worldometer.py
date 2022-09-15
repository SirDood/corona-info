import re
from dataclasses import asdict, astuple, dataclass, fields
from enum import Enum, auto
from typing import Union

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class CoronaData:
    country: str
    total_cases: int
    new_cases: int
    total_deaths: int
    new_deaths: int
    total_recovered: int
    new_recovered: int
    active_cases: int
    serious_cases: int
    total_cases_per_1m: int
    deaths_per_1m: int
    total_tests: int
    tests_per_1m: int
    population: int

    @classmethod
    def field_types(cls) -> tuple:
        return tuple(field.type for field in fields(cls))

    def __post_init__(self):
        self._tuple = astuple(self)

        # Type checking
        for field in fields(self):
            field_value = self.__dict__[field.name]
            if not isinstance(field_value, field.type):
                raise TypeError(
                    f"The field '{field.name}' with value '{field_value}' is not of type {field.type}"
                )

    def __getitem__(self, item: Union[int, str]):
        # Make this accessible by subscripting.
        # Example: bruh_data[0] or bruh_data["attribute"]
        if type(item) is int:
            return self._tuple[item]
        elif type(item) is str:
            return getattr(self, item)

    def __len__(self):
        return len(self._tuple)


class CoronaHeaders(Enum):
    COUNTRY = auto()
    TOTAL_CASES = auto()
    NEW_CASES = auto()
    TOTAL_DEATHS = auto()
    NEW_DEATHS = auto()
    TOTAL_RECOVERED = auto()
    NEW_RECOVERED = auto()
    ACTIVE_CASES = auto()
    SERIOUS_CASES = auto()
    TOTAL_CASES_PER_1M = auto()
    DEATHS_PER_1M = auto()
    TOTAL_TESTS = auto()
    TESTS_PER_1M = auto()
    POPULATION = auto()

    @classmethod
    def as_tuple(cls):
        return tuple(attribute.name for attribute in cls)

    def __str__(self):
        return self.name

    def __int__(self):
        return self.value - 1


def fetch_data() -> list[dict]:
    url = "https://www.worldometers.info/coronavirus/"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")

    # Find the 'today' table
    table = soup.find(id="main_table_countries_today")
    table_body = table.find("tbody")
    parsed_table = list(asdict(country) for country in _parse_table_html(table_body))

    return parsed_table


def _parse_table_html(table: Tag) -> map:  # iterable[CoronaData]
    countries: list[Tag] = table.find_all("tr")[7:]
    result = map(lambda country: sanitise_row(country), countries)

    def sanitise_row(clean_row: Tag) -> CoronaData:
        row_data = clean_row.find_all("td")[1:15]
        sanitised_row = map(lambda enum: sanitise_value(enum[0], enum[1].text), enumerate(row_data))
        corona_data = CoronaData(*sanitised_row)
        return corona_data

    def sanitise_value(column: int, value: str):
        sanitised_value = value.replace(",", "").strip()

        if sanitised_value == "N/A" or not sanitised_value:
            sanitised_value = 0

        clean_value = sanitised_value
        if isinstance(clean_value, str) and len(clean_value) > 0 and column > 0:
            temp = clean_value
            if len(temp) > 0 and (temp[0] == "+" or temp[0] == "-"):
                temp = temp[1:]
            clean_value = convert_to_num(temp)

        if isinstance(clean_value, float):
            clean_value = int(clean_value)

        return clean_value

    return result


def convert_to_num(text: str) -> Union[int, float, str]:
    result = text

    if not result:
        result = 0
    elif result.isdigit():
        result = int(result)
    elif is_float(result):
        result = float(result)

    return result


def is_float(text: str) -> bool:
    match = re.match(r"^\d*\.\d*$", text.strip())
    return bool(match)
