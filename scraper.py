import time
import csv
import re
import urllib.parse
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)

from facebook_scraper import FacebookEmailScraper
from exception_handler import handle_stale_exception
from helper import timed
from color_and_styles import *

# Logger
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(f"logs/scraper_{timestamp}.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


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

    @timed()
    def open_google_maps(self):
        logger.info(f"Opening Google Maps for query: {self.query}")
        base_url = "https://www.google.com/maps/search/"
        encoded_url = urllib.parse.quote(self.query)
        url = base_url + encoded_url

        print(Yellow + f"Opening Google Maps for query: {self.query}" + Reset)
        try:
            self.driver.get(url)
            print(Green + "Google Maps opened" + Reset)
            logger.info(f"Google Maps opened: {self.query}")
        except Exception as e:
            logger.error(f"Failed to open Google Maps", exc_info=True)

    @timed()
    @handle_stale_exception(3)
    def scroll_to_load_all_listings(self):
        try:
            div_sidebar = self.driver.find_element(
                By.CSS_SELECTOR, f"div[aria-label='Results for {self.query}']"
            )
            keep_scrolling = True
            print(Yellow + "Scrolling through listings to load all results..." + Reset)
            logger.info(f"Scrolling through listings to load all results...")
            print(Bold + Red + "Warning: This will take a while" + Reset)
            logger.warning("This will take some time...")
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
            logger.info(f"All listings loaded: {self.query}")
        except NoSuchElementException:
            print(Red + Bold + "No listings loaded" + Reset)
            logger.error(f"No listings loaded: {self.query}")

    @timed()
    def retrieve_listings(self):
        print(f"Retrieving all listings for query: {self.query}")
        logger.info(f"Retrieving all listings for query: {self.query}")
        self.all_listings = self.driver.find_elements(By.CLASS_NAME, "hfpxzc")
        if self.all_listings:
            print(f"{len(self.all_listings)} listings retrieved")
            logger.info(
                f"{len(self.all_listings)} listings retrieved for the query: {self.query}"
            )
            self.counter = len(self.all_listings)
        else:
            print(Yellow + "No listings found" + Reset)
            logger.error(f"No listings found")

    @timed()
    def collect_listing_data(self):
        i = 1
        if not self.all_listings:
            self.print_no_listings_message()
            logger.error("No listings found to collect data from")
            return
        for listing in self.all_listings:
            self.initialize_location_data()
            self.print_collecting_message(i)
            logger.info(
                f"Collecting data for listing {i} out of {len(self.all_listings)}"
            )
            if not self.click_listing(listing):
                i += 1
                continue

            self.extract_listing_data()
            self.assign_collected_data()
            self.list_info.append(self.location_data)
            # self.check_for_duplicate(i - 1)
            self.print_collected_data_message(i)
            i += 1

    def print_no_listings_message(self):
        print(Red + "No listings found to collect data from." + Reset)

    def print_collecting_message(self, i):
        print(Yellow + f"Collecting data from listing {i}..." + Reset)

    def click_listing(self, listing):
        try:
            logger.info("Trying to click the listing")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", listing)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", listing)
            print(Green + "Element clicked" + Reset)
            logger.info("Listing Clicked")
            time.sleep(0.5)
            return True
        except ElementClickInterceptedException:
            print(
                Red + "Listing is not clickable. Skipping to the next listing." + Reset
            )
            return False

    def initialize_location_data(self):
        logger.info("Initializing location data")
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

    def clean_text(self, text, data_type="text"):
        """
        Cleans the given text based on the data type.

        Parameters:
        text (str): The text to be cleaned.
        data_type (str): The type of data ('location' or 'phone').

        Returns:
        str: The cleaned text.
        """
        if data_type == "location":
            # Remove unwanted characters for location
            cleaned_text = re.sub(r"[^\x00-\x7F]+", "", text)
        elif data_type == "phone":
            # Remove unwanted characters for phone number, keeping only digits and '+'
            cleaned_text = re.sub(r"[^\d+]", "", text)
        else:
            # Default cleaning (remove non-ASCII characters)
            cleaned_text = re.sub(r"[^\x00-\x7F]+", "", text)

        return cleaned_text.strip()

    def extract_listing_data(self):
        logger.info("Extracting Data form the listing")
        try:
            self.name = self.get_element_text(By.CSS_SELECTOR, ".DUwDvf.lfPIob", "Name")
            self.listing_url = self.driver.current_url
            self.type_of_business = self.get_element_text(
                By.CLASS_NAME, "DkEaL", "Type"
            )
            self.avg_rating = self.get_element_text(
                By.CSS_SELECTOR, ".F7nice > span > span[aria-hidden='true']", "Rating"
            )
            self.reviews_count = self.get_element_text(
                By.CSS_SELECTOR,
                ".F7nice > span > span > span[aria-label*='reviews']",
                "Total Reviewers",
            )
            self.address = self.get_element_text(
                By.CSS_SELECTOR, "[data-item-id='address']", "Address"
            )
            self.phone_number = self.get_element_text(
                By.CSS_SELECTOR, "[data-tooltip='Copy phone number']", "Number"
            )
            self.website_url = self.get_website_url()
            self.is_not_claimed = self.get_element(
                By.CSS_SELECTOR, "a[data-item-id='merchant'] .Io6YTe", "Unclaimed Text"
            )
            if self.website_url:
                if "www.facebook.com" in self.website_url:
                    self.email = self.fb_email_scraper.get_email(self.website_url)
                else:
                    self.email = "NA"
            else:
                self.email = "NA"
        except Exception as e:
            logger.error("Could not extract data from the listing", exc_info=True)

    def assign_collected_data(self):
        logger.info("Assigning Collected data to the dictionary")
        try:
            self.location_data["name"] = self.clean_text(self.name) if self.name else "NA"
            self.location_data["type"] = (
                self.clean_text(self.type_of_business) if self.type_of_business else "NA"
            )
            self.location_data["listing-url"] = (
                self.clean_text(self.listing_url) if self.listing_url else "NA"
            )
            self.location_data["rating"] = self.clean_text(self.avg_rating) if self.avg_rating else "NA"
            self.location_data["reviews_count"] = (
                self.clean_text(self.reviews_count) if self.reviews_count else "NA"
            )
            self.location_data["location"] = self.clean_text(self.address, "location") if self.address else "NA"
            self.location_data["contact"] = (
                self.clean_text(self.phone_number, "phone") if self.phone_number else "NA"
            )
            self.location_data["website"] = (
                self.clean_text(self.website_url) if self.website_url else "NA"
            )
            self.location_data["claimed"] = False if self.is_not_claimed else True
            self.location_data["email"] = self.email
        except Exception as e:
            logger.error("Could not assign collected data", exc_info=True)

    def get_element(self, by, value, element_name="not_specified"):
        logger.info(f"Trying to get {element_name}")
        if value == ".DUwDvf.lfPIob":
            try:
                element = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except (NoSuchElementException, TimeoutException) as e:
                print(Red + Bold + f"No such element Title not found" + Reset)
                logger.error("Name Element not found")
                return None
        else:
            try:
                return self.driver.find_element(by, value)
            except NoSuchElementException:
                print(Red + f"No such element, {element_name}" + Reset)
                logger.error(f"{element_name} Is not found in the listing")
                return None

    @handle_stale_exception(3)
    def get_element_text(self, by, value, element_name):
        if element := self.get_element(by, value, element_name):
            return element.text
        else:
            return None

    @handle_stale_exception(3)
    def get_website_url(self):
        if website_element := self.get_element(
            By.CSS_SELECTOR, "a.lcr4fd.S9kvJb[data-tooltip='Open website']", "Website"
        ):
            return website_element.get_attribute("href")
        else:
            return None

    def save_data_to_csv(self):
        print(Yellow + "Saving collected data to CSV file..." + Reset)
        logger.info("Writing Data to the .csv file")
        if not self.list_info:
            print(Red + "No data to write to CSV." + Reset)
            logger.error("No data to write to CSV.")
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
        logger.info("Data saved to the csv")

    def print_collected_data_message(self, i):
        logger.info(f"Collected data for {i}")
        print(Green + f"Collected data from listing {i}:" + Reset)

    def check_for_duplicate(self, index):
        if index != 0:
            print("Checking for duplicates")
            if self.list_info[index - 1] == self.location_data:
                print(Red + "Duplicate found" + Reset)
                listing = self.all_listings[index]
                if self.click_listing(listing):
                    self.initialize_location_data()
                    self.extract_listing_data()
                    self.assign_collected_data()

            if self.list_info[index]["name"] == self.location_data["name"]:
                print(Red + "Duplicate found" + Reset)
                listing = self.all_listings[index]
                if self.click_listing(listing):
                    self.initialize_location_data()
                    self.extract_listing_data()
                    self.assign_collected_data()
        else:
            return

    def get_duplicates(self):
        self.duplicate_index = set()
        print(Red + "Searching for duplicates" + Reset)
        logger.info(f"Searching for the duplicates for the query {self.query}")
        for i in range(len(self.list_info) - 1):
            for j in range(i + 1, len(self.list_info)):
                if self.list_info[i] == self.list_info[j]:
                    self.duplicate_index.add(j)
                if self.list_info[i]["name"] == self.list_info[j]["name"]:
                    self.duplicate_index.add(j)

        print(Red + f"{self.duplicate_index}")

    def resolve_duplicates(self):
        if self.duplicate_index:
            for i in self.duplicate_index:
                print(Red + Bold + Underline + f"Resolving duplicate {i + 1}" + Reset)
                logger.info(f"Resolving Duplicate {i + 1}")
                listing = self.all_listings[i]
                self.print_collecting_message(i + 1)
                if not self.click_listing(listing):
                    print(
                        Red
                        + Bold
                        + Underline
                        + f"Could not resolve as this duplicate"
                        + Reset
                    )
                    continue
                self.initialize_location_data()
                self.extract_listing_data()
                self.assign_collected_data()
                self.list_info[i] = self.location_data
                print(
                    Green
                    + Bold
                    + Underline
                    + f"Resolved this Duplicate: {i + 1}"
                    + Reset
                )
                self.print_collected_data_message(i + 1)
        else:
            print(Green + Bold + "No Duplicates Found <:-)" + Reset)
            logger.info("No Duplicates Found")

    def close_browser(self):
        print(Yellow + "Closing the browser..." + Reset)
        logger.info("Closing the browser")
        try:
            self.driver.quit()
            print(Green + "Browser closed" + Reset)
            logger.info("Browser Closed")
        except:
            logger.error("Could not close the browser", exc_info=True)
