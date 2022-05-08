#!/bin/bash

printf "Creating a virtual environment...\n"
python3 -m venv corona
printf "Virtual environment created.\n"
source corona/bin/activate
printf "\nInstalling dependencies...\n"
pip install requests beautifulsoup4
printf "Dependencies installed.\n"

printf "\nDon't forget to run 'source corona/bin/activate' before running the script!\n"