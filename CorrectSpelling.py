import requests
from bs4 import BeautifulSoup
import MedicineWebScraping
import re

def main(medicine_name_query):
    allowed_symbols = "-'[]{}+&.()/,0123456789"

    pattern = f'[^a-zA-Z\s{re.escape(allowed_symbols)}]'

    # Remove special symbols except the allowed ones
    medicine_name_query = re.sub(pattern, '', medicine_name_query)
    print(f"Removes symbols: {medicine_name_query}")

    correctName = MedicineWebScraping.correct_spelling(medicine_name_query)

    print(f"Browser Return: {correctName}")

    if "No suggestion found for" not in correctName:
        correctName = correctName.replace(" medicine used for?","")
        medicine_name_query = correctName.strip()
    print(type(medicine_name_query))
    print(f"Spell correction: {medicine_name_query}")
    medicine_name_query = medicine_name_query.title()
    print(f"TitleCase: {medicine_name_query}")

    return medicine_name_query



