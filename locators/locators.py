class ApNewsLocators():
    # This object has all the selectors for ApNews. I prefer writing XPATHS but Beautiful Soup
    # Accepts only CSS SELECTORS by default :c
    # In bigger projects I like putting the locators in a separate folder but since we have only one page for
    # this project I decided leaving it here for simplicity reasons.
    SEARCH_BUTTON = '//button[@class="SearchOverlay-search-button"]'
    INPUT_SEARCH = '//input[@class="SearchOverlay-search-input"]'
    CATEGORY_DROP_DOWN = '//div[@class="SearchFilter-heading"]'
    SELECTED_FILTERS_LABEL = '//div[@class="SearchResultsModule-filters-selected-title"][text()="Selected Filters"]'
    SORT_BY_SELECT = '//span[text()="Sort by"]/../select'
    PAGINATION_NEXT_PAGE = '//div[@class="Pagination-nextPage"]/a'
    PAGINATION_COUNT = '//div[@class="Pagination-pageCounts"]'

    def CATEGORY(category):
        return f'//div[@class="CheckboxInput"]/label/span[contains(text(), "{category}")]/../input'

class NewsLocators():
    NEWS_BLOCK = 'div.SearchResultsModule-results div.PagePromo'
    NEWS_TITLE = 'div.PagePromo-title > a > span'
    NEWS_DATE = 'div.PagePromo-date span span'
    NEWS_DESCRIPTION = 'div.PagePromo-description a span.PagePromoContentIcons-text'
    NEWS_PICTURE = 'div.PagePromo-media a picture img'