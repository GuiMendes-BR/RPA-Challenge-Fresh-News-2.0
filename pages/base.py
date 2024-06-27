from RPA.Browser.Selenium import Selenium
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from config import config



class BasePage(object):
    """Base class to initialize the base page that will be called from all
    pages"""

    URL = None

    def __init__(self, selenium: Selenium):
        
        self.selenium = selenium
        self.explicit_wait_timeout = config['seleniumWaitTimeOut']

        self._open()
        self._configure_selenium()

    def _open(self):
        """Opens a new browser window with the URL specified in self.URL"""
        
        
        self.selenium.open_chrome_browser(self.URL)
        self.selenium.maximize_browser_window()

    def _configure_selenium(self):
        """Sets selenium implicit wait to value in config """
        self.selenium.set_selenium_implicit_wait(config['seleniumWaitTimeOut'])

    @property
    def wait(self) -> WebDriverWait:
        """WebDriverWait object to avoid repetition """
        return WebDriverWait(self.selenium.driver, self.explicit_wait_timeout)

    def click(self, by_locator) -> None:
        """Performs click on web element whose by_locator is passed to it"""
        element = self.wait.until(EC.element_to_be_clickable(by_locator))
        self.selenium.click_element_when_clickable(element)
        
    
    def input_text(self, by_locator, text: str) -> None:
        """Performs text entry of the passed in text, in a web element whose by_locator is passed to it"""
        element = self.wait.until(EC.presence_of_element_located(by_locator))
        self.selenium.input_text(element, text)

    def select(self, by_locator, text: str):
        """Selects from a dropdown the text passed to is"""
        element = self.wait.until(EC.presence_of_element_located(by_locator))
        self.selenium.select_from_list_by_label(element, text)

    def get_text(self, by_locator):
        """Reads text from web element"""
        element = self.wait.until(EC.presence_of_element_located(by_locator))
        return self.selenium.get_text(element)

    def exists(self, by_locator):
        """Checks the existence of and element after timeout period"""
        try:
            self.wait.until(EC.presence_of_element_located(by_locator))
            return True
        except TimeoutError as err:
            return False
    
    def press_key(self, by_locator, key) -> None:
        """Sends a special Key to element"""
        element = self.wait.until(EC.presence_of_element_located(by_locator))
        self.selenium.press_key(element, key)

    def wait_page_load(self, wait_for = 30):
        """Waits for page load"""
        page_state = None
        count = 0
        while page_state != 'complete':
            count +=1
            page_state = self.selenium.driver.execute_script('return document.readyState;')
            sleep(1)
            if count > wait_for:
                break

        return page_state == 'complete'
