import sys
import pyperclip
import os
from scraper import ScrapGoogleMap

from color_and_styles import *


def main():
    if len(sys.argv) > 1:
        location = " ".join(sys.argv[1:])
    else:
        location = pyperclip.paste()

    # Check if the directory exists to save file if not then create the directory
    if not os.path.exists(f"data/{location}"):
        os.makedirs(f"data/{location}")

    with open("business_list.txt", "r") as file:
        business_list = file.readlines()

    cleaned_business_list = [entry.strip() for entry in business_list]
    total_counter = 0

    for business_type in cleaned_business_list:
        query = f"{business_type} in {location}"
        print(
            Cyan
            + "<――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――>"
            + Reset
        )
        print(Magenta + f"Initializing Scraper for the query: {query}" + Reset)
        scraper = ScrapGoogleMap(query, location, business_type)
        print(Green + f"Scraper initialized" + Reset)
        scraper.open_google_maps()
        scraper.scroll_to_load_all_listings()
        scraper.retrieve_listings()
        total_counter += scraper.counter
        scraper.collect_listing_data()
        scraper.save_data_to_csv()
        scraper.close_browser()
        print(Green + f"Data Scraped for the query: {query}" + Reset)
        print(Red + f"total entries as of yet {total_counter}" + Reset)
        print(
            Cyan
            + "<――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――>"
            + Reset
        )

    print(Yellow + "Terminating Program" + Reset)
    print(Red + "Program Terminated Successfully" + Reset)


if __name__ == "__main__":
    main()
