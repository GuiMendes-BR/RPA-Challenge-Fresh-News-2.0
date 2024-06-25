from robocorp import workitems
from robocorp.tasks import task
from selenium import webdriver
import pandas as pd
import re
from robocorp import log
from config import config

from pages import ApNewsPage

@task
def consumer():
    """Process all the produced input Work Items from the previous step."""

    log.info("Starting Execution!")
    driver = webdriver.Chrome()

    log.info("Opening ApNews...")
    ap_news = ApNewsPage(driver)
    ap_news.open()

    for item in workitems.inputs:
        try:
            log.info(f"Reading payload {item.payload}...")
            keyword = item.payload["keyword"]
            category = item.payload["category"]
            months_to_extract = item.payload["months_to_extract"]

            ap_news.search_keyword(keyword)
            if category != "":
                ap_news.search_category(category)
            ap_news.sort_by('Newest') 
            news = ap_news.scrape_news(months_to_extract)
            table = build_table(news, keyword)
            table.to_excel(f"{config['artifactsDir']}/News for {keyword}.xlsx")


            item.done()
        except AssertionError as err:
            item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
        except KeyError as err:
            item.fail("APPLICATION", code="MISSING_FIELD", message=str(err))
        except NotImplementedError as err:
            item.fail("BUSINESS", code="NOT_IMPLEMENTED", message=str(err))
        except SystemError as err:
            item.fail("APPLICATION", code="SYSTEM_ERROR", message=str(err))
        except Exception as err:
            item.fail("APPLICATION", code="UNKNOWN_ERROR", message=str(err))

def count_keyword(row, column, keyword):
    return row[column].count(keyword)

def contains_money(row, column):
    return bool(
        re.search('\$(\d{1,3}[\,\.]?)+', row[column]) or
        re.search('\d+\sdollars|USD', row[column])
    )
 
def build_table(news, keyword):
    df = pd.DataFrame([one_news.model_dump() for one_news in news])

    # Calculate count fields
    df['count_of_keyword_in_title'] = df.apply(lambda row: count_keyword(row, column='title', keyword=keyword), axis=1)
    df['count_of_keyword_in_description'] = df.apply(lambda row: count_keyword(row, column='description', keyword=keyword), axis=1)
    
    # Calculate money fields
    df['title_contains_money'] =  df.apply(lambda row: contains_money(row, column='title'), axis=1)
    df['description_contains_money'] =  df.apply(lambda row: contains_money(row, column='description'), axis=1)

    return df
