from selenium.webdriver.common.by import By
from pages.base import BasePage
from selenium.webdriver.common.keys import Keys
from pydantic import BaseModel, PositiveInt
import datetime
from dateutil.relativedelta import relativedelta
import requests
import time
from bs4 import BeautifulSoup
import re


class News(BaseModel):
    title: str  
    date: datetime.datetime # December 14, 2023
    description: str | None
    picture: str | None

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

        # Capitalize every word in category to match ApNews
        category = category.title()
        if self.exists(ApNewsLocators.CATEGORY(category)):
            self.click(ApNewsLocators.CATEGORY(category))
            # Wait for page to load
            self.exists(ApNewsLocators.SELECTED_FILTERS_LABEL)
            
        else:
            raise AssertionError("Category not found")
        
    def sort_by(self, text):
        self.select(ApNewsLocators.SORT_BY_SELECT, text)
        time.sleep(3)

    def _convert_date(self, date):
        # convert date from string to object
        if re.match(r"\d+ hours? ago", date):
            delta = int(re.match(r"\d+", date)[0])
            date = datetime.datetime.today() - datetime.timedelta(hours=delta)
        elif date == "Yesterday":
            delta = 1
            date = datetime.datetime.today() - datetime.timedelta(days=delta)
        elif re.match(r"\w+ \d{1,2}, \d{4}", date):
            date = datetime.datetime.strptime(date, "%B %d, %Y")
        elif re.match(r"\w+ \d{1,2}", date):
            date = f"{date}, {datetime.date.today().year}"
            date = datetime.datetime.strptime(date, "%B %d, %Y")
        else:
            raise KeyError(f"Could not convert string to date {date}")
        
        return date

    def _download_picture(self, picture, title):
        # Download picture
        image_name = "".join(x for x in title if x.isalnum() or x == " ")
        image_name = f"{image_name}.jpg"

        image_data = requests.get(picture).content
        with open(f'output/pictures/{image_name}', 'wb') as handler:
            handler.write(image_data)

        return image_name


    def scrape_news(self, months_to_extract):
        if months_to_extract == 0: months_to_extract = 1

        cutoff_date = datetime.datetime.now() - relativedelta(months=months_to_extract)

        all_news = []

        current_page = 0
        continue_paginating = True

        current_page, total_pages = self.read_text(ApNewsLocators.PAGINATION_COUNT).split(' of ')
        current_page, total_pages = int(current_page), int(total_pages)

        while continue_paginating:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            news_elements = soup.select(ApNewsLocators.NEWS_BLOCK[1])

            for news_element in news_elements:
                # Title
                title = news_element.select_one(ApNewsLocators.NEWS_TITLE[1]).getText()
                
                # Date
                date = news_element.select_one(ApNewsLocators.NEWS_DATE[1])
                if date is None: # Some news don't have date. In that case I skip it.
                    continue
                else:
                    date = date.getText()
                
                # Description
                description = news_element.select_one(ApNewsLocators.NEWS_DESCRIPTION[1])
                if description is not None: # Some news don't have description
                    description = description.getText()
                
                # Picture
                picture = news_element.select_one(ApNewsLocators.NEWS_PICTURE[1])
                if picture is not None: # Some news don't have pictures
                    picture = picture['src']
                    picture = self._download_picture(picture, title)
                
                date = self._convert_date(date)

                if date < cutoff_date:
                    continue_paginating = False
                    break
                
                all_news.append(
                    News(
                        title=title,
                        date=date,
                        description=description,
                        picture=picture
                    )
                )

            ###### REMOVE IN PRD #######
            break

            # Stop paginating if we've reached the last page
            if current_page == total_pages:
                break

            if continue_paginating:
                current_page +=1
                self.click(ApNewsLocators.PAGINATION_NEXT_PAGE)
                new_current_page, _ = self.read_text(ApNewsLocators.PAGINATION_COUNT).split(' of ')
                new_current_page = int(new_current_page)

                if current_page != new_current_page:
                    raise KeyError("Bot tried to paginate but application did not go to the next page")

        return all_news
        
  
class ApNewsLocators():
    SEARCH_BUTTON = (By.XPATH, '//button[@class="SearchOverlay-search-button"]')
    INPUT_SEARCH = (By.XPATH, '//input[@class="SearchOverlay-search-input"]')
    CATEGORY_DROP_DOWN = (By.XPATH, '//div[@class="SearchFilter-heading"]')
    SELECTED_FILTERS_LABEL = (By.XPATH, '//div[@class="SearchResultsModule-filters-selected-title"][text()="Selected Filters"]')
    SORT_BY_SELECT = (By.XPATH, '//span[text()="Sort by"]/../select')
    NEWS_BLOCK = (By.CSS_SELECTOR, 'div.SearchResultsModule-results div.PagePromo')
    NEWS_TITLE = (By.CSS_SELECTOR, 'div.PagePromo-title > a > span')
    NEWS_DATE = (By.CSS_SELECTOR, 'div.PagePromo-date span span')
    NEWS_DESCRIPTION = (By.CSS_SELECTOR, 'div.PagePromo-description a span.PagePromoContentIcons-text')
    NEWS_PICTURE = (By.CSS_SELECTOR, 'div.PagePromo-media a picture img')
    PAGINATION_NEXT_PAGE = (By.XPATH, '//div[@class="Pagination-nextPage"]/a')
    PAGINATION_COUNT = (By.XPATH, '//div[@class="Pagination-pageCounts"]')

    def CATEGORY(category):
        return (By.XPATH, f'//div[@class="CheckboxInput"]/label/span[contains(text(), "{category}")]/../input')

