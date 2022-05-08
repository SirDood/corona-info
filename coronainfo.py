import requests
from bs4 import BeautifulSoup

url = "https://www.worldometers.info/coronavirus/"
req = requests.get(url)
soup = BeautifulSoup(req.text, 'html.parser')


def get_corona_info(*args):

    try:
        rows = soup.find_all('tr')[8:]
        for row in rows:
            columns = row.find_all('td')
            if args[0].lower() == 'all':
                print()
                print(
                    f"Country: {columns[1].text} ({columns[0].text})\nNew Cases: {columns[3].text}\nNew Deaths: {columns[5].text}\nTotal Cases: {columns[2].text}\nTotal Deaths: {columns[4].text}\n")

            elif columns[1].text in args:
                print()
                print(
                    f"Country: {columns[1].text} ({columns[0].text})\nNew Cases: {columns[3].text}\nNew Deaths: {columns[5].text}\nTotal Cases: {columns[2].text}\nTotal Deaths: {columns[4].text}\n")

    except:
        pass

if __name__ == '__main__':
    get_corona_info("Malaysia")
