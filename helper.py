from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from exception_handler import handle_stale_exception


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
