import requests
from bs4 import BeautifulSoup
from sys import argv


def get_corona_info(countries) -> None:
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
    arg_length = len(countries)

    # Get all rows in the table after the header
    rows = soup.find_all('tr')[8:236]
    print()
    for row in rows:
        # Get every column of each row
        columns = row.find_all('td')

        # For when user wants to search for info on all countries
        if countries[0].lower() == 'all':
            print(
                f"Country: {columns[1].text} ({columns[0].text})\nNew Cases: {columns[3].text}\nNew Deaths: {columns[5].text}\nTotal Cases: {columns[2].text}\nTotal Deaths: {columns[4].text}\n")

        # When the iterated value matches one of the arguments
        elif columns[1].text in countries:
            print(
                f"Country: {columns[1].text} ({columns[0].text})\nNew Cases: {columns[3].text}\nNew Deaths: {columns[5].text}\nTotal Cases: {columns[2].text}\nTotal Deaths: {columns[4].text}\n")
            arg_length -= 1
            continue
        
        # Break the loop when the given list of countries is finished
        if arg_length < 1:
            break

if __name__ == "__main__":
    get_corona_info(argv)