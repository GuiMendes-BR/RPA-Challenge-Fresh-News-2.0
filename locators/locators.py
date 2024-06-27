from selenium.webdriver.common.by import By

class ApNewsLocators():
    """Locators for the search page of Ap News"""
    SEARCH_BUTTON = (By.XPATH, '//button[@class="SearchOverlay-search-button"]')
    INPUT_SEARCH = (By.XPATH, '//input[@class="SearchOverlay-search-input"]')
    CATEGORY_DROP_DOWN = (By.XPATH, '//div[@class="SearchFilter-heading"]')
    SELECTED_FILTERS_LABEL = (By.XPATH, '//div[@class="SearchResultsModule-filters-selected-title"][text()="Selected Filters"]')
    SORT_BY_SELECT = (By.XPATH, '//span[text()="Sort by"]/../select')
    PAGINATION_NEXT_PAGE = (By.XPATH, '//div[@class="Pagination-nextPage"]/a')
    PAGINATION_COUNT = (By.XPATH, '//div[@class="Pagination-pageCounts"]')
    NO_RESULTS_FOUND = (By.XPATH, '//div[@class="SearchResultsModule-noResults"][contains(text(), "There are no results that match")]')

    def CATEGORY(category):
        return (By.XPATH, f'//div[@class="CheckboxInput"]/label/span[contains(text(), "{category}")]/../input')

class NewsLocators():
    """Locators for each individual news block."""
    NEWS_BLOCK = (By.CSS_SELECTOR, 'div.SearchResultsModule-results div.PagePromo')
    NEWS_TITLE = (By.CSS_SELECTOR, 'div.PagePromo-title > a > span')
    NEWS_DATE = (By.CSS_SELECTOR, 'div.PagePromo-date span span')
    NEWS_DESCRIPTION = (By.CSS_SELECTOR, 'div.PagePromo-description a span.PagePromoContentIcons-text')
    NEWS_PICTURE = (By.CSS_SELECTOR, 'div.PagePromo-media a picture img')