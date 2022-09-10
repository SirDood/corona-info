from dataclasses import dataclass
from enum import auto

from coronainfo.models.model_base import BaseData, BaseEnum


@dataclass
class CoronaData(BaseData):
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


class CoronaHeaders(BaseEnum):
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
