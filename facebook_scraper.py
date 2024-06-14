import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FacebookEmailScraper:
    def __init__(self, driver):
        self.driver = driver

    def get_email(self, facebook_url):
        original_window = self.driver.current_window_handle

        # Open the new tab
        if "www.facebook.com" in facebook_url:
            self.driver.switch_to.new_window("tab")
            if facebook_url[-1] == "/":
                facebook_url = facebook_url + "about"
            else:
                facebook_url = facebook_url + "/about"

            self.driver.get(facebook_url)
            time.sleep(0.5)

            # Close popup
            try:
                popup = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Close']"))
                )
                # popup = self.driver.find_element(By.XPATH, "//div[@aria-label='Close']")
                popup.click()
                time.sleep(0.5)
            except TimeoutException:
                pass

            # Scrape Email
            try:
                email_element = self.driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/div/div[4]/div/div/div[2]/ul/li/div/div/div[1]/span"
                )
                email = email_element.text
            except NoSuchElementException:
                print("Can't find email")
                email = None

            self.driver.close()
            self.driver.switch_to.window(original_window)
            print(email)

            return email
        else:
            return None