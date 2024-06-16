from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
from exception_handler import handle_stale_exception
from color_and_styles import *


def timed():
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            time_taken = end - start
            rounded_time = round(time_taken, 2)
            print(Cyan + Magenta + Red + f"Time Taken:  {rounded_time} secs" + Reset)
            return rounded_time

        return wrapper

    return decorator


def get_element(self, by, value):
    try:
        return self.driver.find_element(by, value)
    except NoSuchElementException:
        print('No such element')
        return None


def get_element_text(self, by, value):
    if element := get_element(by, value):
        return element.text
    else:
        return None


@handle_stale_exception(3)
def get_website_url(self):
    if website_element := get_element(By.CSS_SELECTOR, "a.lcr4fd.S9kvJb[data-tooltip='Open website']"):
        return website_element.text.get_attribute('href')
    else:
        return None
