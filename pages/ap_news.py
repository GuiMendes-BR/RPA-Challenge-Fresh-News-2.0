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
from robocorp import log
from config import config

class ApNewsPage(BasePage):

    # Configuração
    URL = config['apNewsUrl']

    def open(self):
        log.info(f"Opening URL {self.URL}...")
        self.driver.get(self.URL)
        self.driver.maximize_window()

    def search_keyword(self, keyword):
        log.info(f"Searching keyword {keyword}...")
        self.click(ApNewsLocators.SEARCH_BUTTON)
        self.type_text(ApNewsLocators.INPUT_SEARCH, keyword)
        self.send_keys(ApNewsLocators.INPUT_SEARCH, Keys.RETURN)

    def search_category(self, category):
        log.info(f"Searching category {category}...")
        assert category != "", "Category cannot be empty"

        self.click(ApNewsLocators.CATEGORY_DROP_DOWN)

        # Capitalize every word in category to match ApNews
        category = category.title()
        if self.exists(ApNewsLocators.CATEGORY(category)):
            log.info("Category found!")
            self.click(ApNewsLocators.CATEGORY(category))
            # Wait for page to load
            self.exists(ApNewsLocators.SELECTED_FILTERS_LABEL)
        else:
            raise AssertionError("Category not found")
        
    def sort_by(self, text):
        log.info(f"Setting sort by as {text}...")
        self.select(ApNewsLocators.SORT_BY_SELECT, text)
        time.sleep(3)

    def _convert_date(self, date):
        # convert date from string to object
        log.info(f"Converting string {date} to datetime...")
        if re.match(r"\d+ hours? ago", date):
            delta = int(re.match(r"\d+", date)[0])
            date = datetime.datetime.today() - datetime.timedelta(hours=delta)
        elif re.match(r"\d+ mins ago", date):
            delta = int(re.match(r"\d+", date)[0])
            date = datetime.datetime.today() - datetime.timedelta(minutes=delta)
        elif date == "Yesterday":
            delta = 1
            date = datetime.datetime.today() - datetime.timedelta(days=delta)
        elif re.match(r"\w+ \d{1,2}, \d{4}", date):
            date = datetime.datetime.strptime(date, "%B %d, %Y")
        elif re.match(r"\w+ \d{1,2}", date):
            date = f"{date}, {datetime.date.today().year}"
            date = datetime.datetime.strptime(date, "%B %d, %Y")
        else:
            raise NotImplementedError(f"Could not convert string to date {date}")
        
        return date

    def _download_picture(self, picture, title):
        log.info(f"Downloading picture {picture}...")
        # Download picture
        image_name = "".join(x for x in title if x.isalnum() or x == " ")
        image_name = f"{image_name}.jpg"

        image_data = requests.get(picture).content
        with open(f'{config['artifactsDir']}/pictures/{image_name}', 'wb') as handler:
            handler.write(image_data)

        log.info(f"Picture saved as {image_name}.")

        return image_name


    def scrape_news(self, months_to_extract):
        if months_to_extract == 0: months_to_extract = 1
        log.info(f"Starting to scrape news up to {months_to_extract} months old...")

        cutoff_date = datetime.datetime.now() - relativedelta(months=months_to_extract)
        log.info(f"Setting cutoff date as {cutoff_date}")

        all_news = []

        # Variables related to the pagination feature
        continue_paginating = True
        current_page, total_pages = self.read_text(ApNewsLocators.PAGINATION_COUNT).split(' of ')
        current_page, total_pages = int(current_page), int(total_pages)


        while continue_paginating:
            # For each page we extract the page html, feed it into Beautiful Soup
            # And finally select the list of news in current page 
            log.info(f"Processing page {current_page}...")
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            news_elements = soup.select(ApNewsLocators.NEWS_BLOCK[1])

            # For each news we need to extract Title, Date, Description and Picture
            for news_element in news_elements:
                # Title
                title = news_element.select_one(ApNewsLocators.NEWS_TITLE[1]).getText()
                log.info(f"Processing news with title {title}...")
                
                # Date
                date = news_element.select_one(ApNewsLocators.NEWS_DATE[1])
                if date is None:
                    # Some news don't have date. In that case I skip it because the age of the news is relevant 
                    # for this process.
                    continue
                else:
                    date = date.getText()
                date = self._convert_date(date)
                
                # Description
                description = news_element.select_one(ApNewsLocators.NEWS_DESCRIPTION[1])
                if description is not None: # Some news don't have description
                    description = description.getText()
                else:
                    description = ""
                
                
                # Picture
                picture = news_element.select_one(ApNewsLocators.NEWS_PICTURE[1])
                if picture is not None: # Some news don't have pictures
                    picture = picture['src']
                    picture = self._download_picture(picture, title)
                
                # We're only interested in news up to a cutoff date.
                # Since we'are ordering the list from newest news to oldest, we assume that
                # If we've reached the cutoff date, there's nothing more that we're interested into
                if date < cutoff_date:
                    log.info("We've reached the cutoff date, stop paginating!")
                    continue_paginating = False
                    break


                # We finally append a new news to the list
                all_news.append(
                    News(
                        title=title,
                        date=date,
                        description=description,
                        picture=picture
                    )
                )


            # Stop paginating if we've reached the last page
            if current_page == total_pages:
                log.info("We've reached the last page, stop paginating!")
                break

            # If we need to continue paginating, we click on next page and check if Ap News loaded the new list
            # successfully.
            if continue_paginating:
                log.info("Going to next page...")
                current_page +=1
                self.click(ApNewsLocators.PAGINATION_NEXT_PAGE)
                current_page_in_ap_news, _ = self.read_text(ApNewsLocators.PAGINATION_COUNT).split(' of ')
                current_page_in_ap_news = int(current_page_in_ap_news)

                if current_page != current_page_in_ap_news:
                    raise SystemError("Bot tried to paginate but application did not go to the next page")

        return all_news
        

class ApNewsLocators():
    # This object has all the selectors for ApNews. I prefer writing XPATHS but Beautiful Soup
    # Accepts only CSS SELECTORS by default :c
    # In bigger projects I like putting the locators in a separate folder but since we have only one page for
    # this project I decided leaving it here for simplicity reasons.
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


class News(BaseModel):
    title: str  
    date: datetime.datetime # December 14, 2023
    description: str
    picture: str | None