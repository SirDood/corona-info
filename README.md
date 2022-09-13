# WORK IN PROGRESS. THIS README IS VERY OUTDATED

# Covid Scrapper

A simple web scraping project that scrapes [Worldometer](https://www.worldometers.info/coronavirus/ "Worldometer") for
basic information on Covid-19 cases. The program is a command line Python program that accepts any number of countries
as arguments, besides China for reasons that are beyond me. This program was created 2 years ago, but I recently decided
to push my old projects to GitHub.

### Developed on:

- Linux Mint 20.3 with 5.16.15 kernel
- Python 3.10.4

## Setting up

1. Make sure that you have Python installed. I'm not sure which versions are compatible with it, but just
   use `Python 3.10.4` to be safe.
2. On the terminal, clone this repo via `git clone https://github.com/SirDood/corona-info.git`
3. Enter the repo and setup the project via `cd corona-info && ./setup_unix.sh`
4. Activate the newly created Python virtual environment via `source corona/bin/activate`

## Using the program

The program is very simple to use, as shown by the syntax below:

`python3 coronainfo.py country1 country2 country3 ...`
