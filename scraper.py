import sys, pyperclip, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)
import time
import csv


# Color to Stylize output

Red = "\033[31m"
Green = "\033[32m"
Yellow = "\033[33m"
Blue = "\033[34m"
Magenta = "\033[35m"
Cyan = "\033[36m"
White = "\033[37m"
Reset = "\033[0m"


class ScrapGoogleMap:
    def __init__(self, query, location, type):
        self.query = query
        self.location = location
        self.type = type
        self.driver = webdriver.Firefox()
        self.all_listings = []
        self.list_info = []
        self.location_data = {}
        self.counter = 0

    def open_google_maps(self):
        url = "https://www.google.com/maps/search/"

        # Create a searchable url by the browser
        split = self.query.split()
        url = url + split[0]  # initialize the url to avoid the + sign in the start
        for i in range(1, len(split)):
            url += f"+{split[i]}"

        print(Yellow + f"Opening Google Maps for query: {self.query}" + Reset)
        self.driver.get(url)
        print(Green + "Google Maps opened" + Reset)

    def scroll_to_load_all_listings(self):
        div_sidebar = self.driver.find_element(
            By.CSS_SELECTOR, f"div[aria-label='Results for {self.query}']"
        )
        keepScrolling = True
        print(Yellow + "Scrolling through listings to load all results..." + Reset)
        while keepScrolling:
            div_sidebar.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            div_sidebar.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            html = self.driver.find_element(By.TAG_NAME, "html").get_attribute(
                "outerHTML"
            )
            if "You've reached the end of the list." in html:
                keepScrolling = False
        print(Green + "All listings loaded" + Reset)

    def retrieve_listings(self):
        print(f"Retrieving all listings for query: {self.query}")
        self.all_listings = self.driver.find_elements(By.CLASS_NAME, "hfpxzc")
        if self.all_listings:
            print(f"{len(self.all_listings)} listings retrieved")
            self.counter += len(self.all_listings)
        else:
            print(Yellow + "No listings found" + Reset)

    def collect_listing_data(self):
        i = 1
        if not self.all_listings:
            print(Red + "No listings found to collect data from." + Reset)
            return
        for listing in self.all_listings:
            print(Yellow + f"Collecting data from listing {i}..." + Reset)

            # Using JS to clink the element
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", listing
                )
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", listing)

                # add time for the lisitng to load
                time.sleep(0.3)

            except ElementClickInterceptedException:
                print(
                    Red
                    + f"Listing {i} is not clickable. Skipping to the next listing."
                    + Reset
                )
                i += 1
                continue

            self.location_data = {
                "name": "NA",
                "type": "NA",
                "listing-url": "NA",
                "rating": "NA",
                "reviews_count": "NA",
                "location": "NA",
                "contact": "NA",
                "website": "NA",
                "claimed": False,
            }

            try:
                name = self.driver.find_element(By.CSS_SELECTOR, ".DUwDvf.lfPIob")
            except NoSuchElementException:
                name = None

            try:
                listing_url = self.driver.current_url
            except NoSuchElementException:
                listing_url = None

            try:
                type = self.driver.find_element(By.CLASS_NAME, "DkEaL")
            except NoSuchElementException:
                type = None

            try:
                avg_rating = self.driver.find_element(
                    By.CSS_SELECTOR, ".F7nice > span > span[aria-hidden='true']"
                )
            except NoSuchElementException:
                avg_rating = None

            try:
                total_reviews = self.driver.find_element(
                    By.CSS_SELECTOR,
                    ".F7nice > span > span > span[aria-label*='reviews']",
                )
            except NoSuchElementException:
                total_reviews = None

            try:
                address = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-item-id='address']"
                )
            except NoSuchElementException:
                address = None

            try:
                phone_number = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-tooltip='Copy phone number']"
                )
            except NoSuchElementException:
                phone_number = None

            try:
                website_element = self.driver.find_element(
                    By.CSS_SELECTOR, "a.lcr4fd.S9kvJb[data-tooltip='Open website']"
                )
                website_url = website_element.get_attribute("href")
            except NoSuchElementException:
                website_url = "NA"

            try:
                isNotClaimed = self.driver.find_element(
                    By.CSS_SELECTOR, "a[data-item-id='merchant'] .Io6YTe"
                )
            except NoSuchElementException:
                isNotClaimed = None

            self.location_data["name"] = name.text if name else "NA"
            self.location_data["type"] = type.text if type else "NA"
            self.location_data["listing-url"] = listing_url if listing_url else "NA"
            self.location_data["rating"] = avg_rating.text if avg_rating else "NA"
            self.location_data["reviews_count"] = (
                total_reviews.text[1:-1] if total_reviews else "NA"
            )
            self.location_data["location"] = address.text if address else "NA"
            self.location_data["contact"] = phone_number.text if phone_number else "NA"
            self.location_data["website"] = website_url if website_url else "NA"
            self.location_data["claimed"] = False if isNotClaimed else True

            self.list_info.append(self.location_data)
            print(Green + f"Collected data from listing {i}:" + Reset)
            print(Blue + f"{self.location_data}" + Reset)

            # if i == 2:
            #     break
            i += 1

    def save_data_to_csv(self):
        print(Yellow + "Saving collected data to CSV file..." + Reset)
        if not self.list_info:
            print(Red + "No data to write to CSV." + Reset)
            return
        with open(
            f"data/{self.location}/{self.query}.csv",
            mode="w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(file, fieldnames=self.list_info[0].keys())

            writer.writeheader()

            for row in self.list_info:
                writer.writerow(row)
        print(Green + f"Data saved to {self.query}.csv successfully." + Reset)

    def close_browser(self):
        print(Yellow + "Closing the browser..." + Reset)
        self.driver.quit()
        print(Green + "Browser closed" + Reset)


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

    for type in cleaned_business_list:

        query = f"{type} in {location}"
        print(
            Cyan
            + "<――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――>"
            + Reset
        )
        print(Magenta + f"Initializing Scraper for the query: {query}" + Reset)
        scraper = ScrapGoogleMap(query, location, type)
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
    print(Red + "Program Terminated Sucessfully" + Reset)


if __name__ == "__main__":
    main()
