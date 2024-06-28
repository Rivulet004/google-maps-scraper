from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


def get_element(driver, by, value):
    """
    Get the first element
    """
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except (NoSuchElementException, TimeoutException):
        print("No such element")
        return None
    

def get_element(driver, by, value):
    """
    Returns the the list of all the elements by value
    """

    try:
        list_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return list_elements
    except:
        print("elements not found")

@handle_stale_exception(3)
def get_element_text(self, by, value):
    if element := get_element(by, value):
        return element.text
    else:
        return None


@handle_stale_exception(3)
def get_website_url(self):
    if website_element := get_element(
        By.CSS_SELECTOR, "a.lcr4fd.S9kvJb[data-tooltip='Open website']"
    ):
        return website_element.text.get_attribute("href")
    else:
        return None


def scroll_click(driver, element, offset=0):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", element)


def scroll_screen(driver, until):
    driver.execute_script("arguments[0].scrollIntoView(true);", until)


def open_in_new_window(driver, url):
    driver.switch_to.new_window("window")
    driver.get(url)


def open_in_new_tab(driver, url):
    driver.switch_to.new_window("tab")
    driver.get(url)


def initialize_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_
    pass