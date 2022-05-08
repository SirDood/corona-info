import requests
from bs4 import BeautifulSoup


def get_corona_info(*args) -> None:
    """
    Prints some information on Covid-19 cases in the country(s) given in the following format:

    Country: COUNTRY_NAME (RANK)
    New Cases: xxx
    New Deaths: xxx
    Total Cases: xxx
    Total Deaths: xxx 
    """

    # Define and initialise variables
    url = "https://www.worldometers.info/coronavirus/"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    # Get all rows in the table after the header
    rows = soup.find_all('tr')[8:236]
    print()
    for row in rows:
        # Get every column of each row
        columns = row.find_all('td')

        # For when user wants to search for info on all countries
        if args[0].lower() == 'all':
            print(
                f"Country: {columns[1].text} ({columns[0].text})\nNew Cases: {columns[3].text}\nNew Deaths: {columns[5].text}\nTotal Cases: {columns[2].text}\nTotal Deaths: {columns[4].text}\n")

        # When the iterated value matches one of the arguments
        elif columns[1].text in args:
            print(
                f"Country: {columns[1].text} ({columns[0].text})\nNew Cases: {columns[3].text}\nNew Deaths: {columns[5].text}\nTotal Cases: {columns[2].text}\nTotal Deaths: {columns[4].text}\n")


if __name__ == '__main__':
    get_corona_info("Malaysia")
