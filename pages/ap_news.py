from selenium.webdriver.common.by import By
from pages.base import BasePage
from selenium.webdriver.common.keys import Keys

class ApNewsPage(BasePage):

    # Configuração
    URL = "https://apnews.com/"

    def open(self):
        self.driver.get(self.URL)
        self.driver.maximize_window()

    def search_keyword(self, keyword):
        self.click(ApNewsLocators.SEARCH_BUTTON)
        self.type_text(ApNewsLocators.INPUT_SEARCH, keyword)
        self.send_keys(ApNewsLocators.INPUT_SEARCH, Keys.RETURN)

    def search_category(self, category):
        assert category != "", "Category cannot be empty"

        self.click(ApNewsLocators.CATEGORY_DROP_DOWN)


        # Capitalize category
        if self.exists(ApNewsLocators.CATEGORY(category)):
            self.click(ApNewsLocators.CATEGORY(category))
        else:
            raise AssertionError("Category not found")
        
  
class ApNewsLocators():
    SEARCH_BUTTON = (By.XPATH, '//button[@class="SearchOverlay-search-button"]')
    INPUT_SEARCH = (By.XPATH, '//input[@class="SearchOverlay-search-input"]')
    CATEGORY_DROP_DOWN = (By.XPATH, '//div[@class="SearchFilter-heading"]')

    def CATEGORY(category):
        return (By.XPATH, f'//div[@class="CheckboxInput"]/label/span[contains(text(), "{category}")]')

