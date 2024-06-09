#! python3
# scrap.py

import sys, pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import csv


class ScrapGoogleMap:

    def __init__(self, query):
        self.query = query
        self.driver = webdriver.Firefox()  # browser
        self.all_listings = []  # to get all the listings
        self.list_info = []  # to store the dictionary of each listing
        self.location_data = (
            {}
        )  # dictionary for temporarily storing data of the listing before being parsed to the self.list_info

    def open_webpage(self):
        url = "https://www.google.com/maps/search/"

        # Convert the queary that user provied into URL that can be searched
        split = self.query.split()
        url = url + split[0]
        for i in range(1, len(split)):
            url += f"+{split[i]}"

        # Open firefox browser
        print("opening firefox at: ")
        print(url)
        self.driver.get(url)
        print("firefox opened")

    def scroll_to_bottom(self):
        div_sidebar = self.driver.find_element(
            By.CSS_SELECTOR, f"div[aria-label='Results for {self.query}']"
        )

        # Scrolling to the bottom of Page
        keepScrolling = True
        print("Scrolling to bottom to load all listing because of AJAX")
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
        print("Scrolled to Bottom")

    def retrieve_listing(self):
        print("Retrieving Listings")
        self.all_listings = self.driver.find_elements(By.CLASS_NAME, "hfpxzc")
        if self.all_listings:
            print(f"{len(self.all_listings)} listings retrieved")
        else:
            print("NO listings found")

    def collect_data(self):
        i = 1
        if not self.all_listings:
            print("no data to collect as no listings are found")
            return
        for listing in self.all_listings:
            print(f"Collecting data of list no. {i}")
            listing.click()
            time.sleep(3)   # Delay for the list to load

            self.location_data = {
                "name": "NA",
                "type": "NA",
                "rating": "NA",
                "reviews_count": "NA",
                "location": "NA",
                "contact": "NA",
                "website": "NA",
                "isClaimed": False,
            }

            try:
                name = self.driver.find_element(By.CSS_SELECTOR, ".DUwDvf.lfPIob")
            except NoSuchElementException:
                name = None

            try:
                type = self.driver.find_element(By.CLASS_NAME, "DkEaL")
            except NoSuchElementException:
                type = None

            try:
                avg_rating = self.driver.find_element(
                    By.CLASS_NAME, "section-star-display"
                )
            except NoSuchElementException:
                avg_rating = None

            try:
                total_reviews = self.driver.find_element(
                    By.CLASS_NAME, "section-rating-term"
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
                website = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-item-id='authority']"
                )
            except NoSuchElementException:
                website = None

            try:
                isNotClaimed = self.driver.find_element(
                    By.CSS_SELECTOR, "div[aria-label='Claim this business']"
                )
            except NoSuchElementException:
                isNotClaimed = None

            self.location_data["name"] = name.text if name else "NA"
            self.location_data["type"] = type.text if type else "NA"
            self.location_data["rating"] = avg_rating.text if avg_rating else "NA"
            self.location_data["reviews_count"] = (
                total_reviews.text[1:-1] if total_reviews else "NA"
            )
            self.location_data["location"] = address.text if address else "NA"
            self.location_data["contact"] = phone_number.text if phone_number else "NA"
            self.location_data["website"] = website.text if website else "NA"
            self.location_data["isClaimed"] = False if isNotClaimed else True

            self.list_info.append(self.location_data)
            print(f"Collected data of list no. {i}")
            print(self.location_data)
            if i == 1:
                print("breaking only in testing phase")
                break
            i += 1

    def extract_data(self):
        print("Converting collected data into a CSV file")
        if not self.list_info:
            print("No data to write to CSV")
            return
        with open(f"data/{self.query}.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.list_info[0].keys())

            writer.writeheader()

            for row in self.list_info:
                writer.writerow(row)
        print("Converted all data to the CSV file")

    def close_borwser(self):
        print("Closing Browser")
        self.driver.quit()
        print("Browser Closed")


def main():
    if (len(sys.argv)) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = pyperclip.paste()

    scraper = ScrapGoogleMap(query)
    scraper.open_webpage()
    # scraper.scroll_to_bottom() just for testing
    scraper.retrieve_listing()
    scraper.collect_data()
    scraper.extract_data()
    scraper.close_borwser()


if __name__ == "__main__":
    main()
