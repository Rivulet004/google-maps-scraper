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
        self.driver = webdriver.Firefox()
        self.all_listings = []
        self.list_info = []
        self.location_data = {}

    def open_google_maps(self):
        url = "https://www.google.com/maps/search/"
        split = self.query.split()
        url = url + split[0]
        for i in range(1, len(split)):
            url += f"+{split[i]}"

        print(f"Opening Google Maps for query: {self.query}")
        self.driver.get(url)
        print("Google Maps opened")

    def scroll_to_load_all_listings(self):
        div_sidebar = self.driver.find_element(
            By.CSS_SELECTOR, f"div[aria-label='Results for {self.query}']"
        )
        keepScrolling = True
        print("Scrolling through listings to load all results", end="")
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
        print("All listings loaded")

    def retrieve_listings(self):
        print(f"Retrieving all listings for query: {self.query}")
        self.all_listings = self.driver.find_elements(By.CLASS_NAME, "hfpxzc")
        if self.all_listings:
            print(f"{len(self.all_listings)} listings retrieved")
        else:
            print("No listings found")

    def collect_listing_data(self):
        i = 1
        if not self.all_listings:
            print("No listings found to collect data from.")
            return
        for listing in self.all_listings:
            print(f"Collecting data from listing {i}...")
            listing.click()
            time.sleep(1)

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
                website = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-item-id='authority']"
                )
            except NoSuchElementException:
                website = None

            try:
                isNotClaimed = self.driver.find_element(
                    By.CSS_SELECTOR, "a[data-item-id='merchant'] .Io6YTe"
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
            print(f"Collected data from listing {i}: {self.location_data}")
            i += 1

    def save_data_to_csv(self):
        print("Saving collected data to CSV file...")
        if not self.list_info:
            print("No data to write to CSV.")
            return
        with open(
            f"data/{self.query}.csv", mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=self.list_info[0].keys())

            writer.writeheader()

            for row in self.list_info:
                writer.writerow(row)
        print(f"Data saved to {self.query}.csv successfully.")

    def close_browser(self):
        print("Closing the browser...")
        self.driver.quit()
        print("Browser closed")


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = pyperclip.paste()

    scraper = ScrapGoogleMap(query)
    scraper.open_google_maps()
    scraper.scroll_to_load_all_listings()
    scraper.retrieve_listings()
    scraper.collect_listing_data()
    scraper.save_data_to_csv()
    scraper.close_browser()


if __name__ == "__main__":
    main()
