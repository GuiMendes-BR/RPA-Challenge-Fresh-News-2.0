from RPA.Browser.Selenium import Selenium
from time import sleep


class BasePage(object):
    """Base class to initialize the base page that will be called from all
    pages"""

    URL = None

    def __init__(self, selenium: Selenium):
        self.selenium = selenium

        self._open()
        self._configure_selenium()

    def _open(self):
        self.selenium.open_chrome_browser(self.URL)
        self.selenium.maximize_browser_window()

    def _configure_selenium(self):
        # self.selenium.set_selenium_timeout(30)
        # self.selenium.set_browser_implicit_wait(30)
        self.selenium.set_selenium_implicit_wait(30)

    def click(self, locator: str) -> None:
        """ Performs click on web element whose locator is passed to it"""
        self.selenium.click_element_when_clickable(locator)
    
    def input_text(self, locator: str, text: str) -> None:
        """ Performs text entry of the passed in text, in a web element whose locator is passed to it"""
        self.selenium.input_text_when_element_is_visible(locator, text)

    def select(self, locator: str, text: str):
        self.selenium.select_from_list_by_label(locator, text)

    def get_text(self, locator: str):
        return self.selenium.get_text(locator)

    def exists(self, locator: str):
        return self.selenium.is_element_visible(locator)
    
    def press_key(self, locator: str, key) -> None:
        self.selenium.press_key(locator, key)

    def wait_page_load(self, wait_for = 30):
        page_state = None
        count = 0
        while page_state != 'complete':
            count +=1
            page_state = self.selenium.driver.execute_script('return document.readyState;')
            sleep(1)
            if count > wait_for:
                break

        return page_state == 'complete'
