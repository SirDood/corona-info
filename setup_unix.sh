#!/bin/bash

printf "Creating a virtual environment...\n"
python3 -m venv venv
printf "Virtual environment created.\n"
source venv/bin/activate
printf "\nInstalling dependencies...\n"
pip install requests beautifulsoup4
printf "Dependencies installed.\n"

printf "\nDon't forget to run 'source venv/bin/activate' before running the script!\n"
