import os

import requests
from bs4 import BeautifulSoup

from helpers import get_cache_dir


class CoronaModel:
    def __init__(self):
        pass

    def fetch_data(self) -> str:
        """Fetches raw html data from `https://www.worldometers.info/coronavirus/`.

        This function fetches the raw html data from `https://www.worldometers.info/coronavirus/` and 
        parses it to get the table which shows data from the current date.

        Returns
        -------
        str
            A string of the raw html table body data.
        """

        url = "https://www.worldometers.info/coronavirus/"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")

        # Find the 'today' table
        table = soup.find(id="main_table_countries_today")
        table_body = table.find("tbody")

        return str(table_body)

    def parse_raw_data(self, soup: BeautifulSoup) -> list[str]:
        """Parses raw html table body for data.

        Parameters
        ----------
        soup : BeautifulSoup
            A BeautifulSoup object, assumed to be the body of the table.

        Returns
        -------
        list[str]
            A list of strings which contain the sanitised data of all available countries.
        """

        countries = soup.find_all("tr")[7:]

        # Get content of each column
        result = []
        for country in countries:
            country_data = country.find_all("td")[:15]

            clean_data = []
            for i, data in enumerate(country_data, 0):
                value = data.text.replace(",", "").strip()

                # For World, "No." is just nothing, so this is to assign it 0
                if not i and not value:
                    value = "0"

                clean_data.append(value)

            result.append(",".join(clean_data))

        return result

    def get_table_headers(self) -> list[str]:
        headers = [
            "No.",
            "Country",
            "Total Cases",
            "New Cases",
            "Total Deaths",
            "New Deaths",
            "Total Recovered",
            "New Recovered",
            "Active Cases",
            "Serious",
            "Total Cases/1M",
            "Deaths/1M",
            "Total Tests",
            "Tests/1M",
            "Population"
        ]

        return headers


if __name__ == "__main__":
    corona = CoronaModel()
    # corona.fetch_data()
    with open(get_cache_dir("raw"), "r") as file:
        raw_data = file.read()
    soup = BeautifulSoup(raw_data, "html.parser")
    corona.parse_raw_data(soup)
