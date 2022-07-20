import requests
from bs4 import BeautifulSoup


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

    def parse_raw_data(self, content: str = None) -> list[str]:
        """Parses raw html table body for data.

        Parameters
        ----------
        content: str | None
            A string that will be parsed for data.

        Returns
        -------
        list[str]
            A list of strings which contain the sanitised data of all available countries.
        """
        soup = BeautifulSoup(content, "html.parser")
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

    def parse_clean_data(self, content: str = None, delimiter: str = "\n") -> list[tuple]:
        r"""
        Parses csv-like file for data.

        Parameters
        ----------
        content: str | None
            A string that will be parsed for data.

        delimiter: str
            The delimiter that will be used to split the data. Defaults to '\n'

        Returns
        -------
        list[tuple]
            A list of tuples which contain clean data of all available countries.
        """
        countries_data = content.split(delimiter)
        result = []
        for row_data in countries_data:
            data_tuple = tuple(row_data.split(","))
            result.append(data_tuple)

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
    print(corona.parse_clean_data())
