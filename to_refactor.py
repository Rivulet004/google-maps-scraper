import sys
import pyperclip
import os
import time
import csv
import urllib.parse
from facebook_scraper import FacebookEmailScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)

# Color and Styles for the output

Red = "\033[31m"
Green = "\033[32m"
Yellow = "\033[33m"
Blue = "\033[34m"
Magenta = "\033[35m"
Cyan = "\033[36m"
White = "\033[37m"
Reset = "\033[0m"
Bold = "\x1b[1m"
Underline = "\x1b[4m"
blink = "\x1b[5m"
reverse = "\x1b[7m"


class ScrapGoogleMap:
    def __init__(self, query, location, business_type):
        self.query = query
        self.location = location
        self.type = business_type
        self.driver = webdriver.Firefox()
        self.all_listings = []
        self.list_info = []
        self.location_data = {}
        self.counter = 0
        self.fb_email_scraper = FacebookEmailScraper(self.driver)

    def open_google_maps(self):
        base_url = "https://www.google.com/maps/search/"
        encoded_url = urllib.parse.quote(self.query)
        url = base_url + encoded_url

        print(Yellow + f"Opening Google Maps for query: {self.query}" + Reset)
        self.driver.get(url)
        print(Green + "Google Maps opened" + Reset)

    def scroll_to_load_all_listings(self):
        try:
            div_sidebar = self.driver.find_element(
                By.CSS_SELECTOR, f"div[aria-label='Results for {self.query}']"
            )
            keep_scrolling = True
            print(Yellow + "Scrolling through listings to load all results..." + Reset)
            print(Bold + Red + "Warning: This will take a while" + Reset)
            while keep_scrolling:
                div_sidebar.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
                div_sidebar.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
                html = self.driver.find_element(By.TAG_NAME, "html").get_attribute(
                    "outerHTML"
                )
                if "You've reached the end of the list." in html:
                    keep_scrolling = False
            print(Green + "All listings loaded" + Reset)
        except NoSuchElementException:
            print(Red + Bold + "No listings loaded" + Reset)

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
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", listing)

                # add time for the listing to load
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
                "email": "NA",
                "listing-url": "NA",
                "rating": "NA",
                "reviews_count": "NA",
                "location": "NA",
                "contact": "NA",
                "website": "NA",
                "claimed": "NA",
            }

            # Collect Data
            try:
                name = self.driver.find_element(By.CSS_SELECTOR, ".DUwDvf.lfPIob")
            except NoSuchElementException:
                name = None

            try:
                listing_url = self.driver.current_url
            except NoSuchElementException:
                listing_url = None

            try:
                type_of_business = self.driver.find_element(By.CLASS_NAME, "DkEaL")
            except NoSuchElementException:
                type_of_business = None

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
                try:
                    website_url = website_element.get_attribute("href")
                except StaleElementReferenceException:
                    website_url = "Stale Exception"
            except NoSuchElementException:
                website_url = "NA"

            try:
                is_not_claimed = self.driver.find_element(
                    By.CSS_SELECTOR, "a[data-item-id='merchant'] .Io6YTe"
                )
            except NoSuchElementException:
                is_not_claimed = None

                if "www.facebook.com" in website_url:
                    email = self.fb_email_scraper.get_email(website_url)
                    self.location_data["email"] = email
                else:
                    self.location_data["email"] = "NA"

            # Assign Collected Data
            try:
                self.location_data["name"] = name.text if name else "NA"
                self.location_data["type"] = (
                    type_of_business.text if type_of_business else "NA"
                )
                self.location_data["listing-url"] = listing_url if listing_url else "NA"
                self.location_data["rating"] = avg_rating.text if avg_rating else "NA"
                self.location_data["reviews_count"] = (
                    total_reviews.text[1:-1] if total_reviews else "NA"
                )
                self.location_data["location"] = address.text if address else "NA"
                self.location_data["contact"] = phone_number.text if phone_number else "NA"
                self.location_data["website"] = website_url if website_url else "NA"
                self.location_data["claimed"] = False if is_not_claimed else True
            except StaleElementReferenceException:
                print(Bold + "Error: Stale Error")
                pass

            self.list_info.append(self.location_data)
            print(Green + f"Collected data from listing {i}:" + Reset)
            print(Blue + f"{self.location_data}" + Reset)

            # if i == 2:
            #     break
            i += 1

    def save_data_to_csv(self):
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