from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class BasePage(object):
    """Base class to initialize the base page that will be called from all
    pages"""

    def __init__(self, driver: webdriver):
        self.driver = driver

    def click(self, by_locator: Tuple[str, By]) -> None:
        """ Performs click on web element whose locator is passed to it"""
        self.driver.find_element(*by_locator).click()
    
    def type_text(self, by_locator: Tuple[str, By], text: str) -> None:
        """ Performs text entry of the passed in text, in a web element whose locator is passed to it"""
        self.driver.find_element(*by_locator).send_keys(text)
    
    def exists(self, by_locator: Tuple[str, By]):
        try:
            self.driver.find_element(*by_locator)
        except NoSuchElementException:
            return False
        return True
    
    def send_keys(self, by_locator: Tuple[str, By], key) -> None:
        self.driver.find_element(*by_locator).send_keys(key)